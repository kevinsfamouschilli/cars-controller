class Vision_Object:
    def __init__(self, key, values):
        self.MAC_Address = key
        self.Object_Type = values[0]        
        self.X_Pos = values[1]
        self.Y_Pos = values[2]        
        self.X_Vel = values[3]
        self.Y_Vel = values[4]
        self.Orientation = values[5]
        
        # Two spare fields which are currently unused:
        # self.spare1 = values[6]
        # self.spare2 = values[7]
