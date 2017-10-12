from collections import deque
import math
import networkx as nx

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

        # Used to track next node to target
        self.current_target = None

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

        # How close in mm until we stop driving to avoid collision with vision objects
        collision_avoid_distance = 100

        # How close in mm until we consider ourselves at a given point
        point_target_margin = 60
        
        # All actions the agent wishes to take are stored in this queue
        actions_queue = deque()

        # Decide if we should stop to avoid hitting wall
        if (not self.is_car_inbounds()):
            self.print_filtered("Stopping to avoid collision with wall.")
            actions_queue.append(["STOP",0,0])
            return actions_queue
            
        # Check vision objects
        for vis_obj in self.vision_objects:

            # Dont detect potential collision with self
            if(vis_obj.MAC_Address == self.address):
                continue

            # Decide if we should stop to avoid collision with a vision object
            distanceToObject = self.calculate_distance(self.x_pos, self.y_pos,vis_obj.X_Pos, vis_obj.Y_Pos)
            if(distanceToObject < collision_avoid_distance):
                self.print_filtered("Stopping to avoid collision with an object in sight.")
                actions_queue.append(["STOP",0,0])
                return actions_queue

        # Decide what position to target
        if (self.current_target is None):
            # Haven't got a target, so pick first node in graph - this particular graph node index starts from 1
            self.current_target = self.map_graph.nodes(data=True)['1']
        else:
            # Check if we have reached target
            if (self.calculate_distance(self.x_pos,self.y_pos,int(self.current_target['x']),int(self.current_target['y'])) < point_target_margin):
                # If we have, change target to next node in map graph
                self.current_target = self.map_graph.nodes(data=True)[list(nx.neighbors(self.map_graph, self.current_target['node_id']))[0]]
            else:
                # Haven't reached it, so keep targetting it
                pass

        # Queue actions               
        actions_queue.append(["FORWARD",100,0])
        actions_queue.append(["TARGET",int(self.current_target['x']),int(self.current_target['y'])])
        
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
        border = 25;
        x_max = 1200 - border;
        x_min = 0 + border;
        y_max = 900 - border;
        y_min = 0 + border;
        
        if self.x_pos > x_min and self.x_pos < x_max and self.y_pos > y_min and self.y_pos < y_max:
            return True
        else:
            return False

    '''
    Function which prints iff self.output is set to "Verbose"
    Useful for development testing and debugging.
    '''
    def print_filtered(self, output_string):
        if (self.output == "Verbose"):
            print(output_string)
