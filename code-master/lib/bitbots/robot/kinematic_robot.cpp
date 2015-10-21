#include <limits>
#include <vector>
#include <map>
#include <string>
#include <assert.h>
#include <Eigen/Core>
#include <Eigen/Geometry>
#include <Eigen/LU>

#include "kinematic_robot.hpp"
#include "inverse_computation.hpp"
#include "pose.hpp"
#include "jointids.hpp"

#define ROBOT_IMPL_FOR_JOINT_USAGE
#include "kinematic_joint-impl.hpp"
#undef ROBOT_IMPL_FOR_JOINT_USAGE

using namespace Robot;
using namespace Kinematics;
using namespace Eigen;
using namespace std;
namespace Kin = ::Robot::Kinematics;

typedef unsigned int uint;
typedef const uint cuint;

typedef KJoint::AngleCheck AngleCheck;

static const Matrix4d id4= Matrix4d::Identity();
static const double max_angle_diff_to_skip = 20 * degree_to_rad;
static const double min_angle_diff_to_skip = -max_angle_diff_to_skip;

//0.15 rad is an angle of round about 9 degree
static const double max_angle_disturb = 0.15;
static uniform_real_distribution<double> dist(-max_angle_disturb, max_angle_disturb);
static random_device rd;
static mt19937 gen(rd());

static BITBOTS_INLINE void fill_random_angles(KRobot::AngleMatrixType& angleOff, cuint num) {
    angleOff = KRobot::AngleMatrixType(num, 1);
    for(uint i = 0; i < num; ++i) {
        angleOff(i) = dist(gen);
    }
}

enum ChainManipulation{add=true, minus=false};

template<bool addition>
BITBOTS_INLINE void KRobot::manipulate_chain_angles(AngleMatrixType& angleOff, Chain& chain, const unsigned single_jacobi_cols) {
    fill_random_angles(angleOff, single_jacobi_cols);
    for(uint i = 0, i_pl_1 = 1; i < (unsigned)angleOff.rows(); ++i, ++i_pl_1) {
        if(chain[i_pl_1].evaluate_option(KJointChainMember::Options::need_to_ignore)) {
            angleOff(i) = 0;
            continue;
        }
        if(addition) {
            chain[i_pl_1]->m_angle += angleOff(i);
        } else {
            chain[i_pl_1]->m_angle -= angleOff(i);
        }
    }
    //Allow "illegal" roboter positions to make the calculation more robust
    update_chain<AngleCheck::unchecked, UpdateChainFlags::NOP, true>(chain);
}

inline
static uint16_t get_chain_bit(cuint idx) {
    return 1 << idx;
}

template<typename T>
inline static unsigned num_set_bits2(const T bitvector) {
    T n_bits = sizeof(T) * (T)CHAR_BIT - (T) 1, bits = bitvector & (T)1;
    while(n_bits) {
        if(bitvector & (T)1<<n_bits)
            ++bits;
        --n_bits;
    }
    return bits;
}

template<typename T>
inline static unsigned num_set_bits(T bitvector) {
    static_assert(sizeof(T) * CHAR_BIT <= 64, "This version of the bit counting algorithm is not capable to be guaranteed right with Types counting more than 64 bits");
    const static uint64_t masks[6] = {0x5555555555555555,
        0x3333333333333333,
        0x0F0F0F0F0F0F0F0F,
        0x00FF00FF00FF00FF,
        0x0000FFFF0000FFFF,
        0x00000000FFFFFFFF};
        unsigned idx = 0, shift = 1;
        while(true) {
            // Every iteration counts the number of bits in a given block of increasing size
            // The masks represent this size.
            bitvector = (bitvector & ((T)masks[idx])) + ((bitvector >> shift) & ((T)masks[idx]));
            // This conditions is true, when all the bits are in the "number section"
            if(! (bitvector >> shift))
                return bitvector;
            ++idx;
            shift = shift << 1;
            L_DEBUG(if(idx > sizeof(masks))throw runtime_error("Something strange happened on counting bits"));
        }
}

