from collections import deque
import math

class Human(object):
    
    agent_name = 'Human'
    agent_description = 'Agent modelled around human driving behavior'
    output = "Verbose";
    
    '''
    Constructor
    '''
    def __init__(self, address):
        self.address = address
        self.orientation = 0
        self.x_pos = 0
        self.y_pos = 0
        self.x_vel = 0
        self.y_vel = 0
        self.speed = 0
        self.map_graph = None
        self.vision_objects = []

    '''
    Called by the vehicle class to update the agent precepts
    '''
    def update_precepts(self, orientation, x_pos,y_pos,x_vel,y_vel, map_graph, vision_objects):
        self.orientation = orientation
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.speed = math.sqrt(self.x_vel**2 + self.y_vel**2)
        self.map_graph = map_graph
        self.vision_objects = vision_objects

    '''
    This function is called by the vehicle class when it is time to decide what to do
    
    The logic for the agent should go here, as follows:
    1. Use the self variables to determine what the vehicle should do.    
    2. Queue all desired actions in the actions_queue

    Once this funciton finishes, the actions will then be adjusted as appropriate
    for the vehicle type and then sent to the vehicle
    
    Allowable actions are:
    ["STOP",0,0]
    ["FORWARD",SPEED(0-100%),0]
    ["REVERSE",SPEED(0-100%),0]
    ["LEFT",AMOUNT(0-100%),0]
    ["RIGHT",AMOUNT(0-100%),0]
    ["TARGET",X Coordinate,Y Coordinate]
    '''    
    def decide_actions(self):
        # All actions the agent wishes to take are stored in this queue
        actions_queue = deque()

        # Check for wall of simulator
        if (not self.is_car_inbounds()):
            # Decide to stop to avoid hitting wall
            self.print_filtered("Stopping to avoid collision with wall.")
            actions_queue.append(["STOP",0,0])
            return actions_queue
            
        # Check vision objects
        for vis_obj in self.vision_objects:

            # Dont detect potential collision with self
            if(vis_obj.MAC_Address == self.address):
                continue
            
            distanceToObject = self.calculate_distance(self.x_pos, self.y_pos,vis_obj.X_Pos, vis_obj.Y_Pos)
            if(distanceToObject < 150):
                # Decide to stop to avoid collision with a vision object
                self.print_filtered("Stopping to avoid collision with an object in sight.")
                actions_queue.append(["STOP",0,0])
                return actions_queue

        # Not going to hit anything, so drive forward at 100%
        self.print_filtered("Not hitting anything, so drive forward.")
        actions_queue.append(["FORWARD",100,0])

        # Return actions_queue
        return actions_queue

    '''
    Calculate distance from (x1,y1) to (x2,y2)
    '''
    def calculate_distance(self, x1,y1,x2,y2):
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    '''
    Check car is within bounds
    '''
    def is_car_inbounds(self):        
        border = 100;
        x_max = 1200 - border;
        x_min = 0 + border;
        y_max = 900 - border;
        y_min = 0 + border;
        
        # whilst in bounds, drive at constant speed
        if self.x_pos > x_min and self.x_pos < x_max and self.y_pos > y_min and self.y_pos < y_max:
            return True
        else:
            return False

    def print_filtered(self, output_string):
        if (self.output == "Verbose"):
            print(output_string)
