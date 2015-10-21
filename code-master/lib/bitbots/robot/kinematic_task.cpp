#include <set>
#include <Eigen/Core>
#include <boost/foreach.hpp>

#include "kinematic_task.hpp"
#include "kinematic_joint.hpp"
#include "chain_member.hpp"
#include "jointids.hpp"
#include "../debug/debugmacro.h"

using namespace Robot;
using namespace Kinematics;
using namespace std;
using namespace Eigen;

static inline void ignore_id_set(KRobot::Chain* chain, const KinematicTask::TaskIdSet& idset_for_first_task, const KRobot::MultipleAxisType& axis) {
    for(KJointChainMember& mem: *chain) {
        if(idset_for_first_task.find((*mem).get_id()) != idset_for_first_task.end()) {
            // disable joints, choosen for first task in the second task part
            mem.set_ignorance_for_axis(axis(1));
        } else {
            mem.set_ignorance_for_axis(axis(0));
        }
    }
}

/**
 * This method is not optimal for performance issues, but it should be called very often.
 * This tries to set most of the joints inactive for a given axis, when it's not supposed to
 * used for this subtask
 */
static inline void ignore_id_set(KRobot::Chain* chain, const KinematicTask::TaskIdContainer& idset_for_tasks, const KRobot::MultipleAxisType& axis) {
    assert(idset_for_tasks.size() == (unsigned)axis.rows());
    for(unsigned i = 0; i < idset_for_tasks.size(); ++i) {
        const KinematicTask::TaskIdSet& idset_for_nth_task = idset_for_tasks[i];
        for(KJointChainMember& mem: *chain) {
            if(idset_for_nth_task.find((*mem).get_id()) != idset_for_nth_task.end()) {
                // disable joints, choosen for first task in the second task part
                //mem.set_ignorance_for_axis(axis(1));
            } else {
                //mem.set_ignorance_for_axis(axis(0));
                mem.set_ignorance_for_axis(axis(i));
            }
        }
    }
}

template<typename TaskIdMarker>
static inline KRobot::Chain* handle_ignorance_sets(KRobot::Chain* chain, bool& new_chain, const TaskIdMarker& idset_for_tasks, const std::set<int>& ignore_joints, const KRobot::MultipleAxisType& axis) {
    // Handle the ignore joint options, first the use of chain
    if(idset_for_tasks.size()) {
        assert(axis.rows() > 1);
        // When we are using an original chain, we need to copy it, because we modify options
        if(!new_chain) {
            chain = new KRobot::Chain(chain->begin(), chain->end());
            new_chain = true;
        }
        ignore_id_set(chain, idset_for_tasks, axis);
    }
    for(KJointChainMember& mem: *chain) {
        if(ignore_joints.find((*mem).get_id()) != ignore_joints.end()) {
            mem.set_inactive();
        }
    }
    return chain;
}

