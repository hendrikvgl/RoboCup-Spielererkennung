
cdef class Robot:
    def __cinit__(self, bool initialize_empty=False):
        self.is_initialized_empty = initialize_empty
        if initialize_empty is True:
            self.robot = NULL
            return
        cdef object config = get_config()
        try:
            self.robot = create_robot_from_config(config)
        except BaseException, e:
            print e
            #exit()
            raise e

        # Mit einer leeren Pose initialisieren
        cdef Pose zero
        self.robot.update(zero)

    def __dealloc__(self):
        if not self.is_initialized_empty:
            del self.robot

    cdef const _Joint* get_c_joint_by_id(self, int id):
        return ref(self.robot.get_joint_by_id(id))
    cdef const _Joint* get_c_joint_by_name(self, string name):
        return ref(self.robot.get_joint_by_name(name))
    cpdef Joint get_joint_by_id(self, int id):
        cdef Joint joint = Joint(str(id))
        joint.set_joint(self.robot.get_joint_by_id(id))
        return joint
    cpdef Joint get_joint_by_name(self, string name):
        cdef Joint joint = Joint(name)
        joint.set_joint(self.robot.get_joint_by_name(name))
        return joint

    cpdef debugprint(self):
        self.robot.print_robot_data_for_debug()

    cpdef update(self, PyPose pose):
        self.robot.update(deref(pose.pose))

    cpdef update_masses(self):
        self.robot.update_robot_masses()

    cpdef inverse_chain_t(self, int id, object target, float error=1e-1, int max_it=1, int axis=-1):
        print "This Method is deprecated, use the direct one inverse_chain_t"
        self.inverse_chain(id, target, error, max_it, axis, False)

    cpdef inverse_chain(self, int id, object target, object error=1e-1, int max_it=1, object axis=-1, bool multiple=False):
        cdef object begin, end
        begin = time.time()
        cdef Vector3d c_target_v
        cdef VectorXd c_target_m = VectorXd(6, 1)
        cdef int num
        cdef MAxisType axx
        if not multiple:
            c_target_v = Vector3d(target[0], target[1], target[2])
            if axis is 3:
                c_target_v = c_target_v / 1000
            if axis is -1:
                num = self.robot.inverse_chain(id, c_target_v, <double>error, max_it)
            else:
                num = self.robot.inverse_chain(id, c_target_v, <double>error, max_it, int_to_axis(axis))
        else:
            c_target_m.insert(Vector3d(target[0][0], target[0][1], target[0][2])).add(Vector3d(target[1][0], target[1][1], target[1][2]))
            axx=MAxisType(2,1)
            axx.insert(int_to_axis(axis[0])).add(int_to_axis(axis[0]))
            for i in range(len(axis)):
                if axis[i] is 3:
                    c_target_m.col(i).insert(c_target_m.col(i) / 1000)
            num = self.robot.inverse_chain(id, c_target_m, Vector2d(<double>error[0], <double>error[1]), max_it, axx)
        end = time.time()
        cdef string s = "Berechnungszeit: %f" % (end - begin)
        print "Invertiert in %d Iterationen %s" % (num, s) if num is not -1 else "Keine Konvergenz %s" % s

    cpdef inverse_chain_m(self, int id, list targets, tuple errors, int max_it, tuple axis):
        self.inverse_chain(id, targets, errors, max_it, axis, True)


    cpdef inverse_cog_chain_t(self, int id, object target, object ignore_axis=(0,0,1), float error=1e-1, int max_it=1, bool local=True):
        print "This Method is deprecated, use the direct one: inverse_cog_chain"
        self.inverse_cog_chain(id, target, ignore_axis, error, max_it, local)

    cpdef inverse_cog_chain(self, int id, object target, object ignore_axis=np.array((0,0,1)), float error=1e-1, int max_it=1, bool local=True):
        cdef object begin, end
        begin = time.time()
        cdef Vector3d c_target = Vector3d(target[0], target[1], target[2])
        c_target = c_target / 1000
        cdef Vector3i c_ignore_axis = Vector3i(ignore_axis[0], ignore_axis[1], ignore_axis[2])
        cdef int num
        if local:
            num = self.robot.inverse_local_cog_chain(self.robot.get_chain_by_id(id), c_target, c_ignore_axis, error, max_it)
        else:
            num = self.robot.inverse_global_cog_chain(self.robot.get_chain_by_id(id), c_target, c_ignore_axis, error, max_it)
        end = time.time()
        cdef string s = "Berechnungszeit: %f" % (end - begin)
        print "Invertiert in %d Iterationen %s" % (num, s) if num is not -1 else "Keine Konvergenz %s" % s

    cpdef np.ndarray get_centre_of_gravity(self, bool with_mass=False):
        cdef Vector4d ep = self.robot.get_centre_of_gravity()
        cdef np.ndarray vec = np.array((ep.x(), ep.y(), ep.z(), ep.at(3)), dtype=np.float32)
        vec[0:3] = vec[0:3] * 1000
        if not with_mass:
            vec[3] = 1
        return vec

    cpdef np.ndarray get_centre_of_gravity_with_offset(self, np.ndarray of):
        of.reshape(4,4)
        cdef Matrix4d offset_m

        offset_m.insert(<double>of[0,0]).add(<double>of[0,1]).add(<double>of[0,2]).add(<double>of[0,3]) \
                   .add(<double>of[1,0]).add(<double>of[1,1]).add(<double>of[1,2]).add(<double>of[1,3]) \
                   .add(<double>of[2,0]).add(<double>of[2,1]).add(<double>of[2,2]).add(<double>of[2,3]) \
                   .add(<double>of[3,0]).add(<double>of[3,1]).add(<double>of[3,2]).add(<double>of[3,3])
        cdef Vector4d ep = self.robot.get_centre_of_gravity(offset_m)
        cdef np.ndarray vec = np.array((ep.x(), ep.y(), ep.z(), ep.at(3)), dtype=np.float32)
        vec[0:3] = vec[0:3] * 1000
        return vec

    cpdef float get_mass(self):
        return self.robot.get_mass()

    cpdef update_with_matrix(self, np.ndarray ndarr):
        if ndarr.ndim != 1 or ndarr.shape[0] != 20 or ndarr.dtype != np.float32:
            raise ValueError("Invalid joint Matrix")

        cdef arr = np.array(ndarr, dtype=np.float32)
        cdef double *data = <double*>np.PyArray_BYTES(arr)
        self.robot.update(<VectorXd>MapVectorXd(data, 20))

    cpdef PyPose set_angles_to_pose(self, PyPose pose, int chain_id=-1, float time=0):
        self.robot.set_angles_to_pose(deref(pose.pose), chain_id, time)
        return pose

    cpdef set_initial_angles(self, float roll, float pitch, float yaw):
        self.robot.set_initial_angles(Vector3d(roll, pitch, yaw))

    cpdef reset_initial_angles(self):
        self.robot.reset_initial_angles()

    cpdef Joint get_l_foot_endpoint(self):
        cdef Joint joint = Joint("LFootEndpoint")
        joint.set_joint(self.robot.get_joint_by_id(LFoot))
        return joint

    cpdef Joint get_r_foot_endpoint(self):
        cdef Joint joint = Joint("RFootEndpoint")
        joint.set_joint(self.robot.get_joint_by_id(RFoot))
        return joint

    cpdef Joint get_l_arm_endpoint(self):
        cdef Joint joint = Joint("LArmEndpoint")
        joint.set_joint(self.robot.get_joint_by_id(LArm))
        return joint

    cpdef Joint get_r_arm_endpoint(self):
        cdef Joint joint = Joint("RArmEndpoint")
        joint.set_joint(self.robot.get_joint_by_id(RArm))
        return joint

    cpdef Joint get_camera(self):
        cdef Joint joint = Joint("Camera")
        joint.set_joint(self.robot.get_joint_by_id(Cam))
        return joint

    cpdef Joint get_center(self):
        cdef Joint joint = Joint("Root")
        joint.set_joint(self.robot.get_joint_by_id(Center))
        return joint

    cdef list chain_to_list(self, const_Chain& chain):
        cdef list result = []
        cdef Joint joint
        cdef const_ChainIterator it = chain.begin()

        while it != chain.end():
            joint = Joint("")
            joint.set_joint(deref(it).get())
            result.append(joint)
            it += 1

        return result

    cpdef list get_l_arm_chain(self):
        return self.chain_to_list(self.robot.get_chain_by_id(LArmC))

    cpdef list get_l_leg_chain(self):
        return self.chain_to_list(self.robot.get_chain_by_id(LLegC))

    cpdef list get_r_arm_chain(self):
        return self.chain_to_list(self.robot.get_chain_by_id(RLegC))

    cpdef list get_r_leg_chain(self):
        return self.chain_to_list(self.robot.get_chain_by_id(LLegC))

    cpdef list get_head_chain(self):
        return self.chain_to_list(self.robot.get_chain_by_id(HeadC))
