import copy
import math
import time

import numpy as np

from skimage.color import rgb2gray

from pysim.constants import *
from pysim import track

class Racecar:

    def __init__(self, bullet_client, origin, carpos, planeId, direction_field, urdfRootPath='', timeStep=0.01):
        self.urdfRootPath = urdfRootPath
        self.timeStep = timeStep
        self._p = bullet_client
        self._origin = origin
        self._carpos = carpos
        self._direction_field = direction_field
        self._dist_sensors = DISTANCE_SENSORS
        self.speed = 0
        self.rayHitColor = [1,0,0]
        self.rayMissColor = [0,1,0]
        self._time = time.time()
        self._sensor = []
        self._planeId = planeId
        self.reset()

    def reset(self):
        x = self._origin[0]
        y = self._origin[1]
        z = self._origin[2] + 0.03
        scale = 0.41
        carsize = 0.205
        carx = x + self._carpos[0] 
        cary = y + self._carpos[1] - carsize/2
        #carx = x+2.90-0.35
        #cary = y+0.35-carsize/2
        #cary = y + 5.0-carsize/2
        carStartOrientation = self._p.getQuaternionFromEuler([0, 0, self._carpos[2]])
        carStartOrientation90 = self._p.getQuaternionFromEuler([0,0,math.pi/2])
        carStartOrientation00 = self._p.getQuaternionFromEuler([0,0,0])
#        carId = self._p.loadURDF("data/racecar/racecar.urdf", [carx, cary, z], carStartOrientation90, globalScaling=scale)
        car = self._p.loadURDF("./pysim/data/racecar/racecar_differential1.urdf", [carx, cary, z], carStartOrientation, globalScaling=scale,useFixedBase=False)
