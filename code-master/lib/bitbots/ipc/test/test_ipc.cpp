#include <iostream>
#include <thread>
#include <array>
#include <strstream>
#include <utility>

#include <gtest/gtest.h>
#include <gtest/gtest-spi.h>

#include "../shm.hpp"
#include "../../debug/debugmacro.h"

using namespace std;
using namespace IPC;
using namespace Robot;

namespace Test {
//#define EXPECT_EQ(expected, actual) EXPECT_EQ(expected, actual)<< "But was:"<<endl<< actual<< endl<<"instead of"<<endl<<expected

static const unsigned size = 2500;
typedef array<Pose, size> PoseArray;

template<bool write_into_pose, bool secure=false>
struct ThreadWorker {
    void operator()(SharedMemoryIPCProvider* ipc, PoseArray* poses) {
        // The pointer stuff is necessary, because the compiler complains about references
        for(Pose& p: *poses) {
            if(write_into_pose){
                if(secure) {
                    p = ipc->get_pose();
                } else {
                    p = ipc->get_pose_ref();
                }
            } else {
                ipc->update(p);
            }
        }
    }
};

void check_poses(PoseArray& poses, int& num_errors) {
    // Check the given poses.
    // It should be invariant, that all motor positions are equal for a given pose.
    // Until now, this is not garanteed, although we try to secure these raise conditions using a mutex
    unsigned i = 0;
    // Some bloating stuff to assure we only generate one non fatal failure, and then just count the number of errors.
    bool already_had_error = false;
    for(Pose& p: poses) {
        float set_values = p.get_joints()[0]->get_goal();
        strstream s;
        s<<"Pose "<<i<<"\n";
        bool err = false;
        for(Joint* j: p.get_joints()) {
            if(j->get_goal() != set_values && !err) {
                s<<"Error with Pose: Expect "<<set_values<<" insteadt of "<<j->get_goal()<<"\n";
                err = true;
                ++num_errors;
            }
            if(already_had_error)
                continue;
            EXPECT_EQ(j->get_goal(), set_values);
            EXPECT_TRUE(set_values != 0);
            //EXPECT_EQ(j->get_position(), set_values);
            if(err)
                already_had_error = true;
        }
        if(err) {
            L_DEBUG(cout<<s.str()<<endl);
        } else {
            //L_DEBUG(cout<<"Pose OK:"<<i<<endl);
        }
        ++i;
    }
}

void prepare_ref_poses(PoseArray& refs) {
    int num = 1, max = 120;
    for(Pose& p: refs) {
        for(Joint* j: p.get_joints()) {
            j->set_position(num);
            j->set_speed(num);
            j->set_goal(num);
        }
        num = (++num) % max + 1;
        ASSERT_TRUE(num != 0);
    }
}

TEST(IPC, setStatePenalty) {
    SharedMemoryIPCProvider ipc;
    ipc.set_state(8);
}

TEST(IPC, RaceCondition) {
    SharedMemoryIPCProvider ipc;
    // Preparing many poses in a given array with nonzero values
    PoseArray refs, updates;
    prepare_ref_poses(refs);

    ipc.update(refs[refs.size() - 1]);
    ipc.lock();
    for(const Joint* j: ipc.get_pose_ref().get_const_joints())
        ASSERT_TRUE(j->get_goal() != 0);
    ipc.unlock();
    // Create one thread to update the ipc pose, and another to write the ipc pose into the second array
    thread t1(ThreadWorker<false>(), &ipc, &refs);
    thread t2(ThreadWorker<true, true>(), &ipc, &updates);
    t1.join();
    t2.join();

    // Expect some errors on the check
    int num_errors = 0;
    check_poses(updates, num_errors);

    EXPECT_EQ(num_errors, 0);

    L_DEBUG(cerr<<"Counted "<<num_errors<<" failures"<<endl);
}

TEST(IPC, RaceConditionUnsecure) {
    SharedMemoryIPCProvider ipc;
    // Preparing many poses in a given array with nonzero values
    PoseArray refs, updates;
    prepare_ref_poses(refs);

    ipc.update(refs[refs.size() - 1]);
    ipc.lock();
    for(const Joint* j: ipc.get_pose_ref().get_const_joints())
        ASSERT_TRUE(j->get_goal() != 0);
    ipc.unlock();
    // Create one thread to update the ipc pose, and another to write the ipc pose into the second array
    thread t1(ThreadWorker<false>(), &ipc, &refs);
    thread t2(ThreadWorker<true>(), &ipc, &updates);
    t1.join();
    t2.join();

    // Expect some errors on the check
    int num_errors = 0;
    EXPECT_NONFATAL_FAILURE(check_poses(updates, num_errors), "");

    EXPECT_GT(num_errors, 0);

    L_DEBUG(cerr<<"Counted "<<num_errors<<" failures"<<endl);
}

TEST(IPC, MultipleInstances) {
    SharedMemoryIPCProvider ipc1;
    ipc1.lock();
    int old_state = ipc1.get_state();
    int desired_state = 1337;
    ipc1.set_state(desired_state);
    
    SharedMemoryIPCProvider ipc2;
    EXPECT_EQ(ipc2.get_state(), desired_state);

    ipc1.set_state(old_state);
    ipc1.unlock();
}

TEST(IPC, resetPoseAndState) {
    SharedMemoryIPCProvider ipc;
    Pose pose;
    for(Joint* j: pose.get_joints()) {
        j->set_position(0);
        j->set_goal(0);
        j->set_speed(0);
    }
    ipc.update(pose);
    Pose p = ipc.get_pose();
    for(const Joint* j: p.get_joints()) {
        EXPECT_EQ(j->get_goal(), 0);
    }
    ipc.set_state(1);
}

} //namespace Test

using namespace ::Test;

int main(int argc, char** argv) {
    testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