void KRobot::init_chains(const ChainsTemplate& chains_template, const int max_id) {
    if(chains_template.size() == 0)
        return;
    m_joint_chain_mapping.resize(m_joints.size(), JointMapType(-1, 0));
    int chain_id = 0;
    m_joint_chain_mapping[0].first = 0;
    for(const vector<int>& chain_template: chains_template) {
        uint16_t chain_bit = get_chain_bit(chain_id);
        m_chains.push_back(Chain());
        Chain& chain = m_chains.back();
        //insert first joint to every chain
        chain.push_back(KJointChainMember(m_joints[0]));
        m_joint_chain_mapping[0].second |= chain_bit;
        for(int joint_id: chain_template) {
            KJointChainMember mem(m_joints[joint_id]);
            mem.set_active_with_id(max_id);
            chain.push_back(mem);
            if(m_joint_chain_mapping[joint_id].first == -1) {
                m_joint_chain_mapping[joint_id].first = chain_id;
            }
            m_joint_chain_mapping[joint_id].second |= chain_bit;
        }
        ++ chain_id;
    }
    chain_id = 0;
    for(Chain& chain: m_chains) {
        //Now finish initialising the joints and set their inverse transform, the transform of the last chain member is correct by default (Identity)
        // The root joint would need several inverse transforms, so it won't be set by default
        for(int i = chain.size() - 2; i >= 0; --i) {
            KJointChainMember& mem = chain[i];
            mem->create_inverse_transform_with_follower(*chain[i + 1]);
            bool missing_joits = false;
            if((unsigned)mem->get_id() >= m_joint_chain_mapping.size()) {
                missing_joits = true;
                L_DEBUG(std::cerr<<mem->get_id()<<std::endl);
            } else {
                if(num_set_bits(((uint16_t)m_joint_chain_mapping[mem->get_id()].second)) > 1) {
                    mem.set_option(KJointChainMember::SingleOptions::is_in_multiple_chains);
                }
            }
            if(missing_joits)
                std::cerr<<"The Robots joint chain mapping is filled incomplete"<<std::endl;
        }
        ++chain_id;
    }
}

void KRobot::create_chain_template_and_init_chains(const KRobot& other) {
    ChainsTemplate chains;
    chains.reserve(other.m_chains.size());
    for(uint i = 0; i < other.m_chains.size(); ++i) {
        chains.push_back(vector<int>());
        vector<int>& current = chains[i];
        for(uint j = 1; j < other.m_chains[i].size(); ++j) {
            const KJoint& joint = *other.m_chains[i][j];
            current.push_back(&joint - ((const KJoint*)(&other.m_joints[0])) );
        }
    }
    init_chains(chains, other.m_max_motor_id);
}

template<AngleCheck checked, unsigned update_flags, bool skip_static_start>
BITBOTS_INLINE void KRobot::update_chain(Chain& chain) {
    L_DEBUG(std::cout<<(update_flags?"Update flags ":"")<< (update_flags & reset_start_chain_matrix? "Reset Start ":"")
    <<(update_flags & update_masses? "Update Masses":"")<<(update_flags?"\n":""));
    // I think, first I need the positional update for every joint. Then I can perform the mass updates
    if(update_flags & reset_start_chain_matrix)
        chain[0]->m_chain_matrix = id4;
    unsigned i = 1;
    while(skip_static_start && chain[i].evaluate_option(KJointChainMember::Options::need_to_ignore)) ++i;
    const Affine3d* prev = &chain[i - 1]->m_chain_matrix;
    for(; i < chain.size(); ++i) {
        KJointChainMember& mem = chain[i];
        KJoint& joint = *mem;
        if(mem.evaluate_option(KJointChainMember::SingleOptions::is_inverse)) {
            prev = &joint.update_chain_matrix<checked, KJoint::InvType::is_inverse>(*prev);
        } else if(! mem.evaluate_option(KJointChainMember::SingleOptions::is_restart)) {
            prev = &joint.update_chain_matrix<checked>(*prev);
        } else {
            prev = &joint.get_chain_matrix();
        }
    }

    if(update_flags & update_masses) {
        // Reset the mass offset vectors of some important joints
        m_joints[JointIds::Root].m_chain_masspoint = m_joints[JointIds::Root].m_mass_offset;
        chain.back()->m_chain_masspoint = chain.back()->m_mass_offset;

        for(int i = chain.size() - 2; i >= 0; --i) {
            if(chain[i].evaluate_option(KJointChainMember::SingleOptions::is_inverse) && chain[i + 1].evaluate_option(KJointChainMember::SingleOptions::is_inverse)) {
                KJoint& joint = *chain[i];
                if(chain[i].evaluate_option(KJointChainMember::SingleOptions::is_in_multiple_chains)) {
                    joint.update_chain_masspoint_with_follower<false, KJoint::InvType::is_inverse>(*chain[i + 1]);
                    //joint.m_mass_endpoint = create_mass_offset((Eigen::Matrix<double, 4, 2>()<<joint.m_mass_endpoint, joint.m_mass_endpoint).finished()); TODO I don't get the sense
                    if(joint.get_id() != JointIds::Root) {
                        throw std::runtime_error("Currently, there is no support in this function for joints in multilple chain except the Root joint");
                    }
                } else {
                    joint.update_chain_masspoint_with_follower<false, KJoint::InvType::is_inverse>(*chain[i + 1]);
                }
            } else {
                if(chain[i].evaluate_option(KJointChainMember::SingleOptions::is_in_multiple_chains))
                    chain[i]->update_chain_masspoint_with_follower<true>(*chain[i + 1]);
                else if (!chain[i + 1].evaluate_option(KJointChainMember::SingleOptions::is_restart))
                    chain[i]->update_chain_masspoint_with_follower(*chain[i + 1]);
            }
        }
    }
}

