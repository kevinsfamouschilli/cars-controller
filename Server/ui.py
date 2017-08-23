# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Car.ui'
#
# Created: Sun Jul  7 13:35:01 2013
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
import time
import random
import common

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_CV(QtGui.QWidget):

    def __init__(self):
        super(Ui_CV, self).__init__()        
        self.initUI()
        
    def initUI(self):
        
        self.pens = {}
        
        self.initialisePens()
        
        self.setGeometry(300, 300, 1200, 900)
        self.setWindowTitle('Computer Vision Display')
        self.show()

    def initialisePens(self):
        pen = QtGui.QPen()
        pen.setWidth(8)
        pen.setColor(QtGui.QColor(255,0,0,255))
        self.pens["CAR_POSITION"] = pen

        pen = QtGui.QPen()
        pen.setWidth(5)
        pen.setColor(QtGui.QColor(0,0,0,255))
        self.pens["TARGET_POSITION"] = pen

        pen = QtGui.QPen()
        pen.setWidth(1)
        pen.setColor(QtGui.QColor(0,0,0,255))
        self.pens["CAR_TO_TARGET_LINE"] = pen
        
    def paintEvent(self, e):
       # self.drawVisionObjects()
        self.drawCars()

    def drawCars(self):

        qp = QtGui.QPainter()
        qp.begin(self)

        for car in common.cars:
            # Draw current position
            qp.setPen(self.pens["CAR_POSITION"])  
            qp.drawPoint(car.X_Pos, car.Y_Pos)

            # Draw line between current and target
            qp.setPen(self.pens["CAR_TO_TARGET_LINE"])
            qp.drawLine(QtCore.QLineF(car.X_Pos, car.Y_Pos,car.targets[car.currentTarget][0], car.targets[car.currentTarget][1]))
            
            # Draw target position
            qp.setPen(self.pens["TARGET_POSITION"])  
            qp.drawPoint(car.targets[car.currentTarget][0], car.targets[car.currentTarget][1])
        qp.end()
        
    def drawVisionObjects(self):
        qp = QtGui.QPainter()
        qp.begin(self)
        
        qp.setPen(self.pens["CAR_POSITION"])
        
        for vis_obj in vision_objects:
            if (vis_obj.Object_Type != 1): #dont draw cars
                qp.drawPoint(vis_obj.X_Pos, vis_obj.Y_Pos)
        qp.end()
        
class Ui_MainWindow(object):
    def setupUi(self, MainWindow, length):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(300, 300) #Width and height of the window
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))

        self.connectPB = QtGui.QPushButton(self.centralwidget)
        self.connectPB.setGeometry(QtCore.QRect(15, 15, 75, 25))
        self.connectPB.setObjectName(_fromUtf8("connectPB"))
        
        self.CarTest = QtGui.QPushButton(self.centralwidget)
        self.CarTest.setGeometry(QtCore.QRect(105, 15, 90, 25))
        self.CarTest.setObjectName(_fromUtf8("CarTest"))
        
        self.quitPB = QtGui.QPushButton(self.centralwidget)
        self.quitPB.setGeometry(QtCore.QRect(210, 15, 75, 25))
        self.quitPB.setObjectName(_fromUtf8("quitPB"))


        self.lineEdit = QtGui.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(15, 55, 270, 25))
        self.lineEdit.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))


        self.RunPB = QtGui.QPushButton(self.centralwidget)
        self.RunPB.setGeometry(QtCore.QRect(15, 95, 75, 25))
        self.RunPB.setObjectName(_fromUtf8("RunPB"))

        self.StopPB = QtGui.QPushButton(self.centralwidget)
        self.StopPB.setGeometry(QtCore.QRect(15, 135, 75, 25))
        self.StopPB.setObjectName(_fromUtf8("StopPB"))


        self.CarSwitch = QtGui.QPushButton(self.centralwidget)
        self.CarSwitch.setGeometry(QtCore.QRect(210, 95, 75, 25))
        self.CarSwitch.setObjectName(_fromUtf8("CarSwitch"))

        self.CarAll = QtGui.QPushButton(self.centralwidget)
        self.CarAll.setGeometry(QtCore.QRect(210, 135, 75, 25))
        self.CarAll.setObjectName(_fromUtf8("CarAll"))

        
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        


        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.MainWindow=MainWindow
            
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Zen Wheels", None))
        self.connectPB.setText(_translate("MainWindow", "Connect", None))
        self.quitPB.setText(_translate("MainWindow", "Quit", None))
        self.RunPB.setText(_translate("MainWindow", "Run", None))
        self.StopPB.setText(_translate("MainWindow", "Stop", None))
        self.CarSwitch.setText(_translate("MainWindow", "Switch Car", None))
        self.CarAll.setText(_translate("MainWindow", "Control All", None))
        self.CarTest.setText(_translate("MainWindow", "Test Connection", None))
    
        

