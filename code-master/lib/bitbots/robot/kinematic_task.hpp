#ifndef _KINEMATIC_ROBOT_TASK_HPP__
#define _KINEMATIC_ROBOT_TASK_HPP__

#include <set>
#include <Eigen/Core>

#include "kinematic_robot.hpp"
#include "kinematic_joint.hpp"
#include "jointids.hpp"

namespace Robot {
namespace Kinematics {

/**
 * \brief This is a wrapper to create KinematicTasks for the robot implementation
 *
 * This KinematicTask creates kinematic chain and performs them.
 * There are various ways, the used chains can be created or used. Most of all, the chains are
 * build dynamically and there are some options, you can apply on the chain members.
 */
class KinematicTask {
public:

    /**
     * A simple small wrapper to hold and export the chain.
     */
    class ChainHolder : public std::pair<KRobot::Chain*, bool> {
    public:
        ChainHolder()
        :pair(nullptr, false)
        {}

        ChainHolder(ChainHolder& other)
        :pair(other.first, other.second)
        {
            other.first = nullptr;
            other.second = false;
        }

        ChainHolder(ChainHolder&& other)
        :pair(other.first, other.second)
        {
            other.first = nullptr;
            other.second = false;
        }

        ChainHolder& operator=(ChainHolder& other) {
            this->~ChainHolder();
            first = other.first;
            second = other.second;
            other.first = nullptr;
            other.second = false;
            return *this;
        }

        ChainHolder& operator=(ChainHolder&& other) {
            this->~ChainHolder();
            first = other.first;
            second = other.second;
            other.first = nullptr;
            other.second = false;
            return *this;
        }

        ChainHolder(KRobot::Chain& chain, const bool new_chain)
        :pair(&chain, new_chain)
        {}

        ~ChainHolder() {
            if(second)
                delete first;
        }

        size_t size() {
            return first? first->size():0;
        }

        KRobot::Chain& operator*() {
            return *first;
        }

        /**
         * This operator enables some nice syntax, as this chain holder is primary holding a Chain pointer.
         * Using this operator, there are expressions like the following are possible:
         * holder->size(), for calling the size method of the Chain.
         * This avoids the confusing indirection of the get method or the bracket horror using the * operator.
         */
        KRobot::Chain* operator->() {
            return first;
        }

        KRobot::Chain& get() {
            return *first;
        }

        KRobot::Chain::value_type& operator[](const unsigned idx) {
            return (*first)[idx];
        }

        KJoint& get_joint(unsigned idx) {
            return *first->at(idx);
        }

    };

    enum DisableType{none, direct_chain, inverse_chain};
    typedef std::set<unsigned> TaskIdSet;
    typedef std::vector<TaskIdSet> TaskIdContainer;

private:
    const KRobot& m_robot;

    template<typename TaskIdMarker>
    inline void perform_intern(JointIds from, JointIds to, const KRobot::MultipleTargetType& target_position, const KRobot::MultipleAxisType axis,
                        const KRobot::MultipleErrorType error, const TaskIdMarker& idset_for_tasks=TaskIdMarker(), const int max_it=100,
                        const std::set<int>& ignore_joints=std::set<int>(),const  DisableType disable_chain=DisableType::none) const;
    inline
    void perform_intern(ChainHolder& chain, const KRobot::MultipleTargetType& target_position, const KRobot::MultipleAxisType axis,
                        const KRobot::MultipleErrorType error, const int max_it=100) const;

    template<typename TaskIdMarker>
    inline ChainHolder create_chain_intern(JointIds from, JointIds to, const KRobot::MultipleAxisType axis, const TaskIdMarker& idset_for_tasks=TaskIdMarker(),
                                           const std::set<int>& ignore_joints=std::set<int>(), const DisableType disable_chain=DisableType::none) const;

public:

    //! \defgroup public kinematic interfaces

    KinematicTask(const KRobot& robot)
    :m_robot(robot) {}

    /**
     * This method performs a kinematic task for manipulating the robots centre of gravity
     * \param chain_id: The chain id used as direct basis of the task. All the other chain will be inverse chains.
     * \param target_position: The position, the centre of gravity should finally reach
     * \param ignore_joints: A set joint jointids, that will be set inactive
     * \param error: The maximum error value to fulfil this task
     * \param max_it: maximum number of iterations
     * \param disable_chain: This is an optional parameter to specify, whether a given part of the chain should be considered as inactive
     */
    void perform_centre_of_gravity_task(ChainIds chain_id, const Eigen::Vector3d& target_position, const std::set<int>& ignore_joints, const double error=1e-1, const int max_it=100, const DisableType disable_chain=DisableType::none) const;
    void perform_centre_of_gravity_task(ChainHolder& holder, const Eigen::Vector3d& target_position, const double error=1e-1, const int max_it=100) const;
    ChainHolder create_centre_of_gravity_chain(ChainIds chain_id, const std::set<int>& ignore_joints, const DisableType disable_chain=DisableType::none) const;

