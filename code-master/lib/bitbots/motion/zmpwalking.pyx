# -*- encoding: utf8 -*-
from bitbots.robot.pose cimport Pose as CPose
from bitbots.robot.pypose cimport PyPose, wrap_pose
from libcpp cimport bool
from libcpp.string cimport string
from eigen cimport Vector3f
from eigen cimport Vector2d
from eigen cimport Vector3d
from cython.operator cimport dereference as deref

cdef public _ZMPParameter parameter = get_default_parameter()

cdef class ZMPParameter:

    def __cinit__(self):
        self.params = new _ZMPParameter(parameter)

    def __dealloc__(self):
        del self.params

    property belly_pitch:
        def __get__(self):
            return self.params.default_belly_pitch
        def __set__(self, float belly_pitch):
            self.params.default_belly_pitch = belly_pitch
    property belly_roll:
        def __get__(self):
            return self.params.default_belly_roll
        def __set__(self, float belly_roll):
            self.params.default_belly_roll = belly_roll
    property stepHeight:
        def __get__(self):
            return self.params.stepHeight
        def __set__(self, float stepHeight):
            self.params.stepHeight = stepHeight
    property tStep:
        def __get__(self):
            return self.params.tStep
        def __set__(self, float tStep):
            self.params.tStep = tStep
    property tZmp:
        def __get__(self):
            return self.params.tZmp
        def __set__(self, float tZmp):
            self.params.tZmp = tZmp
    property bodyHeight:
        def __get__(self):
            return self.params.bodyHeight
        def __set__(self, float bodyHeight):
            self.params.bodyHeight = bodyHeight
    property bodyTilt:
        def __get__(self):
            return self.params.bodyTilt
        def __set__(self, float bodyTilt):
            self.params.bodyTilt = bodyTilt
    property footX:
        def __get__(self):
            return self.params.footX
        def __set__(self, float footX):
            self.params.footX = footX
    property footY:
        def __get__(self):
            return self.params.footY
        def __set__(self, float footY):
            self.params.footY = footY
    property supportX:
        def __get__(self):
            return self.params.supportX
        def __set__(self, float supportX):
            self.params.supportX = supportX
    property supportY:
        def __get__(self):
            return self.params.supportY
        def __set__(self, float supportY):
            self.params.supportY = supportY
    property turnCompThreshold:
        def __get__(self):
            return self.params.turnCompThreshold
        def __set__(self, float turnCompThreshold):
            self.params.turnCompThreshold = turnCompThreshold
    property turnComp:
        def __get__(self):
            return self.params.turnComp
        def __set__(self, float turnComp):
            self.params.turnComp = turnComp
    property velFastForward:
        def __get__(self):
            return self.params.velFastForward
        def __set__(self, float velFastForward):
            self.params.velFastForward = velFastForward
    property velFastTurn:
        def __get__(self):
            return self.params.velFastTurn
        def __set__(self, float velFastTurn):
            self.params.velFastTurn = velFastTurn
    property supportFront:
        def __get__(self):
            return self.params.supportFront
        def __set__(self, float supportFront):
            self.params.supportFront = supportFront
    property supportFront2:
        def __get__(self):
            return self.params.supportFront2
        def __set__(self, float supportFront2):
            self.params.supportFront2 = supportFront2
    property supportBack:
        def __get__(self):
            return self.params.supportBack
        def __set__(self, float supportBack):
            self.params.supportBack = supportBack
    property supportSideX:
        def __get__(self):
            return self.params.supportSideX
        def __set__(self, float supportSideX):
            self.params.supportSideX = supportSideX
    property supportSideY:
        def __get__(self):
            return self.params.supportSideY
        def __set__(self, float supportSideY):
            self.params.supportSideY = supportSideY
    property supportTurn:
        def __get__(self):
            return self.params.supportTurn
        def __set__(self, float supportTurn):
            self.params.supportTurn = supportTurn
    property frontComp:
        def __get__(self):
            return self.params.frontComp
        def __set__(self, float frontComp):
            self.params.frontComp = frontComp
    property AccelComp:
        def __get__(self):
            return self.params.AccelComp
        def __set__(self, float AccelComp):
            self.params.AccelComp = AccelComp
    property supportModYInitial:
        def __get__(self):
            return self.params.supportModYInitial
        def __set__(self, float supportModYInitial):
            self.params.supportModYInitial = supportModYInitial
    property pDefault:
        def __get__(self):
            return self.params.pDefault
        def __set__(self, int pDefault):
            self.params.pDefault = pDefault
    property stanceLimitX:
        def __get__(self):
            return (self.params.stanceLimitX.at(0), self.params.stanceLimitX.at(1))
        def __set__(self, stanceLimitX):
            self.params.stanceLimitX = Vector2d(<double> stanceLimitX[0], <double> stanceLimitX[1])
    property stanceLimitY:
        def __get__(self):
            return (self.params.stanceLimitY.at(0), self.params.stanceLimitY.at(1))
        def __set__(self, stanceLimitY):
            self.params.stanceLimitY = Vector2d(<double> stanceLimitY[0], <double> stanceLimitY[1])
    property stanceLimitA:
        def __get__(self):
            return (self.params.stanceLimitA.at(0), self.params.stanceLimitA.at(1))
        def __set__(self, stanceLimitA):
            self.params.stanceLimitA = Vector2d(<double> stanceLimitA[0], <double> stanceLimitA[1])
    property velDelta:
        def __get__(self):
            return (self.params.velDelta.at(0), self.params.velDelta.at(1), self.params.velDelta.at(2))
        def __set__(self, velDelta):
            self.params.velDelta = Vector3d(<double> velDelta[0], <double> velDelta[1], <double> velDelta[2])
    property footSizeX:
        def __get__(self):
            return (self.params.footSizeX.at(0), self.params.footSizeX.at(1))
        def __set__(self, footSizeX):
            self.params.footSizeX = Vector2d(<double> footSizeX[0], <double> footSizeX[1])
    property qLArm:
        def __get__(self):
            return (self.params.qLArm.at(0), self.params.qLArm.at(1), self.params.qLArm.at(2))
        def __set__(self, qLArm):
            self.params.qLArm = Vector3d(<double> qLArm[0], <double> qLArm[1], <double> qLArm[2])
    property qRArm:
        def __get__(self):
            return (self.params.qRArm.at(0), self.params.qRArm.at(1), self.params.qRArm.at(2))
        def __set__(self, qRArm):
            self.params.qRArm = Vector3d(<double> qRArm[0], <double> qRArm[1], <double> qRArm[2])
    property phSingle:
        def __get__(self):
            return (self.params.phSingle.at(0), self.params.phSingle.at(1))
        def __set__(self, phSingle):
            self.params.phSingle = Vector2d(<double> phSingle[0], <double> phSingle[1])
    property stanceLimitMarginY:
        def __get__(self):
            return self.params.stanceLimitMarginY
        def __set__(self, stanceLimitMarginY):
            self.params.stanceLimitMarginY = stanceLimitMarginY
    property ankleSupportFaktor:
        def __get__(self):
            return self.params.ankleSupportFaktor
        def __set__(self, ankleSupportFaktor):
            self.params.ankleSupportFaktor = ankleSupportFaktor
    property armImuParamX:
        def __get__(self):
            return (self.params.armImuParamX.at(0),self.params.armImuParamX.at(1),self.params.armImuParamX.at(2),self.params.armImuParamX.at(3))
        def __set__(self, armImuParamX):
            self.params.armImuParamX = Vector4d(<double> armImuParamX[0],<double> armImuParamX[1],<double> armImuParamX[2],<double> armImuParamX[3])
    property armImuParamY:
        def __get__(self):
            return (self.params.armImuParamY.at(0),self.params.armImuParamY.at(1),self.params.armImuParamY.at(2),self.params.armImuParamY.at(3))
        def __set__(self, armImuParamY):
            self.params.armImuParamY = Vector4d(<double> armImuParamY[0],<double> armImuParamY[1],<double> armImuParamY[2],<double> armImuParamY[3])

    property zPhase:
        def __get__(self):
            return (self.params.zPhase.at(0),self.params.zPhase.at(1))
        def __set__(self, zPhase):
            self.params.zPhase = Vector2d(<double> zPhase[0], <double> zPhase[1])

    property xPhase:
        def __get__(self):
            return (self.params.xPhase.at(0),self.params.xPhase.at(1))
        def __set__(self, xPhase):
            self.params.xPhase = Vector2d(<double> xPhase[0], <double> xPhase[1])

    property bodyTiltXScaling:
        def __get__(self):
            return self.params.bodyTilt_x_scaling
        def __set__(self,bodyTiltXScaling):
            self.params.bodyTilt_x_scaling = bodyTiltXScaling


