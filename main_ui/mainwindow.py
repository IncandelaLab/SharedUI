# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../main_ui/mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1366, 858)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.hlMainSections = QtWidgets.QHBoxLayout()
        self.hlMainSections.setSpacing(0)
        self.hlMainSections.setObjectName("hlMainSections")
        self.vlUISelect = QtWidgets.QVBoxLayout()
        self.vlUISelect.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.vlUISelect.setSpacing(0)
        self.vlUISelect.setObjectName("vlUISelect")
        self.leInformation = QtWidgets.QLineEdit(self.centralwidget)
        self.leInformation.setReadOnly(True)
        self.leInformation.setObjectName("leInformation")
        self.vlUISelect.addWidget(self.leInformation)
        self.listInformation = QtWidgets.QListWidget(self.centralwidget)
        self.listInformation.setMinimumSize(QtCore.QSize(0, 155))
        self.listInformation.setObjectName("listInformation")
        item = QtWidgets.QListWidgetItem()
        self.listInformation.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listInformation.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listInformation.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listInformation.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listInformation.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listInformation.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listInformation.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listInformation.addItem(item)
        self.vlUISelect.addWidget(self.listInformation)
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.vlUISelect.addItem(spacerItem)
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName("lineEdit")
        self.vlUISelect.addWidget(self.lineEdit)
        self.listAssembly = QtWidgets.QListWidget(self.centralwidget)
        self.listAssembly.setObjectName("listAssembly")
        item = QtWidgets.QListWidgetItem()
        self.listAssembly.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listAssembly.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listAssembly.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listAssembly.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listAssembly.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listAssembly.addItem(item)
        self.vlUISelect.addWidget(self.listAssembly)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.vlUISelect.addItem(spacerItem1)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.vlUISelect.addWidget(self.lineEdit_2)
        self.listShippingAndReceiving = QtWidgets.QListWidget(self.centralwidget)
        self.listShippingAndReceiving.setObjectName("listShippingAndReceiving")
        item = QtWidgets.QListWidgetItem()
        self.listShippingAndReceiving.addItem(item)
        self.vlUISelect.addWidget(self.listShippingAndReceiving)
        spacerItem2 = QtWidgets.QSpacerItem(20, 25, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.vlUISelect.addItem(spacerItem2)
        self.pbUpload = QtWidgets.QPushButton(self.centralwidget)
        self.pbUpload.setEnabled(False)
        self.pbUpload.setObjectName("pbUpload")
        self.vlUISelect.addWidget(self.pbUpload)
        spacerItem3 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.vlUISelect.addItem(spacerItem3)
        self.vlUISelect.setStretch(0, 1)
        self.vlUISelect.setStretch(1, 6)
        self.vlUISelect.setStretch(2, 1)
        self.vlUISelect.setStretch(3, 1)
        self.vlUISelect.setStretch(4, 5)
        self.vlUISelect.setStretch(5, 1)
        self.vlUISelect.setStretch(6, 1)
        self.vlUISelect.setStretch(7, 2)
        self.vlUISelect.setStretch(10, 12)
        self.hlMainSections.addLayout(self.vlUISelect)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.hlMainSections.addItem(spacerItem4)
        self.hlUIpane = QtWidgets.QHBoxLayout()
        self.hlUIpane.setSpacing(0)
        self.hlUIpane.setObjectName("hlUIpane")
        self.swPages = QtWidgets.QStackedWidget(self.centralwidget)
        self.swPages.setFrameShape(QtWidgets.QFrame.Box)
        self.swPages.setObjectName("swPages")
        self.hlUIpane.addWidget(self.swPages)
        self.hlMainSections.addLayout(self.hlUIpane)
        self.hlMainSections.setStretch(0, 8)
        self.hlMainSections.setStretch(1, 1)
        self.hlMainSections.setStretch(2, 40)
        self.gridLayout.addLayout(self.hlMainSections, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1366, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.listInformation.setCurrentRow(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.leInformation.setText(_translate("MainWindow", "Parts, tooling, and supplies"))
        __sortingEnabled = self.listInformation.isSortingEnabled()
        self.listInformation.setSortingEnabled(False)
        item = self.listInformation.item(0)
        item.setText(_translate("MainWindow", "search for parts"))
        item = self.listInformation.item(1)
        item.setText(_translate("MainWindow", "baseplates"))
        item = self.listInformation.item(2)
        item.setText(_translate("MainWindow", "sensors"))
        item = self.listInformation.item(3)
        item.setText(_translate("MainWindow", "PCBs"))
        item = self.listInformation.item(4)
        item.setText(_translate("MainWindow", "protomodules"))
        item = self.listInformation.item(5)
        item.setText(_translate("MainWindow", "modules"))
        item = self.listInformation.item(6)
        item.setText(_translate("MainWindow", "tooling"))
        item = self.listInformation.item(7)
        item.setText(_translate("MainWindow", "supplies"))
        self.listInformation.setSortingEnabled(__sortingEnabled)
        self.lineEdit.setText(_translate("MainWindow", "Production steps and testing"))
        __sortingEnabled = self.listAssembly.isSortingEnabled()
        self.listAssembly.setSortingEnabled(False)
        item = self.listAssembly.item(0)
        item.setText(_translate("MainWindow", "kapton placement steps"))
        item = self.listAssembly.item(1)
        item.setText(_translate("MainWindow", "sensor placement steps"))
        item = self.listAssembly.item(2)
        item.setText(_translate("MainWindow", "PCB placement steps"))
        item = self.listAssembly.item(3)
        item.setText(_translate("MainWindow", "wirebonding and encapuslating"))
        item = self.listAssembly.item(4)
        item.setText(_translate("MainWindow", "unbiased DAQ"))
        item = self.listAssembly.item(5)
        item.setText(_translate("MainWindow", "IV curve"))
        self.listAssembly.setSortingEnabled(__sortingEnabled)
        self.lineEdit_2.setText(_translate("MainWindow", "Shipping and receiving"))
        __sortingEnabled = self.listShippingAndReceiving.isSortingEnabled()
        self.listShippingAndReceiving.setSortingEnabled(False)
        item = self.listShippingAndReceiving.item(0)
        item.setText(_translate("MainWindow", "shipments"))
        self.listShippingAndReceiving.setSortingEnabled(__sortingEnabled)
        self.pbUpload.setText(_translate("MainWindow", "Upload changes to database (WIP)"))

