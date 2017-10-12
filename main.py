import sys
import _thread
import threading
import socketserver
import binascii
import json
import time
import errno
import select
from PyQt4.QtGui import QApplication, QMainWindow
from PyQt4 import QtCore,QtGui
from bluetooth import *

from core.ui import Ui_MainWindow, Ui_CV
from core import *
from display import projector

def bt_send():
    """
    Send outgoing messages to cars
    """
    readSocket = False
    
    while common.bt_running:
        for vehicle in common.vehicles:
            try:
                can_read, can_write, has_error = select.select([], [vehicle.socket], [], 0)
                if vehicle.socket in can_write:
                    try:
                        item = vehicle.out_dict.popitem()
                    except KeyError:
                        # Dictionary is empty, do nothing
                        pass
                    else:
                        # Send command
                        vehicle.socket.send(item[0])
                        
                        # Calculate and print total system delay
                        millis = int(round(time.time()*1000))
                        print("System Delay: %d ms" % (millis - item[1]))

                        # TODO log delays to file for analysis
                
            except (BluetoothError, OSError, ValueError) as e:
                print(e)
                vehicle.socket.close()
                common.vehicle.remove(vehicle)

        # Sleep is essential otherwise all system resources are taken and total system delay skyrockets
        time.sleep(common.bt_loop_sleep/1000);

                
class service(socketserver.BaseRequestHandler):
    def handle(self):
        while 1:
            self.data = self.request.recv(1024)

            print('Handling request')
            if not (self.data):
                break

            self.data = self.data.strip()

            readJSON(self.data)
        self.request.close()
def readJSON(data):

    referenceTime = 0

    # Decode jsondata into k-v pairs
    datastr = data.decode('utf-8')
    datastr = "{" + find_between_r(datastr,"{","}") + "}"
    #print(datastr)
    cv_json = json.loads(datastr)
    
    # Precepts for the cars - at the moment this is everything visible
    vision_objects = []
    
    # For loop on each k-v pair in the json
    for key, value in cv_json.items():
        if(key != "time"):
            vis_obj = Vision_Object.Vision_Object(key, value)
            vision_objects.append(vis_obj)
        elif (key == "time"):
            referenceTime = value
    
    # For each car in our list
    for vehicle in common.vehicles:
        # Check if we received CV data
        if vehicle.address in cv_json:
            
            # Set last seen time in car object
            vehicle.updatePreceptTime(referenceTime)
            
            # Create vision object from json
            vis_obj = Vision_Object.Vision_Object(vehicle.address, cv_json[vehicle.address])

            # Update the corresponding car based on MAC
            vehicle.updateStateFromVisionObject(vis_obj)

            # Update corresponding car precepts
            vehicle.updatePrecepts(vision_objects, common.map_graph)
                                    
            # Vehicle agent to make decision based on updated vision        
            vehicle.decideAction()
        else:
            print("%s is lost." % vehicle.address)
    
    if(common.cvDataWindow):
        self.cvwindow.update()

def find_between_r( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""

def connectToVehicles():
    # Try connect to all of our cars
    print("Connecting to vehicles...")
    num_connected = 0
    for address in common.addresses:
        # Try to connect to each car three times
        for x in range(1,4):
            try:
                print("Connecting to %s (Attempt %d)" % (address, x))
                socket = BluetoothSocket(RFCOMM)
                socket.connect((address, 1))
                print("Connected to %s" % address)
                # TODO: Read "Human" and "Car" values from config file
                common.vehicles.append(Vehicle.Vehicle(address, socket, "Human", "Car"))
                num_connected += 1
                break # Connected, so break out of inner for loop
            except (BluetoothError, OSError) as e:
                print("Could not connect to %s because %s" % (address, e))

    return num_connected

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def main():
    # Load config
    load_config.load_vehicles()
    load_config.load_map_data()
    
    # Connect to Zenwheels vehicles
    num_connected = connectToVehicles()

    # Start projection
    print("Starting projection")
    projector.start_projection()

    # Quit if we did not find any vehicles
    if(num_connected == 0):
        print("No vehicles connected, shutting down...")
        sys.exit(0)
    
    # Start communication threads
    print("Starting communication thread")
    t_process = threading.Thread(target=bt_send)
    t_process.daemon = True
    t_process.start()
        
    # Main loop
    print("Start server...")
    t = ThreadedTCPServer(('localhost',1520), service)
    server_thread = threading.Thread(target=t.serve_forever())
    server_thread.daemon = True
    server_thread.start()
    #t.serve_forever()

    # Cleanup sockets
    print('Shutting down...')
    common.bt_running = False
    t_process.join()
    for vehicle in common.vehicles:
        vehicle.socket.close()
    print('Exiting...')

    # Stop projector
    #time.sleep(1)
    #projector.stop_projection()

    sys.exit(result)

if __name__ == '__main__':
    main()
