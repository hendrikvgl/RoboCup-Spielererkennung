from libcpp cimport bool
from libcpp.vector cimport vector
from libcpp.map cimport map
from libcpp.string cimport string
from cython.operator cimport address as ref
from cython.operator cimport dereference as deref

import time

from eigen cimport *
import numpy as np
cimport numpy as np
# Nötig, wenn man Numpy ordentlich mit Cython nutzen will
np.import_array()

from bitbots.util import get_config
from bitbots.robot.pose cimport Pose
from bitbots.robot.pypose cimport PyPose

def rfoot():
    return RFoot
def lfoot():
    return LFoot

# Important the implementation of the class Robot is in this included file robot.pxi
include "robot.pxi"

cdef class Joint:

    def __cinit__(self, string name):
        self.name = name
        self.has_value = False

    def __dealloc__(self):
        del self.joint

    cdef set_joint(self, const _Joint& joint):
        if self.has_value is True:
            del self.joint
        self.joint = new _Joint(joint)
    cdef init_from_joint(self, const _Joint& joint):
        if self.has_value is True:
            del self.joint
        self.joint = new _Joint(joint)

    cpdef get_angle(self):
        return self.joint.get_angle()

    cpdef update_angle(self, float degree):
        self.joint.update_angle(degree)

    cpdef np.ndarray get_chain_matrix(self, bool inverse=False):
        cdef Affine3d cm = self.joint.get_chain_matrix_inverse() if inverse else self.joint.get_chain_matrix()
        cdef np.ndarray mat = matrix4d_to_numpy(cm.matrix())
        mat[0:3,3] = mat[0:3,3] * 1000
        return mat

    cpdef np.ndarray get_transform(self, bool inverse=False):
        cdef Affine3d tr = self.joint.get_inverse_transform() if inverse else self.joint.get_transform()
        cdef np.ndarray mat = matrix4d_to_numpy(tr.matrix())
        mat[0:3,3] = mat[0:3,3] * 1000
        return mat

    cpdef np.ndarray get_centre_of_gravity(self, bool with_mass=False):
        cdef Vector4d cog
        cog = self.joint.get_centre_of_gravity() if with_mass else self.joint.get_normalized_centre_of_gravity()
        cdef np.ndarray vec = np.array((cog.x(), cog.y(), cog.z()),dtype=np.float32)
        return vec * 1000

    cpdef np.ndarray get_chain_masspoint(self):
        cdef Vector4d cmp = self.joint.get_chain_masspoint()
        cdef np.ndarray vec = np.array((cmp.x(), cmp.y(), cmp.z()),dtype=np.float32)
        return vec * 1000

    cpdef np.ndarray get(self):
        cdef Matrix4d tr = self.joint.get_transform().matrix()
        cdef np.ndarray mat = matrix4d_to_numpy(tr)
        mat[0:3,3] = mat[0:3,3] * 1000
        return mat

    cpdef np.ndarray get_endpoint(self):
        cdef Vector4d ep = self.joint.get_endpoint()
        return np.array((ep.x(), ep.y(), ep.z()), dtype=np.float32) * 1000

    cdef const _Joint* get_joint(self):
        return self.joint

    cpdef int get_id(self):
        return self.joint.get_id()

    cdef string get_name(self):
        return str(self.name)


cdef class ChainHolder:

    def __cinit__(self):
        pass
    def __dealloc__(self):
        pass

    cdef _ChainHolder get(self):
        return deref(self.chain)

    cdef set(self, _ChainHolder chain):
        self.chain = new _ChainHolder(chain)

    cpdef Joint get_joint(self, int idx):
        cdef Joint rvalue = Joint("")
        rvalue.set_joint(self.chain.get_joint(idx))
        return rvalue

    cpdef int size(self):
        return self.chain.size() if self.chain is not NULL else 0