template<AngleCheck check>
void KRobot::update_chain(KRobot::Chain& chain, uint update_flags) {
    // Avoid misinterpretation with to much bits set
    update_flags &= UpdateChainFlags::both;
    switch(update_flags) {
        case(UpdateChainFlags::reset_start_chain_matrix):
            return update_chain<check, UpdateChainFlags::reset_start_chain_matrix>(chain);
        case(UpdateChainFlags::update_masses):
            return update_chain<check, UpdateChainFlags::update_masses>(chain);
        case(UpdateChainFlags::both):
            return update_chain<check, UpdateChainFlags::both>(chain);
        default:
            return update_chain<check, UpdateChainFlags::NOP>(chain);
    }
}

void KRobot::update_chain(KRobot::Chain& chain, KRobot::AngleCheck check, uint update_flags) {
    // Avoid misinterpretation with to much bits set
    check = (KRobot::AngleCheck)(check & AngleCheck::check);
    switch(check) {
        case(AngleCheck::check):
            return update_chain<AngleCheck::check>(chain, update_flags);
        case(AngleCheck::unchecked):
            return update_chain<AngleCheck::unchecked>(chain, update_flags);
        default:
            return update_chain<AngleCheck::check>(chain, update_flags);
    }
}


template<AngleCheck checked>
BITBOTS_INLINE void KRobot::update_chain(cuint chain_id) {
    Chain& chain = m_chains[chain_id];
    const Affine3d* prev = &(m_joints[JointIds::Root].m_chain_matrix);
    for(unsigned i = 0; i < chain.size(); ++i) {
        prev = &chain[i]->update_chain_matrix<checked>(*prev);
    }
}

template<AngleCheck checked>
BITBOTS_INLINE void KRobot::update_chains() {
    m_joints[JointIds::Root].m_chain_matrix = id4;
    for(unsigned i = 0; i < m_chains.size(); ++i) {
        update_chain<checked>(i);
    }
}

void KRobot::update_robot_masses() {
    for(Chain& chain: m_chains) {
        update_chain(chain, KJoint::AngleCheck::unchecked, UpdateChainFlags::both);
    }
}

KRobot::KRobot()
:m_max_motor_id(0)
{
    init_mass();
    assert(all_data_valid());
}

KRobot::KRobot(const IdMapping& idMapping, const ChainMapping& chainMapping, const Joints& joints, const ChainsTemplate& chains_template, int max_id)
:m_joints(joints), m_id_mapping(idMapping), m_chain_mapping(chainMapping), m_max_motor_id(max_id)
{
    init_chains(chains_template, max_id);
    init_mass();
    assert(all_data_valid());
}

KRobot::KRobot(const KRobot& other)
: m_joints(other.m_joints), m_id_mapping(other.m_id_mapping), m_chain_mapping(other.m_chain_mapping), m_joint_chain_mapping(other.m_joint_chain_mapping), m_max_motor_id(other.m_max_motor_id)
{
    create_chain_template_and_init_chains(other);
    init_mass();
    assert(all_data_valid());
}
#define INIT_MOVE(X) X(std::move(other.X))
KRobot::KRobot (KRobot&& other)
: INIT_MOVE(m_joints), INIT_MOVE(m_chains), INIT_MOVE(m_id_mapping), INIT_MOVE(m_chain_mapping), INIT_MOVE(m_joint_chain_mapping), INIT_MOVE(m_max_motor_id), INIT_MOVE(m_mass)
{
    abort();
}
#undef INIT_MOVE

