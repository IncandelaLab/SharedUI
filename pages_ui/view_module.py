# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'view_module.ui'
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

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(874, 594)
        self.lineEdit = QtGui.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(10, 10, 71, 21))
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.sbModuleID = QtGui.QSpinBox(Form)
        self.sbModuleID.setGeometry(QtCore.QRect(80, 10, 91, 21))
        self.sbModuleID.setMaximum(65536)
        self.sbModuleID.setProperty("value", 0)
        self.sbModuleID.setObjectName(_fromUtf8("sbModuleID"))
        self.lineEdit_2 = QtGui.QLineEdit(Form)
        self.lineEdit_2.setGeometry(QtCore.QRect(10, 30, 71, 21))
        self.lineEdit_2.setReadOnly(True)
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.lineEdit_3 = QtGui.QLineEdit(Form)
        self.lineEdit_3.setGeometry(QtCore.QRect(10, 50, 71, 21))
        self.lineEdit_3.setReadOnly(True)
        self.lineEdit_3.setObjectName(_fromUtf8("lineEdit_3"))
        self.lineEdit_4 = QtGui.QLineEdit(Form)
        self.lineEdit_4.setGeometry(QtCore.QRect(10, 70, 71, 21))
        self.lineEdit_4.setReadOnly(True)
        self.lineEdit_4.setObjectName(_fromUtf8("lineEdit_4"))
        self.leBaseplateID = QtGui.QLineEdit(Form)
        self.leBaseplateID.setGeometry(QtCore.QRect(80, 30, 51, 21))
        self.leBaseplateID.setReadOnly(True)
        self.leBaseplateID.setObjectName(_fromUtf8("leBaseplateID"))
        self.leSensorID = QtGui.QLineEdit(Form)
        self.leSensorID.setGeometry(QtCore.QRect(80, 50, 51, 21))
        self.leSensorID.setReadOnly(True)
        self.leSensorID.setObjectName(_fromUtf8("leSensorID"))
        self.lePCBID = QtGui.QLineEdit(Form)
        self.lePCBID.setGeometry(QtCore.QRect(80, 70, 51, 21))
        self.lePCBID.setReadOnly(True)
        self.lePCBID.setObjectName(_fromUtf8("lePCBID"))
        self.pbGoBaseplate = QtGui.QPushButton(Form)
        self.pbGoBaseplate.setGeometry(QtCore.QRect(130, 30, 41, 21))
        self.pbGoBaseplate.setObjectName(_fromUtf8("pbGoBaseplate"))
        self.pbGoSensor = QtGui.QPushButton(Form)
        self.pbGoSensor.setGeometry(QtCore.QRect(130, 50, 41, 21))
        self.pbGoSensor.setObjectName(_fromUtf8("pbGoSensor"))
        self.pbGoPCB = QtGui.QPushButton(Form)
        self.pbGoPCB.setGeometry(QtCore.QRect(130, 70, 41, 21))
        self.pbGoPCB.setObjectName(_fromUtf8("pbGoPCB"))
        self.lineEdit_5 = QtGui.QLineEdit(Form)
        self.lineEdit_5.setGeometry(QtCore.QRect(10, 100, 71, 21))
        self.lineEdit_5.setReadOnly(True)
        self.lineEdit_5.setObjectName(_fromUtf8("lineEdit_5"))
        self.leThickness = QtGui.QLineEdit(Form)
        self.leThickness.setGeometry(QtCore.QRect(80, 100, 91, 21))
        self.leThickness.setReadOnly(True)
        self.leThickness.setObjectName(_fromUtf8("leThickness"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.lineEdit.setText(_translate("Form", "Module ID", None))
        self.lineEdit_2.setText(_translate("Form", "Baseplate ID", None))
        self.lineEdit_3.setText(_translate("Form", "Sensor ID", None))
        self.lineEdit_4.setText(_translate("Form", "PCB ID", None))
        self.pbGoBaseplate.setText(_translate("Form", "Go to", None))
        self.pbGoSensor.setText(_translate("Form", "Go to", None))
        self.pbGoPCB.setText(_translate("Form", "Go to", None))
        self.lineEdit_5.setText(_translate("Form", "Thickness", None))