cdef class KinematicTask:

    def __cinit__(self, Robot robot):
        self.task = new _KinematicTask(deref(robot.robot))

    cpdef perform(self, int fromm, int to, object target, object error=1e-3, object axis=3, int max_it=100, list first_task_ids=[], list ignore_joints=[]):
        cdef Vector3d target_v
        cdef VectorXd target_m = VectorXd(6,1)
        cdef JointID from_id = int_to_JointID(fromm)
        cdef JointID to_id = int_to_JointID(to)
        cdef AxisT ax
        cdef MAxisType axx
        cdef set[unsigned int] ft_ids
        cdef set[int] ignore_j
        for idd in first_task_ids:
            ft_ids.insert(<unsigned int> idd)
        for ig in ignore_joints:
            ignore_j.insert(<int> ig)
        if len(first_task_ids) == 0:
            # easy case, where only one target is set
            ax = int_to_axis(axis)
            target_v = Vector3d(target[0], target[1], target[2])
            if axis is 3:
                target_v = target_v / 1000
            self.task.perform_task(from_id, to_id, target_v, ax, <double>float(error), max_it, ignore_j)
        else:
            axx = MAxisType(2, 1)
            axx.insert(int_to_axis(axis[0])).add(int_to_axis(axis[1]))
            target_m.insert(Vector3d(target[0][0], target[0][1], target[0][2])).add(Vector3d(target[1][0], target[1][1], target[1][2]))
            for i in range(len(axis)):
                if axis[i] is 3:
                    target_m.col(i).insert(target_m.col(i) / 1000)
            self.task.perform_task(from_id, to_id, target_m, axx, Vector2d(<double>float(error[0]), <double>float(error[1])), ft_ids, max_it, ignore_j)

    cpdef ChainHolder create_chain(self, int fromm, int to, object axis=3, list first_task_ids=[], list ignore_joints=[]):
        cdef ChainHolder rvalue = ChainHolder()
        cdef JointID from_id = int_to_JointID(fromm)
        cdef JointID to_id = int_to_JointID(to)
        cdef AxisT ax
        cdef MAxisType axx
        cdef set[unsigned int] ft_ids
        cdef vector[set[uint]] idset_for_tasks
        cdef set[int] ignore_j
        cdef bool use_first_task_ids_Not_the_idset = True
        for idd in first_task_ids:
            if isinstance(idd, int):
                ft_ids.insert(<unsigned int> idd)
                assert(use_first_task_ids_Not_the_idset)
            else:
                use_first_task_ids_Not_the_idset = False
                for iddd in idd:
                    ft_ids.insert(<unsigned int> iddd)
                idset_for_tasks.push_back(ft_ids)
                ft_ids.clear()
        for ig in ignore_joints:
            ignore_j.insert(<int> ig)
        if len(first_task_ids) == 0:
            # easy case, where only one target is set
            ax = int_to_axis(axis)
            rvalue.set(self.task.create_chain(from_id, to_id, ax, ignore_j))
        else:
            axx = MAxisType(len(axis), 1)
            if len(axis) is 2:
                axx.insert(int_to_axis(axis[0])).add(int_to_axis(axis[1]))
            elif len(axis) is 3:
                axx.insert(int_to_axis(axis[0])).add(int_to_axis(axis[1])).add(int_to_axis(axis[2]))
            if use_first_task_ids_Not_the_idset:
                rvalue.set(self.task.create_chain(from_id, to_id, axx, ft_ids, ignore_j))
            else:
                rvalue.set(self.task.create_chain(from_id, to_id, axx, idset_for_tasks, ignore_j))
        return rvalue

    cpdef ChainHolder create_cog_chain(self, int chain_id, list ignore_joints=[]):
        ###_ChainHolder create_centre_of_gravity_chain(ChainIds chain_id, set[int] ignore_joints, _DisableType disable_chain)
        cdef ChainHolder rvalue = ChainHolder()
        cdef ChainID chain = int_to_ChainID(chain_id)
        cdef set[int] ignore_j
        for ig in ignore_joints:
            ignore_j.insert(<int> ig)
        rvalue.set(self.task.create_centre_of_gravity_chain(chain, ignore_j, directChain))
        return rvalue

    cpdef perform_h(self, ChainHolder chain, object target, object error=1e-1, object axis=3, int max_it=1):
        cdef Vector3d target_v
        cdef MTargetType target_m
        cdef AxisT ax
        cdef MAxisType axx
        cdef MErrorType error_m
        if not isinstance(axis, (list, tuple, np.ndarray)):
            # easy case, where only one target is set
            ax = int_to_axis(axis)
            target_v = Vector3d(target[0], target[1], target[2])
            self.task.perform_task(deref(chain.chain), target_v, ax, <double>float(error), max_it)
        else:
            axx = MAxisType(len(axis), 1)
            target_m = VectorXd(3 * len(axis), 1)
            error_m = MErrorType(1, len(axis))
            if len(axis) is 2:
                axx.insert(int_to_axis(axis[0])).add(int_to_axis(axis[1]))
                target_m.insert(Vector3d(target[0][0], target[0][1], target[0][2])).add(Vector3d(target[1][0], target[1][1], target[1][2]))
                error_m.insert(<double>error[0]).add(<double>error[1])
            elif len(axis) is 3:
                axx.insert(int_to_axis(axis[0])).add(int_to_axis(axis[1])).add(int_to_axis(axis[2]))
                target_m.insert(Vector3d(target[0][0], target[0][1], target[0][2])).add(Vector3d(target[1][0], target[1][1], target[1][2])).add(Vector3d(target[2][0], target[2][1], target[2][2]))
                error_m.insert(<double>error[0]).add(<double>error[1]).add(<double>error[2])
            for i in range(len(axis)):
                if axis[i] is 3:
                    target_m.col(i).insert(target_m.col(i) / 1000)
            self.task.perform_task(deref(chain.chain), target_m, axx, error_m, max_it)

    cpdef perform_cog_task(self, int chain_id, object):
        pass

    cpdef update_chain(self, ChainHolder chain, int flags):
        self.task.update_robot_chain(deref(chain.chain), flags)
