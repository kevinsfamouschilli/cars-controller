#0a - Read/write json from file
#0b - Attempt multithreading with sockets
#0c - Attempt keeping socket open in handler

#! /usr/bin/python
import sys
import _thread
import threading
import socketserver
from bluetooth import *
import binascii
import json
from PyQt4.QtGui import QApplication, QMainWindow
from PyQt4 import QtCore,QtGui
from ui import Ui_MainWindow
from time import *

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
        while 1:
            self.data = self.request.recv(1024)
            if not self.data:
                break
            print('Handling request')
            self.data = self.data.strip()
            self.server.signal.emit(self.data)
        print('Closing socket...')
        self.request.close()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class MainWindow(QMainWindow):
    def __init__(self):
      
        QMainWindow.__init__(self)

        # Dictionary for storing cars indexed by MAC address
        self.cars = {}

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
        self.ui.connectPB.clicked.connect(self.tryToConnect)
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

    #The command for the quit button
    def quit(self):
        try:
            self.sock.close()
        except: AttributeError
        sys.exit()

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

    def tryToConnect(self):
        _thread.start_new_thread(self.updateText,())
        _thread.start_new_thread(self.connect,())

    def updateText(self):
        self.ui.lineEdit.setText("Searching all nearby bluetooth devices")

    def connect(self): 
        addr = None
        length = len(self.listcars)

        uuid = '00001101-0000-1000-8000-00805F9B34FB'
        service_matches = find_service( uuid = uuid, address = addr )

        if len(service_matches) == 0:
            self.ui.lineEdit.setText("Could not find device")
            return

        first_match = service_matches[0]
        port = first_match["port"]
        name = first_match["name"]
        host = first_match["host"]
        print(port, name, host)
        
        newcar = car(host, port, self.listcars)

        # Add the new car to our dictionary of cars
        self.cars[host]= newcar
        
        self.listcars.append(newcar)
        print("New car added")
        self.ui.lineEdit.setText("Connection established.")
        length=len(self.listcars)
        print(self.listcars)
        
    def start_server(self):
        self.threads = []
        server = ServerThread()
        server.json_received.connect(self.readJSON)
        self.threads.append(server)
        server.start()
        
    def readJSON(self,data):
        cv_json = json.loads(data.decode('utf-8'))
        #print ('received: ' + cv_json + '\n')
        
        # Just reading json from static file for now...
        #with open('output.json') as json_data:
            #cv_json = json.load(json_data)
            #print(cv_json)

        # For loop on each k-v pair in the json
        for key, value in cv_json.items():
            # Initialise a vision object
            print(value)
            vis_obj = vision_object(key, value)

            # If the object is a car
            if vis_obj.Object_Type == 1:

                # If car exists in dictionary
                if vis_obj.MAC_Address in self.cars:                        
                    # update the corresponding car based on MAC
                    self.cars[vis_obj.MAC_Address].updateStateFromVisionObject(vis_obj)

                    # Cars to make decisions based on updated vision        
                    self.cars[vis_obj.MAC_Address].decideAction()
                else :
                    print("Car " + vis_obj.MAC_Address + " not in dictionary of cars.")

class vision_object:
    def __init__(self, key, values):
        self.MAC_Address = key
        self.Object_Type = values[0]
        self.Orientation = values[1]
        self.X_Pos = values[2]
        self.Y_Pos = values[3]        
        self.X_Vel = values[4]
        self.Y_Vel = values[5]
        
        # Two spare fields which are currently unused:
        # self.spare1 = values[6]
        # self.spare2 = values[7]