template<typename TaskIdMarker>
inline KinematicTask::ChainHolder KinematicTask::create_chain_intern(JointIds from, JointIds to, const KRobot::MultipleAxisType axis, const TaskIdMarker& idset_for_tasks,
                                                                     const std::set<int>& ignore_joints, KinematicTask::DisableType disable_chain) const {
    KRobot::Chain* chain = nullptr;
    const KRobot::JointChainMappingType& joint_chain_mapping = m_robot.get_joint_chain_mapping();
    bool new_chain = true;
    if(from == JointIds::Root) {
        //standard robot's chain
        chain = & const_cast<KRobot::Chain&>(m_robot.get_chain_by_id(joint_chain_mapping[to].first));
        if(chain->back()->get_id() != to) {
            chain = new KRobot::Chain((const KRobot::Chain)*chain);
            while(chain->back()->get_id() != to) {
                chain->pop_back();
            }
        } else {
            new_chain = false;
        }
    } else if (joint_chain_mapping[from].second & joint_chain_mapping[to].second) {
        //Chain where from and to are in on chain
        uint16_t chain_bit = joint_chain_mapping[from].second & joint_chain_mapping[to].second;
        const KRobot::Chain& org = m_robot.get_chain_by_bit(chain_bit);
        chain = new KRobot::Chain();
        chain->reserve(org.size());
        int idx = 0;
        bool inverse = false;
        while(org[idx]->get_id() != from && org[idx]->get_id() != to) {
            ++idx;
        }
        if(org[idx]->get_id() == to) {
            inverse = true;
            while(org[idx]->get_id() != from)
                ++idx;
            chain->push_back(org[idx]);
            --idx;
            while(org[idx]->get_id() != to ) {
                chain->push_back(org[idx]);
                --idx;
            }
            chain->push_back(org[idx]);
        } else {
            chain->push_back(org[idx]);
            ++idx;
            while(org[idx]->get_id() != to) {
                chain->push_back(org[idx]);
                ++idx;
            }
            chain->push_back(org[idx]);
        }
        KJointChainMember::OptionType option = KJointChainMember::SingleOptions::is_inverse;

        if(disable_chain == KinematicTask::inverse_chain) {
            option |= KJointChainMember::SingleOptions::is_inactive;
        }
        if(inverse) {
            for(KJointChainMember& mem : *chain) {
                mem.set_option(option);
            }
        }
    } else {
        //Dynamic chain with from and to in different chains
        int inv_chain_chain_id = joint_chain_mapping[from].first, org_chain_chain_id = joint_chain_mapping[to].first;
        const KRobot::Chain& inv_chain = m_robot.get_chain_by_id(inv_chain_chain_id),
        org_chain = m_robot.get_chain_by_id(org_chain_chain_id);
        chain = new KRobot::Chain();
        chain->reserve(inv_chain.size() + org_chain.size() - 1);
        bool started = false;
        KJointChainMember::OptionType option = KJointChainMember::SingleOptions::is_inverse;
        if(disable_chain == KinematicTask::inverse_chain) {
            option |= KJointChainMember::SingleOptions::is_inactive;
        }
        for(unsigned i = inv_chain.size() - 1; i != (unsigned) -1; --i) {
            const KJointChainMember& mem = inv_chain[i];
            if(started || mem->get_id() == from) {
                started = true;
                chain->push_back(mem);
                chain->back().set_option(option);
                if(mem.evaluate_option(KJointChainMember::SingleOptions::is_in_multiple_chains) && i < inv_chain.size() - 1) {
                    chain->back()->create_inverse_transform_with_follower(*(inv_chain[i + 1]));
                }
            }
        }
        for(unsigned i = 1; i < org_chain.size(); ++i) {
            chain->push_back(org_chain[i]);
            if(disable_chain == DisableType::direct_chain)
                chain->back().set_inactive();
            if((*chain)[i]->get_id() == to) {
                break;
            }
        }
        //check for joints that are in both chains
        KRobot::ChainIdType inv_chain_chain_bit = 1 << inv_chain_chain_id;
        KRobot::ChainIdType org_chain_chain_bit = 1 << org_chain_chain_id;
        KRobot::ChainIdType chain_bits = inv_chain_chain_bit | org_chain_chain_bit;
        for(KJointChainMember& mem: *chain) {
            if((joint_chain_mapping[mem->get_id()].second & chain_bits) == chain_bits) {
                mem.set_option(KJointChainMember::SingleOptions::is_duplicate);
            }
        }
    }
    chain = handle_ignorance_sets(chain, new_chain, idset_for_tasks, ignore_joints, axis);
    return KinematicTask::ChainHolder(*chain, new_chain);
}

KinematicTask::ChainHolder KinematicTask::create_chain(JointIds from, JointIds to, const KRobot::MultipleAxisType axis, const TaskIdSet& idset_for_first_task,
                                                       const set< int >& ignore_joints, KinematicTask::DisableType disable_chain) const {
    return create_chain_intern(from, to, axis, idset_for_first_task, ignore_joints, disable_chain);
}

KinematicTask::ChainHolder KinematicTask::create_chain(JointIds from, JointIds to, const KRobot::MultipleAxisType axis, const KinematicTask::TaskIdContainer& idset_for_tasks, const set<int>& ignore_joints, const KinematicTask::DisableType disable_chain) const {
    return create_chain_intern(from, to, axis, idset_for_tasks, ignore_joints, disable_chain);
}


template<typename TaskIdMarker>
inline void KinematicTask::perform_intern(JointIds from, JointIds to, const KRobot::MultipleTargetType& target_position, const KRobot::MultipleAxisType axis,
                                          const KRobot::MultipleErrorType error, const TaskIdMarker& idset_for_tasks, const int max_it,
                                          const set<int>& ignore_joints, const KinematicTask::DisableType disable_chain) const {
    ChainHolder chain = create_chain_intern(from, to, axis, idset_for_tasks, ignore_joints, disable_chain);
    const_cast<KRobot&>(m_robot).update_chain(*chain, KJoint::AngleCheck::check, KRobot::UpdateChainFlags::reset_start_chain_matrix);
    const_cast<KRobot&>(m_robot).inverse_chain(*chain, target_position, error, max_it, axis);
}

inline
void KinematicTask::perform_intern(KinematicTask::ChainHolder& chain, const KRobot::MultipleTargetType& target_position, const KRobot::MultipleAxisType axis,
                                   const KRobot::MultipleErrorType error, const int max_it) const {
    const_cast<KRobot&>(m_robot).update_chain(*chain, KJoint::AngleCheck::check, KRobot::UpdateChainFlags::reset_start_chain_matrix);
    const_cast<KRobot&>(m_robot).inverse_chain(*chain, target_position, error, max_it, axis);
}

void KinematicTask::perform_task(JointIds from, JointIds to, const Vector3d& target_position, KJoint::AxisType axis, const double error, const int max_it,
                                 const std::set<int>& ignore_joints, KinematicTask::DisableType disable_chain) const {
    perform_intern(from, to, target_position, KRobot::SingleAxisTypeMat((KRobot::SingleAxisTypeMat()<<axis).finished()), Vector1d(error), TaskIdSet(), max_it, ignore_joints, disable_chain);
}