cdef class ZMPWalkingEngine:

    def __cinit__(self, ZMPParameter params=None, object config={}, string robottype="Darwin"):
        parameter = get_default_parameter()
        if params is None:
            self.thisptr = new _ZMPWalk(parameter)
        else:
            self.thisptr = new _ZMPWalk(deref(params.params))
        self.init_from_config(config, robottype)

    def __dealloc__(self):
        del self.thisptr
        del self.parameter

    cpdef init_from_config(self, object zmp_config, string robottype):
        # TODO: doppelt mit oben???
        self.r_shoulder_pitch_offset = zmp_config["r_shoulder_pitch"]
        self.l_shoulder_pitch_offset = zmp_config["l_shoulder_pitch"]
        self.r_shoulder_roll_offset = zmp_config["r_shoulder_roll"]
        self.l_shoulder_roll_offset = zmp_config["l_shoulder_roll"]
        self.hip_pitch_offset = zmp_config["hip_pitch"]
        self.hip_pitch = zmp_config["HipPitch"]
        self.set_long_legs(zmp_config["HasNewLongLegs"] ,zmp_config["LongLegs"], zmp_config["BodyOffsets"], zmp_config["FootHeight"])
        self.set_belly_roll_pid(zmp_config["BellyRollPID"])
        self.robottype = robottype

        self.set_velocity(0, 0, 0)
        self.stop()

    cpdef start(self):
        self.thisptr.start()

    cpdef stop(self):
        self.thisptr.stop()

    cpdef process(self):
        cdef unsigned char phase
        phase = self.thisptr.update()

        return int(phase)

    cpdef stance_reset(self):
        self.thisptr.stance_reset()

    cpdef set_active(self, bool active):
        self.thisptr.set_active(active)

    cpdef set_tiltX(self, float tiltX, float TiltX_longTime):
        self.thisptr.set_tiltX(tiltX, TiltX_longTime)

    cpdef set_velocity(self, float x, float y, float z):
        self.thisptr.set_velocity(x, y, z)

    cpdef reset(self):
        pass

    cdef set_gyro(self, int x, int y, int z):
        #Team Darwin hat beim Gyro x und y invertiert und mit '/0.273' komisch normiert
        #self.thisptr.set_gyro_data(Vector3d(-x/0.273, -y/0.273, z/0.273))
        self.thisptr.set_gyro_data(Vector3d(-x, -y, z))

    cdef set_long_legs(self,bool is_long, list legs, list body_offsets, float foot_height):
        cdef float thigh, tibia
        thigh, tibia = legs
        hip_y_offset, hip_z_offset = body_offsets
        if is_long is True:
            self.thisptr.set_long_legs(thigh, tibia, hip_y_offset, hip_z_offset, foot_height)

    cdef set_belly_roll_pid(self, list pid):
        p, i, d = pid
        self.thisptr.set_belly_roll_pid(p,i,d)

    property running:
        def __get__(self):
            return self.thisptr.is_active()

    property velocity:
        def __get__(self):
            cdef Vector3d vel = self.thisptr.get_velocity()
            return (vel.x(), vel.y(), vel.z())
        def __set__(self, object val):
            cdef float x, y, z
            x, y, z = val
            self.thisptr.set_velocity(x, y, z)

    property uLeft:
        def __get__(self):
            cdef Vector3d uLeft = self.thisptr.get_uLeft()
            return (uLeft.x(), uLeft.y(), uLeft.z())

    property uRight:
        def __get__(self):
            cdef Vector3d uRight = self.thisptr.get_uRight()
            return (uRight.x(), uRight.y(), uRight.z())

    property pose:
        def __get__(self):
            cdef PyPose p = wrap_pose(self.thisptr.get_pose())
            return p

    property gyro:
        def __set__(self, object val):
            cdef int x, y ,z
            x, y, z = val
            self.set_gyro(x, y, z)

    property hip_pitch:
        def __set__(self, float val):
            self.thisptr.set_hip_pitch(val)
        def __get__(self):
            return self.thisptr.get_hip_pitch()

    property r_shoulder_pitch_offset:
        def __set__(self, double offset):
            self.thisptr.set_r_shoulder_pitch_offset(offset)
        def __get__(self):
            return self.thisptr.get_r_shoulder_pitch_offset()

    property robottype:
        def __set__(self, string robottype):
            self.thisptr.set_robottype(robottype)
        def __get__(self):
            return self.thisptr.get_robottype()

    property l_shoulder_pitch_offset:
        def __set__(self, double offset):
            self.thisptr.set_l_shoulder_pitch_offset(offset)
        def __get__(self):
            return self.thisptr.get_l_shoulder_pitch_offset()

    property r_shoulder_roll_offset:
        def __set__(self, double offset):
            self.thisptr.set_r_shoulder_roll_offset(offset)
        def __get__(self):
            return self.thisptr.get_r_shoulder_roll_offset()

    property l_shoulder_roll_offset:
        def __set__(self, double offset):
            self.thisptr.set_l_shoulder_roll_offset(offset)
        def __get__(self):
            return self.thisptr.get_l_shoulder_roll_offset()

    property hip_pitch_offset:
        def __set__(self, double offset):
            self.thisptr.set_hip_pitch_offset(offset)
        def __get__(self):
            return self.thisptr.get_hip_pitch_offset()