#        car = self._p.loadURDF(os.path.join(self.urdfRootPath,"racecar/racecar_differential.urdf"), [0,0,.2],useFixedBase=False)
        self.racecarUniqueId = car
        #for i in range (self._p.getNumJoints(car)):
        #    print (self._p.getJointInfo(car,i))
        for wheel in range(self._p.getNumJoints(car)):
            self._p.setJointMotorControl2(car,wheel,self._p.VELOCITY_CONTROL,targetVelocity=0,force=0)
            self._p.getJointInfo(car,wheel)

        #self._p.setJointMotorControl2(car,10,self._p.VELOCITY_CONTROL,targetVelocity=1,force=10)
        c = self._p.createConstraint(car,9,car,11,jointType=self._p.JOINT_GEAR,jointAxis =[0,1,0],parentFramePosition=[0,0,0],childFramePosition=[0,0,0])
        self._p.changeConstraint(c,gearRatio=1, maxForce=10000)

        c = self._p.createConstraint(car,10,car,13,jointType=self._p.JOINT_GEAR,jointAxis =[0,1,0],parentFramePosition=[0,0,0],childFramePosition=[0,0,0])
        self._p.changeConstraint(c,gearRatio=-1, maxForce=10000)

        c = self._p.createConstraint(car,9,car,13,jointType=self._p.JOINT_GEAR,jointAxis =[0,1,0],parentFramePosition=[0,0,0],childFramePosition=[0,0,0])
        self._p.changeConstraint(c,gearRatio=-1, maxForce=10000)

        c = self._p.createConstraint(car,16,car,18,jointType=self._p.JOINT_GEAR,jointAxis =[0,1,0],parentFramePosition=[0,0,0],childFramePosition=[0,0,0])
        self._p.changeConstraint(c,gearRatio=1, maxForce=10000)

        c = self._p.createConstraint(car,16,car,19,jointType=self._p.JOINT_GEAR,jointAxis =[0,1,0],parentFramePosition=[0,0,0],childFramePosition=[0,0,0])
        self._p.changeConstraint(c,gearRatio=-1, maxForce=10000)

        c = self._p.createConstraint(car,17,car,19,jointType=self._p.JOINT_GEAR,jointAxis =[0,1,0],parentFramePosition=[0,0,0],childFramePosition=[0,0,0])
        self._p.changeConstraint(c,gearRatio=-1, maxForce=10000)

        c = self._p.createConstraint(car,1,car,18,jointType=self._p.JOINT_GEAR,jointAxis =[0,1,0],parentFramePosition=[0,0,0],childFramePosition=[0,0,0])
        self._p.changeConstraint(c,gearRatio=-1, gearAuxLink = 15, maxForce=10000)
        c = self._p.createConstraint(car,3,car,19,jointType=self._p.JOINT_GEAR,jointAxis =[0,1,0],parentFramePosition=[0,0,0],childFramePosition=[0,0,0])
        self._p.changeConstraint(c,gearRatio=-1, gearAuxLink = 15,maxForce=10000)

        self.steeringLinks = [0,2]
        self.maxForce = 1000
        self.nMotors = 2
        self.motorizedwheels=[8,15]
        self.speedMultiplier = 51
        # self.steeringMultiplier = 0.257729373093 # +/- 14.7668 grad
        self.steeringMultiplier = 0.5

        # self.speedParameter = self._p.addUserDebugParameter('Speed', 0, 2, 1)
        _ = self.getSensor()

    def getCoordinate(self):
        carpos, carorn = self._p.getBasePositionAndOrientation(self.racecarUniqueId)

        posEuler = self._p.getEulerFromQuaternion(carorn)

        yaw = posEuler[2]

        return carpos[0], carpos[1], yaw

    def diffAngle(self):

        x, y, yaw = self.getCoordinate()

        in0   = any([func(x, y) for func in self._direction_field[0]])
        in45  = any([func(x, y) for func in self._direction_field[45]])
        in90  = any([func(x, y) for func in self._direction_field[90]])
        in135 = any([func(x, y) for func in self._direction_field[135]])
        in180 = any([func(x, y) for func in self._direction_field[180]])
        in225 = any([func(x, y) for func in self._direction_field[225]])
        in270 = any([func(x, y) for func in self._direction_field[270]])
        in315 = any([func(x, y) for func in self._direction_field[315]])


        if not (in0 or in45 or in90 or in135 or in180 or in225 or in270 or in315): # not in any field.
            # TODO: condition something.
            # print('*****************************')
            return 0
        else:
            # print('Yaw:\t', round(math.degrees(yaw))+180)
            # yaw = abs(yaw)
            if in0:
                # print(0)
                return abs(yaw-0)
            if in45:
                # print(45)
                return abs(yaw-math.pi/4)
            if in90:
                # print(90)
                return abs(yaw-math.pi/2)
            if in135:
                # print(135)
                return abs(yaw-math.pi/2-math.pi/4)
            if in180:
                # print(180)
                return abs(abs(yaw)-math.pi)
            if in225:
                # print(225)
                return abs(yaw+math.pi/2+math.pi/4)
            if in270:
                # print(270)
                return abs(yaw+math.pi/2)
            if in315:
                # print(in315)
                return abs(yaw+math.pi/4)

    def getSensor(self):
        x_, y_, yaw = self.getCoordinate()

        def rayWithRadians(x, y, radians, R=[10, 10]):

            # calculate position to rayTest
            x_new = R[0] * math.cos(radians) + x
            y_new = R[1] * math.sin(radians) + y

            try:
                # position ray hit
                _, _, hit, pos, _ = self._p.rayTest([x, y, 0], [x_new, y_new, 0])[0]

                # distance from car
                distance = ((pos[0] - x) ** 2 + (pos[1] - y) ** 2) ** 0.5

                # track.createObj(self._p, self._origin, pos[0], pos[1])

                if hit == 1.: # miss
                    return (x_new, y_new), 7
                else:
                    return (pos[0], pos[1]), distance
            except Exception as e:
                print('not found object', e)

                return (x_new, x_new), 7

        obs = []

        now_time = time.time()

        disp = True
        if (now_time - self._time) > .3:
            disp = True

        for degree in self._dist_sensors:
            to, distance = rayWithRadians(x_, y_, yaw + math.radians(-degree))
            obs.append(distance)
            # self._p.addUserDebugLine([x_, y_, 0], [to[0], to[1], 0], self.rayHitColor)
            # track.createObj(self._p, self._origin, hits[0], hits[1])
            # print(degree, distance, (x_, y_), to)

        return np.array(obs)

    def getObservation(self):

        observation = None

        if OBSERVATION_TYPE == 'image':
            observation = self.getCameraImage() # to gray scale
        if OBSERVATION_TYPE == 'sensor':
            # observation = np.concatenate([self.getSensor(), np.array([self.speed/self.speedMultiplier])]) # norm
            # observation = self.getSensor()/7
            observation = np.concatenate([self.getSensor()/7, [self.diffAngle()/math.pi], np.array([self.speed/self.speedMultiplier])]) # norm
        if OBSERVATION_TYPE == 'sensor+image':
            observation = np.concatenate([self.getSensor()/7, self.getCameraImage().flatten()/255])

        return observation

    def getCameraImage(self):

        ls = self._p.getLinkState(self.racecarUniqueId, 5, computeForwardKinematics=True)
        camPos = ls[0]
        camOrn = ls[1]
        camMat = self._p.getMatrixFromQuaternion(camOrn)
        upVector = [0, 0, 1]
        forwardVec = [camMat[0], camMat[3], camMat[6]]
        camUpVec =  [camMat[2], camMat[5], camMat[8]]
        camTarget = [camPos[0]+forwardVec[0]*10, camPos[1]+forwardVec[1]*10, camPos[2]+forwardVec[2]*10]
        camUpTarget = [camPos[0]+camUpVec[0], camPos[1]+camUpVec[1], camPos[2]+camUpVec[2]]
        viewMat = self._p.computeViewMatrix(camPos, camTarget, camUpVec)
        projMat = (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, -1.0000200271606445, -1.0, 0.0, 0.0, -0.02000020071864128, 0.0)
        return self._p.getCameraImage(CAMERA_WIDTH, CAMERA_HEIGHT, viewMatrix=viewMat,projectionMatrix=projMat, renderer=self._p.ER_BULLET_HARDWARE_OPENGL, shadow=0)[2]

    def _isCollision(self, part_id):

        aabbmin, aabbmax = self._p.getAABB(self.racecarUniqueId,
                                           part_id)  # 5==red block; 1==right wheel; 3==left wheel
        objs = self._p.getOverlappingObjects(aabbmin, aabbmax)
        # print(objs)

        for x in objs:
            if (x[1] == -1 and not (x[0] == self.racecarUniqueId or x[0] == self._planeId)):
                return True
        return False

    def isCollision(self):

        return any([self._isCollision(i) for i in range(1, 10)])

    def applyAction(self, motorCommands):

        # sp = self._p.readUserDebugParameter(self.speedParameter)
        targetVelocity = motorCommands[0]*self.speedMultiplier
        # targetVelocity = sp*self.speedMultiplier
        self.speed = targetVelocity
        
        steeringAngle = motorCommands[1]*self.steeringMultiplier

        for motor in self.motorizedwheels:
            self._p.setJointMotorControl2(self.racecarUniqueId,motor,self._p.VELOCITY_CONTROL,targetVelocity=targetVelocity,force=self.maxForce)
        for steer in self.steeringLinks:
            self._p.setJointMotorControl2(self.racecarUniqueId,steer,self._p.POSITION_CONTROL,targetPosition=steeringAngle)
