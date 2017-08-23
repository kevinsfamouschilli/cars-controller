import sys
import _thread
import threading
import socketserver
from bluetooth import *
from protocol import *
import binascii
import json
from PyQt4.QtGui import QApplication, QMainWindow
from PyQt4 import QtCore,QtGui
import queue
from ui import Ui_MainWindow, Ui_CV
import time
import math
import common
import errno
import select
from timer import Timer

# Use to debug without needing real cars connected
cvDataWindow = False

# List of MAC addresses to automatically connect to
addresses = [
  '00:06:66:61:A9:59',  # MicroCar-89 (Orange)
  #'00:06:66:61:A3:48'   # MicroCar-72 (Red)
]

# Whether the communication threads are running
bt_running = True

# Whether or not the CV is connected to the socket and providing data
cv_running = False

def process():
    """
    Send outgoing messages to cars
    """
    readSocket = False
    
    while bt_running:
        for car in common.cars:
            try:
                can_read, can_write, has_error = select.select([], [car.socket], [], 0)
                if car.socket in can_write:
                    try:
                        item = car.out_queue.get(False)
                    except queue.Empty:
                        pass
                    else:
                        car.socket.send(item[1])
                        millis = int(round(time.time()*1000))
                        print("System Delay: %d ms" % (millis - item[0]))
                
            except (BluetoothError, OSError, ValueError) as e:
                print(e)
                car.socket.close()
                common.cars.remove(car)

        # Sleep is essential otherwise all system resources are taken and total system delay skyrockets
        time.sleep(0.05);

class ServerThread(QtCore.QThread):
    json_received = QtCore.pyqtSignal(object)

    def __init__(self):
        QtCore.QThread.__init__(self)
        
    def run(self):       
        t = ThreadedTCPServer(('localhost',1520), service)
        t.signal = self.json_received
        t.serve_forever()
        
class service(socketserver.BaseRequestHandler):
    
    global cv_running
    
    def handle(self):
        cv_running = True
        while 1:
            self.data = self.request.recv(1024)
            if not self.data:
                break            
            self.data = self.data.strip()                
            self.server.signal.emit(self.data)

        cv_running = False
        print('Closing socket\n')
        self.request.close()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # Start window which visualises the CV data
        if (cvDataWindow):
            self.cvwindow = Ui_CV()
            self.cvwindow.show()

        # (Legacy) A list of all the car objects that are currently connected
        self.listcars = []
        
        #Which car from the list is currently being controlled
        self.carindex = 0
        
        #the number of cars currently connected
        length = len(self.listcars)
        
        #The control state is whether all cars are being controlled (1) or only a single car(0)
        self.ControlState=0
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self, length)

        #Button Controls:
        #For example: connectPB is the name of a button created in the UI
        #self.tryToConnect is the function that happens when connectPB is pressed
        #self.ui.connectPB.clicked.connect(self.tryToConnect)
        self.ui.quitPB.clicked.connect(self.quit)
        self.ui.RunPB.clicked.connect(self.Run) 
        self.ui.StopPB.clicked.connect(self.Stop)
        self.ui.CarSwitch.clicked.connect(self.carSwitch)
        self.ui.CarAll.clicked.connect(self.AllCars)
        self.ui.CarTest.clicked.connect(self.TestAll)
        
        # Start the threaded socket server
        self.start_server()
    
    #This cycles through the connected cars, changing which one is being controlled
    #It flashes the lights of the current car
    #It also sets the control state to a single car
    def carSwitch(self):
        self.carindex = (self.carindex + 1)%len(self.listcars)
        i = self.listcars[self.carindex]
        i.LightsOn()
        sleep(0.75)
        i.LightsOff()
        self.ControlState=0

    #Sets the control state all of the cars
    def AllCars(self):
        for x in self.listcars:
            x.LightsOn()
        sleep(1)
        for x in self.listcars:
            x.LightsOff()
        self.ControlState=1

    #Flashes the lights of all connected cars
    def TestAll(self):
        for x in self.listcars:
            x.LightsOn()
        sleep(1)
        for x in self.listcars:
            x.LightsOff()
            
  # Todo: fix this
    #The command for the quit button
    def quit(self):
        global running
        running = False

    #Drives one or all cars forward        
    def Run(self):
        if self.ControlState:
            for i in self.listcars:
                i.run()
        else:
            i = self.listcars[self.carindex]
            i.run()

    #Stops one or all cars
    def Stop(self):
        if self.ControlState:
            for i in self.listcars:
                i.stop()
        else:
            i = self.listcars[self.carindex]
            i.stop()

    def start_server(self):
        self.threads = []
        server = ServerThread()
        server.json_received.connect(self.readJSON)
        self.threads.append(server)
        server.start()
        
        global cv_running
        cv_running = True
        
    def readJSON(self,data):

        referenceTime = 0

        # Decode jsondata into k-v pairs
        datastr = data.decode('utf-8')
        datastr = "{" + find_between_r(datastr,"{","}") + "}"
        cv_json = json.loads(datastr)
        
        # Precepts for the cars - at the moment this is everything visible
        vision_objects = []
        
        # For loop on each k-v pair in the json
        for key, value in cv_json.items():
            if(key != "time"):
                vis_obj = vision_object(key, value)
                vision_objects.append(vis_obj)
            elif (key == "time"):
                #millis = int(round(time.time()*1000))
                referenceTime = value
                #print("Transmission Delay: %d ms" % (millis - value))
        
        # For each car in our list
        for car in common.cars:
            # Check if we received CV data
            if car.address in cv_json:

                car.updatePreceptTime(referenceTime)
                
                # Create vision object from json
                vis_obj = vision_object(car.address, cv_json[car.address])

                # Update the corresponding car based on MAC
                car.updateStateFromVisionObject(vis_obj)

                # Update corresponding car precepts
                car.updatePrecepts(vision_objects)
                                        
                # Make decision based on updated vision        
                car.decideAction()
            else:
                print("%s is lost." % car.address)
        
        if(cvDataWindow):     
            self.cvwindow.update()
        

