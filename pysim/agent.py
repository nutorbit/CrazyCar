import os,  inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

import copy
import math
import time

import numpy as np

from pysim.constants import DISTANCE_SENSORS
from pysim import track

class Racecar:

    def __init__(self, bullet_client, origin, carpos, urdfRootPath='', timeStep=0.01, calibration=False):
        self.urdfRootPath = urdfRootPath
        self.timeStep = timeStep
        self._p = bullet_client
        self._origin = origin
        self._carpos = carpos
        self._calibration = calibration
        self._dist_sensors = DISTANCE_SENSORS
        self.speed = 0
        self.rayHitColor = [1,0,0]
        self.rayMissColor = [0,1,0]
        self._time = time.time()
        self._sensor = []
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
        car = self._p.loadURDF(os.path.join(currentdir, "data/racecar/racecar_differential.urdf"), [carx, cary, z], carStartOrientation, globalScaling=scale,useFixedBase=False)
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

    def getSensor(self):
        # initial sensors
        carpos, carorn = self._p.getBasePositionAndOrientation(self.racecarUniqueId)

        posEuler = self._p.getEulerFromQuaternion(carorn)

        yaw = posEuler[2]

        x_, y_  = carpos[0], carpos[1]

        def rayWithRadians(x, y, radians, R=[6, 6]):

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
                    return (x_new, y_new), 100
                else:
                    return (pos[0], pos[1]), distance
            except Exception as e:
                print('not found object', e)

                return (x_new, x_new), 100

        obs = []

        now_time = time.time()

        # disp = True
        # if (now_time - self._time) > .3:
        #     disp = True

        for degree in self._dist_sensors[:]:
            to, distance = rayWithRadians(x_, y_, yaw + math.radians(-degree))
            # self._p.addUserDebugLine([x_, y_, 0], [hits[0], hits[1], 0], self.rayHitColor)
            # track.createObj(self._p, self._origin, hits[0], hits[1])
            # print(degree, distance, (x_, y_), to)
            # if disp:
                # sensor_id = self._p.addUserDebugLine([x_, y_, 0], [0, 0, 0], self.rayMissColor if distance == 100 else self.rayHitColor, parentObjectUniqueId=self.racecarUniqueId)
                # self._sensor.append(sensor_id)
                # self._time = now_time
            obs.append(distance)

        # if disp:
        #     if self._sensor != []:
        #         for sensor_id in self._sensor[:len(self._dist_sensors)]:
        #             self._p.removeUserDebugItem(sensor_id)
        #     self._sensor = self._sensor[len(self._dist_sensors):]

        return obs


    def getActionDimension(self):
        return self.nMotors

    def getObservationDimension(self):
        return len(self.getObservation())

    def getObservation(self):
        observation = []
        pos,orn=self._p.getBasePositionAndOrientation(self.racecarUniqueId)

        observation.extend(list(pos))
        observation.extend(list(orn))

        return observation

    def applyAction(self, motorCommands):

        # sp = self._p.readUserDebugParameter(self.speedParameter)
        targetVelocity = motorCommands[0]*self.speedMultiplier
        # targetVelocity = sp*self.speedMultiplier
        self.speed = targetVelocity
        #print("targetVelocity")
        #print(targetVelocity)
        
        steeringAngle = motorCommands[1]*self.steeringMultiplier
        # if (motorCommands[1] < 106):
        #     steeringAngle = (-4.0/709.0 * motorCommands[1] + 285.0/478.0)
        # else:
        #     steeringAngle = -(4.0/709.0 * motorCommands[1] - 285.0/478.0)
        #print("steeringAngle")
        #print("{} => {}".format(motorCommands[1], steeringAngle))
        #print("maxForce")
        #print(self.maxForce)

        for motor in self.motorizedwheels:
            self._p.setJointMotorControl2(self.racecarUniqueId,motor,self._p.VELOCITY_CONTROL,targetVelocity=targetVelocity,force=self.maxForce)
        for steer in self.steeringLinks:
            self._p.setJointMotorControl2(self.racecarUniqueId,steer,self._p.POSITION_CONTROL,targetPosition=steeringAngle)