#An object of the car class controls a specific car
#By calling functions within this class commands are sent to the car
class car:
    def __init__(self, host, port, listcars):

        # The unique identifier for this car
        self.MAC_Address = host

        # Observed parameters of the car
        self.Orientation = 0
        self.X_Pos = 0
        self.Y_Pos = 0      
        self.X_Vel = 0
        self.Y_Vel = 0
        
        self.action_dict = {'horn' : 0, 'lights' : 0, 'fault' : 0,}
        self.acceleration = 0
        self.steering = 0
        # List of available commands
        self.dict = {}
        self.dict['HORN_OFF'] = '8600'
        self.dict['HORN_ON'] = '8601'
        self.dict['LIGHTS_OFF'] = '8500'
        self.dict['LIGHTS_SOFT'] = '8501'
        self.dict['LIGHTS'] = '8502'
        self.dict['FAULT'] = ['8304',' 8404',' 8301',' 8401']
        self.dict['FAULT_OFF'] = ['8300',' 8400']
        self.dict['STEER_LEFT']=['817F','817E','817D','817C','817B','817A','8179','8178','8177','8176','8175','8174','8173','8172','8171','8170','816F','816E','816D','816C','816B','816A','8169','8168','8167','8166','8165','8164','8163','8162','8161','8160','815F','815E','815D','815C','815B','815A','8159','8158','8157','8156','8155','8154','8153','8152','8151','8150','814F','814E','814D','814C','814B','814A','8149','8148','8147','8146','8145','8144','8143','8142','8141']
        self.dict['STEER_RIGHT']=['8100','8101','8102','8103','8104','8105','8106','8107','8108','8109','810A','810B','810C','810D','810E','810F','8110','8111','8112','8113','8114','8115','8116','8117','8118','8119','811A','811B','811C','811D','811E','811F','8120','8121','8122','8123','8124','8125','8126','8127','8128','8129','812A','812B','812C','812D','812E','812F','8130','8131','8132','8133','8134','8135','8136','8137','8138','8139','813A','813B','813C','813D','813E','813F']
        self.dict['SPEED_BACK']=['827F','827E','827D','827C','827B','827A','8279','8278','8277','8276','8275','8274','8273','8272','8271','8270','826F','826E','826D','826C','826B','826A','8269','8268','8267','8266','8265','8264','8263','8262','8261','8260','825F','825E','825D','825C','825B','825A','8259','8258','8257','8256','8255','8254','8253','8252','8251','8250','824F','824E','824D','824C','824B','824A','8249','8248','8247','8246','8245','8244','8243','8242','8241']
        self.dict['SPEED_FRONT']=['8200','8201','8202','8203','8204','8205','8206','8207','8208','8209','820A','820B','820C','820D','820E','820F','8210','8211','8212','8213','8214','8215','8216','8217','8218','8219','821A','821B','821C','821D','821E','821F','8220','8221','8222','8223','8224','8225','8226','8227','8228','8229','822A','822B','822C','822D','822E','822F','8230','8231','8232','8233','8234','8235','8236','8237','8238','8239','823A','823B','823C','823D','823E','823F']
        self.dict['NO_SPEED']='8200'
        self.dict['NO_STEER'] = '8100'
        
        # Create the client socket
        self.sock=BluetoothSocket( RFCOMM )
        self.sock.connect((host, port))
        
        length = len(listcars)
        
    def updateStateFromVisionObject(self,stateVariables):
        self.Orientation = stateVariables.Orientation
        self.X_Pos = stateVariables.X_Pos
        self.Y_Pos = stateVariables.Y_Pos      
        self.X_Vel = stateVariables.X_Vel
        self.Y_Vel = stateVariables.Y_Vel
        
    def decideAction(self):
        border = 100;
        x_max = 1200 - border;
        x_min = 0 + border;
        y_max = 900 - border;
        y_min = 0 + border;
        
        # whilst in bounds, drive at constant speed
        if self.X_Pos > x_min and self.X_Pos < x_max and self.Y_Pos > y_min and self.Y_Pos < y_max:
            print("Car in bounds... driving")
            self.run()
        else:
            # if out of bounds, then stop
            print("X_Pos %d, X_Min %d, X_Max %d, Y_Pos %d, Y_Min %d, Y_Max %d" % (self.X_Pos,x_min,x_max,self.Y_Pos,y_min,y_max))
            print("Car out of bounds... stopping.")
            self.stop()

    def horn(self):
        self.sock.send(binascii.a2b_hex(self.dict['HORN_ON']))
        sleep(0.5)
        self.sock.send(binascii.a2b_hex(self.dict['HORN_OFF']))
        
    def LightsOn(self):
        self.sock.send(binascii.a2b_hex(self.dict['LIGHTS']))
        
    def LightsOff(self):
        self.sock.send(binascii.a2b_hex(self.dict['LIGHTS_OFF']))

    def run(self):
        self.acceleration=20
        self.sock.send(binascii.a2b_hex(self.dict['SPEED_FRONT'][self.acceleration]))
        self.sock.send(binascii.a2b_hex(self.dict['HORN_ON']))
        sleep(0.5)
        self.sock.send(binascii.a2b_hex(self.dict['HORN_OFF']))
        
    def stop(self):
        self.acceleration=0
        self.sock.send(binascii.a2b_hex(self.dict['NO_SPEED']))

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())  

if __name__ == '__main__':
    main()