void KRobot::update(const Pose& pose, const bool positional_update) {
    vector<const Joint*> pose_joints(pose.get_const_joints());
    for(const Joint* pose_joint: pose_joints) {
        if(pose_joint->get_cid() > m_max_motor_id) {
            continue;
        }
        m_joints[pose_joint->get_cid()].update_angle<AngleCheck::unchecked>(pose_joint->get_position());
    }
    if(positional_update)
        update_chains<AngleCheck::unchecked>();
}

void KRobot::update_from_goals(const Pose& pose, const bool positional_update) {
    vector<const Joint*> pose_joints(pose.get_const_joints());
    for(const Joint* pose_joint: pose_joints) {
        if(pose_joint->get_cid() > m_max_motor_id) {
            continue;
        }
        m_joints[pose_joint->get_cid()].update_angle<AngleCheck::unchecked>(pose_joint->get_goal());
    }
    if(positional_update)
        update_chains<AngleCheck::unchecked>();
}

void KRobot::update(const VectorXd& angles, const bool positional_update) {
    assert(m_max_motor_id == angles.rows());

    for(unsigned i = 0; i < (unsigned)angles.rows(); ++i) {
        m_joints[i + 1].update_angle_rad(angles(i));
    }
    if(positional_update)
        update_chains();
}

bool KRobot::all_data_valid() const {
    for(const KJoint& j: m_joints) {
        if(! j.all_data_valid())
            return false;
    }
    return true;
}

Vector4d KRobot::get_centre_of_gravity() const {
    Matrix4Xd offsets(4, m_joints.size());
    for(uint i = 0; i < m_joints.size(); ++i) {
        offsets.col(i) = m_joints[i].get_centre_of_gravity();
    }
    return create_mass_offset(offsets);
}

Vector4d KRobot::get_centre_of_gravity(const Matrix4d& offset) const {
    Vector4d cog(get_centre_of_gravity());
    return (Vector4d()<<(offset * (Vector4d()<<cog.head<3>(), 1).finished()).head<3>(), cog(3)).finished();
}

void KRobot::init_mass() {
    double mass = 0;
    for(const KJoint& joint: m_joints) {
        mass += joint.get_mass();
    }
    m_mass = mass;
}

void KRobot::print_robot_data_for_debug() const{
    map<string,int>::const_iterator chain_it = m_chain_mapping.begin();
    cout<<"Chain names and Id's"<<endl;
    while(chain_it != m_chain_mapping.end()){
        cout<<chain_it->first<<" "<< chain_it->second<<endl;
        for(uint i = 0; i < m_chains[chain_it->second].size(); ++i) {
            cout<<m_chains[chain_it->second][i]->get_id()<<endl;
        }
        ++chain_it;
    }
    map<string,int>::const_iterator motor_it = m_id_mapping.begin();
    cout<<"Motor names and Id's"<<endl;
    while(motor_it != m_id_mapping.end()){
        cout<<motor_it->first<<" "<< motor_it->second<<endl;
        m_joints[motor_it->second].print_joint_for_debug();
        ++motor_it;
    }
}

template<class Derived>
BITBOTS_INLINE void Kin::fill_jacobi_matrix(Eigen::Block<Derived> jacobi, const KRobot::Chain& chain, const AxisType axis) {
    const Vector3d endpoint = chain.back()->get_endpoint<3>(axis);
    for(int i = jacobi.cols() - 1; i >= 0; --i) {
        const KJointChainMember mem = chain[i + 1];
        if(mem.ignore_for_axis(axis)) {
            jacobi.col(i) = Vector3d::Zero();
            continue;
        }
        const KJoint& current = *mem;
        Vector3d gradient = current.get_local_gradient(endpoint, axis);
        if(mem.evaluate_option(KJointChainMember::SingleOptions::is_inverse))
            gradient = -gradient;
        jacobi.col(i).noalias() = current.get_chain_matrix().linear() * gradient;
    }
    //P_DEBUG("Jacobi for Debug"<<endl<<jacobi);
}

