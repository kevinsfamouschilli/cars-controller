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
import core.load_config as load_config
import core.common as common
import core.car as car
import core.vision_object as vision_object

def bt_send():
    """
    Send outgoing messages to cars
    """
    readSocket = False
    
    while common.bt_running:
        for car in common.cars:
            try:
                can_read, can_write, has_error = select.select([], [car.socket], [], 0)
                if car.socket in can_write:
                    try:
                        item = car.out_dict.popitem()
                    except KeyError:
                        # Dictionary is empty, do nothing
                        pass
                    else:
                        # Send command
                        car.socket.send(item[0])
                        
                        # Calculate and print total system delay
                        millis = int(round(time.time()*1000))
                        print("System Delay: %d ms" % (millis - item[1]))

                        # TODO log delays to file for analysis
                
            except (BluetoothError, OSError, ValueError) as e:
                print(e)
                car.socket.close()
                common.cars.remove(car)

        # Sleep is essential otherwise all system resources are taken and total system delay skyrockets
        time.sleep(common.bt_loop_sleep/1000);

class ServerThread(QtCore.QThread):
    json_received = QtCore.pyqtSignal(object)

    def __init__(self):
        QtCore.QThread.__init__(self)
        
    def run(self):       
        t = ThreadedTCPServer(('localhost',1520), service)
        t.signal = self.json_received
        t.serve_forever()
        
class service(socketserver.BaseRequestHandler):
    
    def handle(self):
        print('\nComputer vision starting...\n')
        common.cv_running = True
        while 1:
            self.data = self.request.recv(1024)
            if not self.data:
                break            
            self.data = self.data.strip()                
            self.server.signal.emit(self.data)

        commoncv_running = False
        print('\nComputer vision stopped\n')
        self.request.close()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # Start window which visualises the CV data
        if (common.cvDataWindow):
            self.cvwindow = Ui_CV()
            self.cvwindow.show()

        # Start control UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #Button Controls:
        self.ui.quitPB.clicked.connect(self.quit)
        
        # Start the threaded socket server
        self.start_server()
            
    #The command for the quit button
    def quit(self):
        common.bt_running = False

    def start_server(self):
        self.threads = []
        server = ServerThread()
        server.json_received.connect(self.readJSON)
        self.threads.append(server)
        server.start()
        common.cv_running = False
        
    def readJSON(self,data):

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
                vis_obj = vision_object.Vision_Object(key, value)
                vision_objects.append(vis_obj)
            elif (key == "time"):
                referenceTime = value
        
        # For each car in our list
        for car in common.cars:
            # Check if we received CV data
            if car.address in cv_json:
                
                # Set last seen time in car object
                car.updatePreceptTime(referenceTime)
                
                # Create vision object from json
                vis_obj = vision_object.Vision_Object(car.address, cv_json[car.address])

                # Update the corresponding car based on MAC
                car.updateStateFromVisionObject(vis_obj)

                # Update corresponding car precepts
                car.updatePrecepts(vision_objects)
                                        
                # Make decision based on updated vision        
                car.decideAction()
            else:
                print("%s is lost." % car.address)
        
        if(common.cvDataWindow):
            self.cvwindow.update()

def find_between_r( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""

def connectToCars():
    # Try connect to all of our cars
    print("Connecting to cars...")
    num_connected = 0
    for address in common.addresses:
        try:
            socket = BluetoothSocket(RFCOMM)
            socket.connect((address, 1))
            print("Connected to %s" % address)
            common.cars.append(car.Car(address, socket))
            num_connected += 1
        except (BluetoothError, OSError) as e:
            print("Could not connect to %s because %s" % (address, e))

    return num_connected

def main():
    # Load config
    load_config.load_vehicles()
    load_config.load_map_data()
    
    # Connect to cars
    num_connected = connectToCars()

    # Quit if we did not find any cars
    if(num_connected == 0):
        print("No cars connected, shutting down...")
        sys.exit(0)
    
    # Start communication threads
    t_process = threading.Thread(target=bt_send)
    t_process.daemon = True
    t_process.start()
        
    # Main loop
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()  
    result = app.exec_()

    # Cleanup sockets
    print('Shutting down...')
    common.bt_running = False
    t_process.join()
    for car in common.cars:
        car.socket.close()
    print('Exiting...')

    sys.exit(result)

if __name__ == '__main__':
    main()
