from bitbots.ipc.ipc import SharedMemoryIPC
import time
ipc = SharedMemoryIPC()
print "count, Accel x, Accel y, Accel z, Gyro x, Gyro y, Gyro z, Gyro norm"
i=0
def v2f(vec):
    return vec.x, vec.y, vec.z
while True:
    time.sleep(0.01)
    i+=1
    #print "Accel: %03.4f %03.4f %03.4f" % ipc.get_accel(), " Gyro: %03.4f %03.4f %03.4f" % ipc.get_gyro()
    print i, ",", ipc.get_accel().x, ",",ipc.get_accel().y,",",ipc.get_accel().z, ", ", ipc.get_gyro().x, ",",ipc.get_gyro().y, ",", ipc.get_gyro().z, ",", ipc.get_gyro().norm()