void Kin::fill_jacobi_matrix_l(KRobot::JacobiType& jacobi, const KRobot::Chain& chain, const AxisType axis) {
    fill_jacobi_matrix(jacobi.block(0,0,jacobi.rows(), jacobi.cols()), chain, axis);
}

BITBOTS_INLINE void Kin::fill_cog_jacobi_matrix(KRobot::JacobiType& jacobi, KRobot::Chain& chain, const double mass) {
    for(int i = jacobi.cols() - 1; i >= 0; --i) {
        const KJointChainMember mem = chain[i + 1];
        if(mem.ignore_for_cog()) {
            jacobi.col(i) = Vector3d::Zero();
            continue;
        }
        const KJoint& current = *mem;
        Vector3d gradient = current.get_local_cog_gradient();
        jacobi.col(i).noalias() = current.get_chain_matrix().linear() * gradient;
    }
    jacobi.array() /= mass;
    //L_DEBUG(cout<<"Jacobi for Debug"<<endl<<jacobi<<endl);
}

void Kin::fill_cog_jacobi_matrix_l(KRobot::JacobiType& jacobi, KRobot::Chain& chain, const double mass) {
    fill_cog_jacobi_matrix(jacobi, chain, mass);
}

template<bool use_local_cog>
int KRobot::inverse_cog_chain(Chain& chain, const Vector3d& target, const Vector3i& ignore_axis, const double error, int const max_it, const double min_angle_d, bool allow_angle_manipulation) {

    int it = max_it + 1;
    const int last = chain.size() - 1;
    int static_end_joints = 1;
    update_chain<AngleCheck::unchecked, UpdateChainFlags::reset_start_chain_matrix | UpdateChainFlags::update_masses>(chain);
    while(chain[last - static_end_joints].evaluate_option(KJointChainMember::Options::need_to_ignore))++static_end_joints;
    /* Ignoring the root joint; The jacobi matrix contains only dynamic joints, so every index is 1 lower than in the chain \
     * Additionally skipping the last joint, that has no effect*/
    const int single_jacobi_cols = (last - static_end_joints);
    JacobiType jacobi(3, single_jacobi_cols);
    Vector3d delta;
    double delta_norm = 0;
    delta = target - get_centre_of_gravity().template head<3>();
    #define HANDLE_IGNORE_AXIS \
    for(unsigned i = 0; i < 3; ++i) { \
        if(ignore_axis(i)) { \
            delta(i) = 0; \
        } \
    }
    HANDLE_IGNORE_AXIS
    //L_DEBUG(cout<<"Debug delta"<<endl<<delta<<endl);

    AngleMatrixType deltaQ(single_jacobi_cols, 1);
    AngleMatrixType angleOff;

    //Iterating until the error is sufficiently small
    do {
        if(allow_angle_manipulation) {
            manipulate_chain_angles<ChainManipulation::add>(angleOff, chain, single_jacobi_cols);
        }
        // TODO need to adjust this method when I want to work with local cog chain inversions, then I need the cog offset for the chains first joint
        fill_cog_jacobi_matrix(jacobi, chain, m_mass);
        InverseJacobiType pseudo_inverse = _intern::pseudo_inverse(jacobi);
        //pseudo_inverse.col(2) = VectorXd::Zero(jacobi.cols(), 1);
        deltaQ.noalias() = pseudo_inverse * delta;
        deltaQ.array() = deltaQ.array().min(max_angle_diff_to_skip).max(min_angle_diff_to_skip);
        if(allow_angle_manipulation) {
            deltaQ -= angleOff;
        }

        //L_DEBUG(cout<<"Inverse: "<<endl;cout<<pseudo_inverse<<endl);
        //L_DEBUG(cout<<"Debug delta"<<endl<<delta<<endl);
        //L_DEBUG(cout<<"Debug angle diffs"<<endl<<deltaQ*rad_to_degree<<endl);

        //updating for the next iteration, root joint has no angle
        for(int i = 1; i <= deltaQ.rows(); ++i) {
            if(chain[i]->get_id() > m_max_motor_id) {
                continue;
            }
            chain[i]->m_angle += deltaQ(i - 1, 0);
        }
        /*// Most possibly, even the roots chain matrix was manipulated, we need to reset it.
        m_joints[JointIds::Root].m_chain_matrix = Matrix::Identity();*/
        //Force the kinematic to have a legal pose
        update_chain<AngleCheck::check, UpdateChainFlags::reset_start_chain_matrix | UpdateChainFlags::update_masses>(chain);
        delta = target - get_centre_of_gravity().template head<3>();
        // Set the delta value to zero, when the axis should be ignored
        HANDLE_IGNORE_AXIS
        delta_norm = delta.norm();
        if(true || delta_norm < (50 * error))//FIXME I think I only want to manipulate once
            allow_angle_manipulation = false;
    } while(delta_norm > error && --it && deltaQ.norm() > min_angle_d);
    L_DEBUG(if(deltaQ.norm() < min_angle_d && delta_norm > error && it != 0)cout<<"Abbruch nach Delta"<<endl);
    L_DEBUG(update_chains();cout<<"Debug endpoint"<<endl<<get_centre_of_gravity()<<endl);
    L_DEBUG(cout<<"Debug angles"<<endl;for(uint i = 1; i < chain.size()-1;++i)cout<<chain[i]->get_angle() * rad_to_degree<<" ";cout<<endl);
    L_DEBUG(if(it != 0)cout<<"Brauchte nur: "<< max_it - it << " Iterationen" << endl);
    return it == 0 ? -1 : max_it - it;
}

