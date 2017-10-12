import math

class Car(object):
    
    vehicle_name = 'Car'
    vehicle_description = 'Standard car vehicle'

    max_speed = 20
    max_acceleration = 20
    max_deceleration = 20

    max_turn = 40
    max_turn_change = 20
    
    '''
    Constructor
    '''
    def __init__(self):
        pass

    '''
    Filters the speed and speed change of the vehicle as per the limits above
    '''
    def filter_speed(self,current_speed,desired_speed):
        output_speed = current_speed
        delta_speed = desired_speed - current_speed

        # Limit acceleration and deceleration
        if (delta_speed > 0):
            # Acceleration
            if(delta_speed < self.max_acceleration):
                output_speed += delta_speed
            else:
                output_speed += self.max_acceleration
        elif (delta_speed < 0):
            # Deceleration
            if(math.abs(delta_speed) < math.abs(self.max_deceleration)):
                output_speed -= math.abs(delta_speed)
            else:
                output_speed -= math.abs(self.max_deceleration)
        else:
            # No speed change, so do nothing
            pass

        # Limit speed to the max speed
        if (output_speed > self.max_speed):
            output_speed = self.max_speed
        if (output_speed < -self.max_speed):
            output_speed = -self.max_speed
        return output_speed

    '''
    Filters the turn of the vehicle as per the limits above
    '''
    def filter_turn (self, current_turn, desired_turn):
        
        if (abs(desired_turn - current_turn) > self.max_turn_change):
            if (desired_turn < current_turn):
                output_turn = current_turn - self.max_turn_change

            if (desired_turn > current_turn):
                output_turn = current_turn + self.max_turn_change
        else :
            output_turn = desired_turn
        
        # Limit turn to the max turn
        if (output_turn > self.max_turn):
            output_turn = self.max_turn

        if (output_turn < -self.max_turn):
            output_turn = -self.max_turn

        #print ("Filtered turn from %d to %d",(desired_turn, output_turn))

        return output_turn
