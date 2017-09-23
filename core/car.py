from core.protocol import *
import math

#An object of the car class controls a specific car
#By calling functions within this class commands are sent to the car
class Car:
    def __init__(self, address, socket):

        # The unique identifier for this car
        self.address = address

        # Observed parameters of the car
        self.Orientation = 0
        self.X_Pos = 0
        self.Y_Pos = 0      
        self.X_Vel = 0
        self.Y_Vel = 0

        # Precepts of the car - for the moment this is everything
        self.Vision_Objects = []

        self.acceleration = 0
        self.steering = 0

        self.preceptTime = 0

        # Defines the rounded rectange path which the car will follow
        self.targets = [(180,450),(250,630),(425,730),(790,730),(970,630),(1030,450),(970,270),(790,170),(445,170),(250,260)]
        self.currentTarget = 0
        
        # Create the client socket
        self.socket = socket

        # Create dictionary for storing output messages
        self.out_dict = dict()

    # Queue given command with associated time
    def queueCommand(self, command):
        if (command not in self.out_dict):
            self.out_dict[command] = self.preceptTime

    def updatePreceptTime(self, newTime):
        self.preceptTime = newTime
        
    def updatePrecepts(self, visionObjects):
        self.Vision_Objects = visionObjects
                
    def updateStateFromVisionObject(self,stateVariables):
        self.Orientation = stateVariables.Orientation
        self.X_Pos = stateVariables.X_Pos
        self.Y_Pos = stateVariables.Y_Pos      
        self.X_Vel = stateVariables.X_Vel
        self.Y_Vel = stateVariables.Y_Vel

    def getOrientationToTarget(self):
        displacementX = self.targets[self.currentTarget][0] - self.X_Pos
        displacementY = self.targets[self.currentTarget][1] - self.Y_Pos

        displacementOrientation = (90 - 180/math.pi*math.atan2(displacementY, displacementX));
        if (displacementOrientation < 0):
                displacementOrientation = 360 + displacementOrientation;
				
        return displacementOrientation
    
    def distance(self, x1,y1,x2,y2):
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    
    # Check car is not going to hit a vision object
    def carIsInFreeSpace(self):
        for vis_obj in self.Vision_Objects:
            if vis_obj.MAC_Address != self.address:
                distanceToObject = self.distance(self.X_Pos, self.Y_Pos,vis_obj.X_Pos, vis_obj.Y_Pos)
                print("Distance to other car: %d mm" % distanceToObject)
                if(distanceToObject < 150):
                    print("Car too close to other object in sight")
                    return False
                else:
                    print("Car not too close to other object")
        # Got this far without finding anything in our zone, so must be in free space
        return True
    
    # Check car is within bounds
    def carIsWithinBounds(self):        
        border = 100;
        x_max = 1200 - border;
        x_min = 0 + border;
        y_max = 900 - border;
        y_min = 0 + border;
        
        # whilst in bounds, drive at constant speed
        if self.X_Pos > x_min and self.X_Pos < x_max and self.Y_Pos > y_min and self.Y_Pos < y_max:
            return True
        else:
            return False

    def calculateSpeed(self):
        return math.sqrt(self.X_Vel**2 + self.Y_Vel**2)
    
    # desiredOrientation - number from 0 to 359
    def orientationControl(self, desiredOrientation):
        
        requiredSteering = 0
        
        # Can't do anything if we are too slow as the orientation value is incorrectly reported as zero
        if(self.calculateSpeed() < 25):
            return
        
        #print ('### START ORIENTATION CONTROL ###')
        
        errorAngle = ((((desiredOrientation - self.Orientation) % 360) + 540) % 360) - 180;
        #print ('Current: %d, Desired %d, errorAngle: %d' % (self.Orientation, desiredOrientation, errorAngle))
        sensitivity = 0.4
        requiredSteering = int(errorAngle * sensitivity)

        # Upper and lower bound the amount of steering
        maxSteering = 50
        if(requiredSteering > maxSteering):
            requiredSteering = maxSteering
        elif(requiredSteering < -maxSteering):
            requiredSteering = -maxSteering

        # Only send steering command if we need to change
        if (self.steering != requiredSteering):
            self.steering = requiredSteering
            # Send steering command
            if self.steering != 0:
                #print ('Steering with intensity %d' % self.steering)
                self.queueCommand(bytes([STEERING, self.steering & 0x7f]))
            else:
                #print ('Steering STRAIGHT')
                self.queueCommand(bytes([STEERING, 0]))
                
    def checkCarAtTarget(self):        
        distanceToTarget = self.distance(self.X_Pos, self.Y_Pos,self.targets[self.currentTarget][0], self.targets[self.currentTarget][1])
        if(distanceToTarget < 50):
            self.currentTarget = (self.currentTarget + 1) % len(self.targets)
            #print("Car targetting (%d,%d)" % (self.targets[self.currentTarget][0], self.targets[self.currentTarget][1]))
        else:
            pass
            #print("Car targetting (%d,%d)" % (self.targets[self.currentTarget][0], self.targets[self.currentTarget][1]))

    def decideAction(self):        
        if (self.carIsWithinBounds() and self.carIsInFreeSpace()):
            #print("Car in bounds and free space... driving")

            desiredSpeed = 30
            if(self.acceleration != desiredSpeed):
                self.acceleration=desiredSpeed
                self.queueCommand(bytes([THROTTLE, self.acceleration & 0x7f])) 
            
            self.checkCarAtTarget()            
            self.orientationControl(self.getOrientationToTarget())
        else:
            # Stop as car is out of bounds or is going to hit something
            print("Car out of bounds or going to collide... stopping.")
            self.stop()
        
    def horn(self):
        self.queueCommand(bytes([HORN, HORN_ON]))
        #sleep(0.5)
        self.queueCommand(bytes([HORN, HORN_OFF]))

    def LightsOn(self):
        self.queueCommand(bytes([HEADLIGHT, HEADLIGHT_BRIGHT]))
        
    def LightsOff(self):
        self.queueCommand(bytes([HEADLIGHT, HEADLIGHT_OFF]))

    def run(self):
        if(self.acceleration != 20):
            self.acceleration=20
            self.queueCommand(bytes([THROTTLE, self.acceleration & 0x7f]))
    def stop(self):
        if(self.acceleration != 0):
            self.acceleration=0
            self.queueCommand(bytes([THROTTLE, 0]))
