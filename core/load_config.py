import csv
import os.path
import core.common as common
import networkx as nx

# Load vehicles CSV file
def load_vehicles():
    reader = csv.reader(open("./config/vehicles.csv", 'rt'), dialect='excel')
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
    
    # Create graph
    map_graph = nx.DiGraph()

    # Load file
    reader = csv.reader(open("./config/map_data.csv", 'rt'), dialect='excel')

     # Skip header row
    iterator = iter(reader)
    next(iterator)

    # Create graph from map data rows
    for row in iterator:
        
        # Create node
        map_graph.add_node(row[0], node_id=row[0],node_type=row[1],x=row[2], y=row[3])

        # Add edges (GOES_TO_1,..,GOES_TO_10)
        for col in range(4,13):
            if(row[col]):
                map_graph.add_edge(row[0],row[col])

    # Save to the global variable
    common.map_graph = map_graph