int KRobot::inverse_local_cog_chain(Chain& chain, const Vector3d& target, const Vector3i& ignore_axis, const double error, const int max_it, const double min_angle_d, const bool allow_angle_manipulation) {
    return inverse_cog_chain<true>(chain, target, ignore_axis, error, max_it, min_angle_d, allow_angle_manipulation);
}

int KRobot::inverse_global_cog_chain(Chain& chain, const Vector3d& target, const Vector3i& ignore_axis, const double error, const int max_it, const double min_angle_d, const bool allow_angle_manipulation) {
    return inverse_cog_chain<false>(chain, target, ignore_axis, error, max_it, min_angle_d, allow_angle_manipulation);
}

int KRobot::inverse_chain(Chain& chain, const MultipleTargetType& target, const MultipleErrorType& error, const unsigned max_it, const MultipleAxisType axis, const double min_angle_d) {
    assert(axis(0) != AxisType::None);
    assert(target.rows() / 3 == error.cols() && error.cols() == axis.rows());
    //P_DEBUG("Target\n"<<target);

    unsigned it = 0;
    const int last = chain.size() - 1;
    const KJoint& end_joint = *chain[last];
    int static_end_joints = 1;
    while(chain[last - static_end_joints].evaluate_option(KJointChainMember::Options::need_to_ignore))++static_end_joints;
    /* Ignoring the root joint; The jacobi matrix contains only dynamic joints, so every index is 1 lower than in the chain \
     * Additionally skipping the last joint, that has no effect*/
    const int single_jacobi_cols = (last - static_end_joints);
    JacobiType jacobi(axis.rows() * 3, single_jacobi_cols);
    MultipleTargetType delta(3 * axis.rows(), 1);
    for(uint i = 0; i < (unsigned)axis.rows(); ++i)delta.block<3, 1>(3 * i, 0) = target.block<3, 1>(3 * i, 0) - end_joint.get_endpoint<3>(axis(i));
    DeltaNormType delta_norms = Eigen::Map<Eigen::Matrix3Xd>(delta.data(), 3, axis.rows()).colwise().norm().array();
    //L_DEBUG(cout<<"Debug delta"<<endl<<delta<<"\n");
    //P_DEBUG("Debug endpoint"<<endl<<end_joint.get_endpoint<3>(axis(0)));
    AngleMatrixType deltaQ(single_jacobi_cols * axis.rows(), 1);
    AngleMatrixType angleOff;
    bool need_to_manipulate_angles = (delta_norms > (10 * error)).all();

    //Iterating until the error is sufficiently small
    do {
        if(need_to_manipulate_angles) {
            manipulate_chain_angles<ChainManipulation::add>(angleOff, chain, single_jacobi_cols);
        }
        for(uint i =  0; i < (unsigned)axis.rows(); ++i) {
            fill_jacobi_matrix(jacobi.block(3 * i, 0, 3, jacobi.cols()), chain, axis(i));
        }
        InverseJacobiType pseudo_inverse(_intern::pseudo_inverse(jacobi));
        deltaQ.noalias() = pseudo_inverse * delta;
        if(need_to_manipulate_angles) {
            deltaQ -= angleOff;
        }

        //updating for the next iteration, root joint has no angle
        for(int i = 1; i <= deltaQ.rows(); ++i) {
            if(chain[i]->get_id() > m_max_motor_id) {
                continue;
            }
            chain[i]->m_angle += deltaQ(i - 1, 0);
        }
        //Force the kinematic to have a legal pose
        update_chain<AngleCheck::check, UpdateChainFlags::NOP, true>(chain);
        for(uint i = 0; i < (unsigned)axis.rows(); ++i) delta.block<3, 1>(3 * i, 0) = target.block<3, 1>(3 * i, 0) - end_joint.get_endpoint<3>(axis(i));
        delta_norms = Eigen::Map<Eigen::Matrix3Xd>(delta.data(), 3, axis.rows()).colwise().norm().array();
        if(true || (delta_norms < (10 * error)).any()) { /*FIXME, I just want to manipulate once*/
            need_to_manipulate_angles = false;
        } else {
            need_to_manipulate_angles = true;
        }
    } while((delta_norms > error).any() && ++it < max_it && deltaQ.norm() > min_angle_d);
    L_DEBUG(if(deltaQ.norm() < min_angle_d && (delta_norms > error).any() && it != 0)cout<<"Abbruch nach Delta"<<endl);
    P_DEBUG("Debug endpoint\n"<<end_joint.get_endpoint<3, AxisType::None>(axis(0)).transpose());
    P_DEBUG("Debug delta\n"<<delta.transpose());
    L_DEBUG(cout<<"Debug angles"<<endl;for(uint i = 1; i < chain.size()-1;++i)cout<<chain[i]->get_angle() * rad_to_degree<<" ";cout<<endl);
    L_DEBUG(if(it != max_it)cout<<"Brauchte nur: "<< it << " Iterationen" << endl);
    return it == max_it ? -1 : it;
}

