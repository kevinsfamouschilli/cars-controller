import csv
import os.path
import common

# Load vehicles CSV file
def load_vehicles():
    reader = csv.reader(open("../config/vehicles.csv", 'rt'), dialect='excel')
    iterator = iter(reader)
    next(iterator) # Skip header row
    for row in iterator:
        #row[0]: MAC_Address
        #row[1]: Bluetooth_SSID
        #row[2]: Description
        #row[3]: Agent_Type
        #row[4]: Vehicle_Type
        #row[5]: Enable (Y/N)

        if(row[5] == "Y"):
            # Add each enabled car to list of cars we try to connect to
            common.addresses.append(row[0])

# Load environment map data CSV File
def load_map_data():
    reader = csv.reader(open("../config/map_data.csv", 'rt'), dialect='excel')
    iterator = iter(reader)
    next(iterator) # Skip header row
    for row in iterator:
        
        #row[0]: NODE_ID
        #row[1]: TYPE
        #row[2]: X
        #row[3]: Y
        #row[4]: GOES_TO_1
        #row[5]: Enable (Y/N)
        
        # TODO: Populate NetworkX graph here
        pass;
