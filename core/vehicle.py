from core.protocol import *
from vehicles import *
from agents import *
import math

#An object of the vehicle class controls a specific car
#By calling functions within this class commands are sent to the car
class Vehicle:
    def __init__(self, address, socket, agent, vehicle):

        # The unique identifier for this car
        self.address = address

        # The agent which controls this vehicle's actions
        if (agent == "Human"):
            self.agent = Human.Human(self.address)
        else :
            print("Invalid agent. Must be 'Human'.")

        # The vehicle type which defines parameters such as vehicle speed, acceleration and turning circle
        if (vehicle == "Car"):
            self.vehicle = Car.Car()
        else :
            print("Invalid vehicle. Must be 'Car'.")

        # Observed parameters of the car
        self.Orientation = 0
        self.X_Pos = 0
        self.Y_Pos = 0      
        self.X_Vel = 0
        self.Y_Vel = 0
        
        # Precepts of the car - for the moment this is everything
        # TODO: Filter precepts
        self.Vision_Objects = []

        self.acceleration = 0
        self.steering = 0

        # Time car was last seen, for tracking overall system delay
        self.preceptTime = 0

        # Defines the rounded rectange path which the car will follow
        # TODO: Use the graph instead
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

    # Update time car was last seen, for tracking overall system delay
    def updatePreceptTime(self, newTime):
        self.preceptTime = newTime

    # Update this cars precepts
    def updatePrecepts(self, visionObjects, map_graph):
        self.Vision_Objects = visionObjects
        self.agent.update_precepts(self.Orientation, self.X_Pos,self.Y_Pos, self.X_Vel,self.Y_Vel, map_graph, self.Vision_Objects)
    
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

    def calculateSpeed(self):
        return math.sqrt(self.X_Vel**2 + self.Y_Vel**2)
    
    # desiredOrientation - number from 0 to 359
    def orientationControl(self, desiredOrientation):
        
        requiredSteering = 0
        
        # Can't do anything if we are too slow as the orientation value is incorrectly reported as zero
        if(self.calculateSpeed() < 25):
            print ('### Too slow to control orientation ###')
            return
        
        print ('### START ORIENTATION CONTROL ###')
        
        errorAngle = ((((desiredOrientation - self.Orientation) % 360) + 540) % 360) - 180;
        print ('Current: %d, Desired %d, errorAngle: %d' % (self.Orientation, desiredOrientation, errorAngle))
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
                print ('Steering with intensity %d' % self.steering)
                self.queueCommand(bytes([STEERING, self.steering & 0x7f]))
            else:
                print ('Steering STRAIGHT')
                self.queueCommand(bytes([STEERING, 0]))

    def decideAction(self):
        # Get agent to decide what to do
        decided_actions = self.agent.decide_actions()

        # Take decided actions and convert to car commands
        for action in decided_actions:
            action_name = action[0]
            action_arg1 = action[1]
            action_arg2 = action[2]

            print(action_name)

            if (action_name == "STOP"):
                self.stop()
            elif (action_name == "FORWARD"):
                self.acceleration=self.vehicle.filter_speed(self.acceleration, action_arg1)
                self.queueCommand(bytes([THROTTLE, self.acceleration & 0x7f]))
            elif (action_name == "REVERSE"):
                self.acceleration=self.vehicle.filter_speed(self.acceleration, action_arg1)
                self.queueCommand(bytes([THROTTLE, self.acceleration & 0x7f]))
            elif (action_name == "LEFT"):
                self.steering = self.vehicle.filter_turn(self.steering, action_arg1)
                self.queueCommand(bytes([STEERING, self.steering & 0x7f]))
                pass
            elif (action_name == "RIGHT"):
                self.steering = -self.vehicle.filter_turn(self.steering, action_arg1)
                self.queueCommand(bytes([STEERING, self.steering & 0x7f]))
            elif (action_name == "TARGET"):
                #TODO: Test this
                displacementX = action_arg1 - self.X_Pos
                displacementY = action_arg2 - self.Y_Pos
                displacementOrientation = (90 - 180/math.pi*math.atan2(displacementY, displacementX));
                if (displacementOrientation < 0):
                        displacementOrientation = 360 + displacementOrientation;
                # TODO: Filter output steering and speed amounts
                self.orientationControl(displacementOrientation)
            else:
                # Unrecognised action, do nothing
                pass
        
    def checkCarAtTarget(self):
        distanceToTarget = self.distance(self.X_Pos, self.Y_Pos,self.targets[self.currentTarget][0], self.targets[self.currentTarget][1])
        if(distanceToTarget < 50):
            self.currentTarget = (self.currentTarget + 1) % len(self.targets)

    def horn(self):
        self.queueCommand(bytes([HORN, HORN_ON]))
        sleep(0.5)
        self.queueCommand(bytes([HORN, HORN_OFF]))

    def headlight_on(self):
        self.queueCommand(bytes([HEADLIGHT, HEADLIGHT_BRIGHT]))
        
    def headlight_off(self):
        self.queueCommand(bytes([HEADLIGHT, HEADLIGHT_OFF]))

    def run(self):
        if(self.acceleration != 20):
            self.acceleration=20
            self.queueCommand(bytes([THROTTLE, self.acceleration & 0x7f]))
    
    def stop(self):
        if(self.acceleration != 0):
            self.acceleration=0
            self.queueCommand(bytes([THROTTLE, 0]))