void KRobot::set_initial_angles(const KRobot::Vector3& rpy, const int chain) {
    m_joints[0].m_chain_matrix.linear() = create_rotation_matrix(rpy);
    if(chain == -1) {
        update_chains<AngleCheck::unchecked>();
    } else {
        update_chain<AngleCheck::unchecked>(m_chains[chain]);
    }
}


void KRobot::set_angles_to_pose(Pose& pose, const int chain_id, const float time) {
    bool success = true;
    if(chain_id == -1) {
        for(const KJoint& joint: m_joints) {
            #define UPDATE_JOINT_IN_POSE \
            if(joint.get_id() > m_max_motor_id || joint.get_id() == 0) { \
                continue; \
            } \
            Joint* pose_joint = pose.get_joint_by_cid(joint.get_id()); \
            double new_pose_joint_angle = joint.get_angle() * rad_to_degree; \
            if(time > 0) { \
                pose_joint->set_speed(fabs(pose_joint->get_position() - new_pose_joint_angle) / time); \
            } else { \
                pose_joint->set_speed(0); \
            } \
            success = success && pose_joint->set_goal(new_pose_joint_angle);
            UPDATE_JOINT_IN_POSE
        }
    } else {
        assert((uint)chain_id < m_chains.size());
        for(const KJointChainMember& mem: m_chains[chain_id]) {
            const KJoint& joint = *mem;
            UPDATE_JOINT_IN_POSE
        }
        #undef UPDATE_JOINT_IN_POSE
    }
    if(!success) {
        L_DEBUG(cerr<<"Konnte nicht alle Winkel schreiben"<<endl);
    }
}

bool KRobot::plausibility_check(const KRobot::Chain& chain, const Vector3d& target) {
    assert(chain.size() > 1);
    const KJoint* last_inactive_joint = chain[0].ptr();
    unsigned i = 1;
    while(chain[i].ignore_for_axis(KJoint::AxisType::Position)) {
        last_inactive_joint = chain[i].ptr();
        ++i;
        L_DEBUG(if(chain.size() == i)throw runtime_error("Chain must contain non inactive members"));
    }
    Vector3d static_target_part = last_inactive_joint->template get_endpoint<3>();
    double dynamic_length = 0;
    while(i < chain.size()) {
        dynamic_length += chain[i]->get_transform().translation().head<3>().norm();
        ++i;
    }
    return (target - static_target_part).norm() <= dynamic_length;
}