    /**
     * This method performs a kinematic task:
     * \param from: The joint, meaning the start of the dynamic Chain
     * \param to: The joint, meaning the end of the dynamic Chain
     * \param target_position: The position, the end(@param to) should have in relation to from(@param from), can be multiple target, when specifying multiple axis
     * \param axis: The used axis for the KinematicTask
     * \param error: The maximum allowed difference vector between the actual and the given robot's relative joint position. can be multiple error(see target_position)
     * \param idset_for_first_task a set containing the jointids, that will be enabled for first, and disabled for the second part of the KinematicTask
     * \param max_it: The maximum number of iterations for the kinematic task, that will be performed by the iterative algorithm
     * \param ignore_joints a set containing the jointids, that will be ignored for the KinematicTask
     * \param disable_chain: This is an optional parameter to specify, whether a given part of the chain should be considered as inactive
     */
    void perform_task(JointIds from, JointIds to, const KRobot::MultipleTargetType& target_position, const KRobot::MultipleAxisType axis, const KRobot::MultipleErrorType error,
                      const TaskIdSet& idset_for_first_task=TaskIdSet(), const int max_it=100, const std::set<int>& ignore_joints=std::set<int>(), const DisableType disable_chain=DisableType::none) const;
    //! \copydoc KinematicTask::perform_task(JointIds,JointIds,const KRobot::MultipleTargetType&,const KRobot::MultipleAxisType,const KRobot::MultipleErrorType,const TaskIdSet&,int,const std::set<int>&,DisableType)
    void perform_task(JointIds from, JointIds to, const Eigen::Vector3d& target_position, KJoint::AxisType axis=KJoint::AxisType::Position, const double error=1e-1, const int max_it=100,
                                        const std::set<int>& ignore_joints=std::set<int>(), const DisableType disable_chain=DisableType::none) const;

    /**
     * The other way to perform the KinematicTask
     * \param chain: The wrapped chain, created by the create_chaim method
     * \param axis: The used axis for the KinematicTask
     * \param target_position: The position, the end(@param to) should have in relation to from(@param from), can be multiple target, when specifying multiple axis
     * \param error: The maximum allowed difference vector between the actual and the given robot's relative joint position. can be multiple error(see target_position)
     * \param max_it: The maximum number of iterations for the kinematic task, that will be performed by the iterative algorithm
     */
    void perform_task(ChainHolder& chain, const KRobot::MultipleTargetType& target_position, const KRobot::MultipleAxisType axis, const KRobot::MultipleErrorType error, int max_it=100) const;
    //! \copydoc KinematicTask::perform_task(ChainHolder&,const KRobot::MultipleTargetType&,const KRobot::MultipleAxisType,const KRobot::MultipleErrorType,int)
    void perform_task(ChainHolder& chain, const Eigen::Vector3d& target_position, KJoint::AxisType axis=KJoint::AxisType::Position, const double error=1e-1, const int max_it=100) const;

    /**
     * This method creates a chain, that can be reused to perform multiple KinematicTasks without recreating the same chain a dozen times
     * \param from: The joint, meaning the start of the dynamic Chain
     * \param to: The joint, meaning the end of the dynamic Chain
     * \param axis: The used axis for the KinematicTask
     * \param idset_for_first_task a set containing the jointids, that will be enabled for first, and disabled for the second part of the KinematicTask
     * \param max_it: The maximum number of iterations for the kinematic task, that will be performed by the iterative algorithm
     * \param ignore_joints a set containing the jointids, that will be ignored for the KinematicTask
     * \param disable_chain: This is an optional parameter to specify, whether a given part of the chain should be considered as inactive
     */
    ChainHolder create_chain(JointIds from, JointIds to, const KRobot::MultipleAxisType axis, const TaskIdSet& idset_for_first_task=TaskIdSet(),
                             const std::set<int>& ignore_joints=std::set<int>(), DisableType disable_chain=DisableType::none) const;
    //! \copydoc KinematicTask::create_chain(JointIds,JointIds,const KRobot::MultipleAxisType,const TaskIdSet&,const std::set<int>&,DisableType)
    inline ChainHolder create_chain(JointIds from, JointIds to, const KJoint::AxisType axis, const std::set<int>& ignore_joints=std::set<int>(), const DisableType disable_chain=DisableType::none) const {
        return create_chain(from, to, KRobot::SingleAxisTypeMat((KRobot::SingleAxisTypeMat()<<axis).finished()), TaskIdSet(), ignore_joints, disable_chain);
    }
    /**
     * This method creates a chain, that can be reused to perform multiple KinematicTasks without recreating the same chain a dozen times
     * \param from: The joint, meaning the start of the dynamic Chain
     * \param to: The joint, meaning the end of the dynamic Chain
     * \param axis: The used axis for the KinematicTask
     * \param idset_tasks a vector containing sets storing the jointids, that will be enabled for n'th, and disabled for the other parts of the KinematicTask
     * \param max_it: The maximum number of iterations for the kinematic task, that will be performed by the iterative algorithm
     * \param ignore_joints a set containing the jointids, that will be ignored for the KinematicTask
     * \param disable_chain: This is an optional parameter to specify, whether a given part of the chain should be considered as inactive
     */
    ChainHolder create_chain(JointIds from, JointIds to, const KRobot::MultipleAxisType axis, const TaskIdContainer& idset_for_tasks,
                             const std::set<int>& ignore_joints=std::set<int>(), const DisableType disable_chain=DisableType::none) const;

    static void assure_chain_correctness(KRobot::Chain& chain);

    void update_robot_chain(ChainHolder& chain, const unsigned update_flags/*=KRobot::UpdateChainFlags::NOP*/);
    void update_robot_chain(KRobot::Chain& chain, const unsigned update_flags/*=KRobot::UpdateChainFlags::NOP*/);
    static void update_robot_chain(KRobot& robot, ChainHolder& chain, const unsigned update_flags/*=KRobot::UpdateChainFlags::NOP*/);
    static void update_robot_chain(KRobot& robot, KRobot::Chain& chain, const unsigned update_flags/*=KRobot::UpdateChainFlags::NOP*/);

};

} } //namespace

#endif //_KINEMATIC_ROBOT_TASK_HPP__
