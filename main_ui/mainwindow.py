# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1132, 688)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.hlMainSections = QtGui.QHBoxLayout()
        self.hlMainSections.setSpacing(0)
        self.hlMainSections.setObjectName(_fromUtf8("hlMainSections"))
        self.vlUISelect = QtGui.QVBoxLayout()
        self.vlUISelect.setSpacing(0)
        self.vlUISelect.setObjectName(_fromUtf8("vlUISelect"))
        self.leInformation = QtGui.QLineEdit(self.centralwidget)
        self.leInformation.setReadOnly(True)
        self.leInformation.setObjectName(_fromUtf8("leInformation"))
        self.vlUISelect.addWidget(self.leInformation)
        self.listInformation = QtGui.QListWidget(self.centralwidget)
        self.listInformation.setObjectName(_fromUtf8("listInformation"))
        item = QtGui.QListWidgetItem()
        self.listInformation.addItem(item)
        item = QtGui.QListWidgetItem()
        self.listInformation.addItem(item)
        item = QtGui.QListWidgetItem()
        self.listInformation.addItem(item)
        item = QtGui.QListWidgetItem()
        self.listInformation.addItem(item)
        item = QtGui.QListWidgetItem()
        self.listInformation.addItem(item)
        item = QtGui.QListWidgetItem()
        self.listInformation.addItem(item)
        item = QtGui.QListWidgetItem()
        self.listInformation.addItem(item)
        self.vlUISelect.addWidget(self.listInformation)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.vlUISelect.addItem(spacerItem)
        self.vlUISelect.setStretch(0, 1)
        self.vlUISelect.setStretch(1, 7)
        self.vlUISelect.setStretch(2, 27)
        self.hlMainSections.addLayout(self.vlUISelect)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.hlMainSections.addItem(spacerItem1)
        self.hlUIpane = QtGui.QHBoxLayout()
        self.hlUIpane.setObjectName(_fromUtf8("hlUIpane"))
        self.swPages = QtGui.QStackedWidget(self.centralwidget)
        self.swPages.setFrameShape(QtGui.QFrame.Box)
        self.swPages.setObjectName(_fromUtf8("swPages"))
        self.hlUIpane.addWidget(self.swPages)
        self.hlMainSections.addLayout(self.hlUIpane)
        self.hlMainSections.setStretch(0, 8)
        self.hlMainSections.setStretch(1, 1)
        self.hlMainSections.setStretch(2, 22)
        self.gridLayout.addLayout(self.hlMainSections, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1132, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.listInformation.setCurrentRow(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.leInformation.setText(_translate("MainWindow", "Information", None))
        __sortingEnabled = self.listInformation.isSortingEnabled()
        self.listInformation.setSortingEnabled(False)
        item = self.listInformation.item(0)
        item.setText(_translate("MainWindow", "modules", None))
        item = self.listInformation.item(1)
        item.setText(_translate("MainWindow", "baseplates", None))
        item = self.listInformation.item(2)
        item.setText(_translate("MainWindow", "sensors", None))
        item = self.listInformation.item(3)
        item.setText(_translate("MainWindow", "PCBs", None))
        item = self.listInformation.item(4)
        item.setText(_translate("MainWindow", "assembly steps", None))
        item = self.listInformation.item(5)
        item.setText(_translate("MainWindow", "supplies", None))
        item = self.listInformation.item(6)
        item.setText(_translate("MainWindow", "equipment", None))
        self.listInformation.setSortingEnabled(__sortingEnabled)