void KinematicTask::perform_task(JointIds from, JointIds to, const KRobot::MultipleTargetType& target_position, const KRobot::MultipleAxisType axis,
                                 const KRobot::MultipleErrorType error, const TaskIdSet& idset_for_first_task, const int max_it, const set<int>& ignore_joints, const KinematicTask::DisableType disable_chain) const
{
    perform_intern(from, to, target_position, axis, error, idset_for_first_task, max_it, ignore_joints, disable_chain);
}

void KinematicTask::perform_task(KinematicTask::ChainHolder& chain, const Vector3d& target_position, KJoint::AxisType axis, const double error, const int max_it) const
{
    perform_intern(chain, target_position, KRobot::SingleAxisTypeMat((KRobot::SingleAxisTypeMat()<<axis).finished()), (Vector1d()<<error).finished(), max_it);
}

void KinematicTask::perform_task(KinematicTask::ChainHolder& chain, const KRobot::MultipleTargetType& target_position, const KRobot::MultipleAxisType axis,
                                 const KRobot::MultipleErrorType error, int max_it) const
{
    perform_intern(chain, target_position, axis, error, max_it);
}

KinematicTask::ChainHolder KinematicTask::create_centre_of_gravity_chain (ChainIds chain_id, const set<int>& ignore_joints, const KinematicTask::DisableType disable_chain ) const {
    KRobot::Chain* chain = new KRobot::Chain();
    const KRobot::Chain& ref_chain = m_robot.get_chain_by_id(chain_id);
    for(unsigned i = ref_chain.size() - 1; i < ref_chain.size(); --i) {
        KJointChainMember mem = ref_chain[i];
        mem.set_option(KJointChainMember::SingleOptions::is_inverse);
        if(i != ref_chain.size() - 1 && mem.evaluate_option(KJointChainMember::SingleOptions::is_in_multiple_chains)) {
            mem->create_inverse_transform_with_follower(*ref_chain[i + 1]);
        }
        if(disable_chain == DisableType::inverse_chain || ignore_joints.find(mem->get_id()) != ignore_joints.end()) {
            mem.set_inactive();
        }
        chain->push_back(mem);
    }
    for(unsigned i = 0; i < m_robot.get_chains().size(); ++i) {
        if(i == chain_id)
            continue;
        const KRobot::Chain& cur_chain = m_robot.get_chain_by_id(i);
        KJointChainMember duplicat_root = cur_chain[0];
        duplicat_root.set_option(KJointChainMember::SingleOptions::is_duplicate | KJointChainMember::SingleOptions::is_restart);
        chain->push_back(duplicat_root);
        for(unsigned j = 1; j < cur_chain.size(); ++j) {
            KJointChainMember cur_mem = cur_chain[j];
            if(disable_chain == DisableType::direct_chain || ignore_joints.find(cur_mem->get_id()) != ignore_joints.end()) {
                cur_mem.set_inactive();
            }
            chain->push_back(cur_mem);
        }
    }
    return ChainHolder(*chain, true);
}

void KinematicTask::perform_centre_of_gravity_task (KinematicTask::ChainHolder& chain, const Vector3d& target_position, const double error, const int max_it) const {
    const_cast<KRobot&>(m_robot).inverse_local_cog_chain(*chain, target_position, Vector3i(1, 0, 1), error, max_it);
}

void KinematicTask::perform_centre_of_gravity_task(ChainIds chain_id, const Vector3d& target_position, const set<int>& ignore_joints, const double error, const int max_it, const DisableType disable_chain) const {
    ChainHolder chain = create_centre_of_gravity_chain(chain_id, ignore_joints, disable_chain);

    const_cast<KRobot&>(m_robot).inverse_local_cog_chain(*chain, target_position, Vector3i(0, 0, 1), error, max_it);
}

void KinematicTask::assure_chain_correctness (KRobot::Chain& chain) {
    for(unsigned i = 0; i < chain.size(); ++i) {
        KJointChainMember& mem = chain[i];
        if(i && mem.evaluate_option(KJointChainMember::SingleOptions::is_in_multiple_chains) && mem.evaluate_option(KJointChainMember::SingleOptions::is_inverse)) {
            mem->create_inverse_transform_with_follower(*chain[i - 1]);
        }
    }
}


void KinematicTask::update_robot_chain(KRobot::Chain& chain, const unsigned update_flags) {
    assure_chain_correctness(chain);
    const_cast<KRobot&>(m_robot).update_chain(chain, KJoint::AngleCheck::check, update_flags);
}
void KinematicTask::update_robot_chain(ChainHolder& chain, const unsigned update_flags) {
    assure_chain_correctness(*chain);
    const_cast<KRobot&>(m_robot).update_chain(*chain, KJoint::AngleCheck::check, update_flags);
}
void KinematicTask::update_robot_chain(KRobot& robot, KRobot::Chain& chain, const unsigned update_flags) {
    assure_chain_correctness(chain);
    robot.update_chain(chain, KJoint::AngleCheck::check, update_flags);
}
void KinematicTask::update_robot_chain(KRobot& robot,ChainHolder& chain, const unsigned update_flags) {
    assure_chain_correctness(*chain);
    robot.update_chain(*chain, KJoint::AngleCheck::check, update_flags);
}