def find_between_r( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""
    
class vision_object:
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
        self.out_queue = queue.Queue()

    # Queue given command with associated time
    def queueCommand(self, command):
        self.out_queue.put([self.preceptTime, command])

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

        # Can't do anything if we are too slow as the orientation value is incorrectly reported as zero
        if(self.calculateSpeed() < 25):
            return
        
        #print ('### START ORIENTATION CONTROL ###')
        
        errorAngle = ((((desiredOrientation - self.Orientation) % 360) + 540) % 360) - 180;
        #print ('Current: %d, Desired %d, errorAngle: %d' % (self.Orientation, desiredOrientation, errorAngle))
        sensitivity = 0.5
        self.steering = int(errorAngle * sensitivity)

        # Upper and lower bound the amount of steering
        maxSteering = 50
        if(self.steering > maxSteering):
            self.steering = maxSteering
        elif(self.steering < -maxSteering):
            self.steering = -maxSteering

        # Send steering command
        if self.steering != 0:
            #print ('Steering with intensity %d' % self.steering)
            self.queueCommand(bytes([STEERING, self.steering & 0x7f]))
        else:
            #print ('Steering STRAIGHT')
            self.queueCommand(bytes([STEERING, 0]))

    def checkCarAtTarget(self):        
        distanceToTarget = self.distance(self.X_Pos, self.Y_Pos,self.targets[self.currentTarget][0], self.targets[self.currentTarget][1])
        if(distanceToTarget < 75):
            self.currentTarget = (self.currentTarget + 1) % len(self.targets)
            #print("Car targetting (%d,%d)" % (self.targets[self.currentTarget][0], self.targets[self.currentTarget][1]))
        else:
            pass
            #print("Car targetting (%d,%d)" % (self.targets[self.currentTarget][0], self.targets[self.currentTarget][1]))

    def decideAction(self):        
        if (self.carIsWithinBounds() and self.carIsInFreeSpace()):
            #print("Car in bounds and free space... driving")

            self.acceleration=25
            self.queueCommand(bytes([THROTTLE, self.acceleration & 0x7f])) 

            self.checkCarAtTarget()            
            self.orientationControl(self.getOrientationToTarget())
        else:
            # Stop as car is out of bounds or is going to hit something
            #print("Car out of bounds or going to collide... stopping.")
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
        self.acceleration=20
        self.queueCommand(bytes([THROTTLE, self.acceleration & 0x7f]))
        
    def stop(self):
        self.acceleration=0
        self.queueCommand(bytes([THROTTLE, 0]))

def connectToCars():
    # Try connect to all of our cars
    print("Connecting to cars...")
    for address in addresses:
        try:
            socket = BluetoothSocket(RFCOMM)
            socket.connect((address, 1))
            print("Connected to %s" % address)
            common.cars.append(Car(address, socket))
        except (BluetoothError, OSError) as e:
            print("Could not connect to %s because %s" % (address, e))

def main():

    global bt_running
    
    # Connect to cars
    connectToCars()

    # Start communication threads
    t_process = threading.Thread(target=process)
    t_process.daemon = True
    t_process.start()
        
    # Main loop
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()  
    result = app.exec_()

    # Cleanup sockets
    print('Shutting down...')
    bt_running = False
    t_process.join()
    for car in common.cars:
        car.socket.close()
    print('Exiting...')

    sys.exit(result)

if __name__ == '__main__':
    main()
