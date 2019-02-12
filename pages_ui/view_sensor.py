# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'view_sensor.ui'
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
        Form.resize(1097, 705)
        self.lineEdit = QtGui.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(10, 10, 81, 21))
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.sbSensorID = QtGui.QSpinBox(Form)
        self.sbSensorID.setGeometry(QtCore.QRect(90, 10, 81, 21))
        self.sbSensorID.setMaximum(2147483647)
        self.sbSensorID.setObjectName(_fromUtf8("sbSensorID"))
        self.lineEdit_2 = QtGui.QLineEdit(Form)
        self.lineEdit_2.setGeometry(QtCore.QRect(10, 30, 81, 21))
        self.lineEdit_2.setReadOnly(True)
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.leIdentifier = QtGui.QLineEdit(Form)
        self.leIdentifier.setGeometry(QtCore.QRect(90, 30, 81, 21))
        self.leIdentifier.setText(_fromUtf8(""))
        self.leIdentifier.setReadOnly(True)
        self.leIdentifier.setObjectName(_fromUtf8("leIdentifier"))
        self.lineEdit_4 = QtGui.QLineEdit(Form)
        self.lineEdit_4.setGeometry(QtCore.QRect(10, 50, 81, 21))
        self.lineEdit_4.setReadOnly(True)
        self.lineEdit_4.setObjectName(_fromUtf8("lineEdit_4"))
        self.lineEdit_5 = QtGui.QLineEdit(Form)
        self.lineEdit_5.setGeometry(QtCore.QRect(10, 70, 81, 21))
        self.lineEdit_5.setReadOnly(True)
        self.lineEdit_5.setObjectName(_fromUtf8("lineEdit_5"))
        self.lineEdit_6 = QtGui.QLineEdit(Form)
        self.lineEdit_6.setGeometry(QtCore.QRect(10, 90, 81, 21))
        self.lineEdit_6.setReadOnly(True)
        self.lineEdit_6.setObjectName(_fromUtf8("lineEdit_6"))
        self.lineEdit_7 = QtGui.QLineEdit(Form)
        self.lineEdit_7.setGeometry(QtCore.QRect(10, 110, 81, 21))
        self.lineEdit_7.setReadOnly(True)
        self.lineEdit_7.setObjectName(_fromUtf8("lineEdit_7"))
        self.lineEdit_8 = QtGui.QLineEdit(Form)
        self.lineEdit_8.setGeometry(QtCore.QRect(10, 140, 81, 21))
        self.lineEdit_8.setReadOnly(True)
        self.lineEdit_8.setObjectName(_fromUtf8("lineEdit_8"))
        self.leType = QtGui.QLineEdit(Form)
        self.leType.setGeometry(QtCore.QRect(90, 50, 81, 21))
        self.leType.setText(_fromUtf8(""))
        self.leType.setReadOnly(True)
        self.leType.setObjectName(_fromUtf8("leType"))
        self.leManufacturer = QtGui.QLineEdit(Form)
        self.leManufacturer.setGeometry(QtCore.QRect(90, 110, 81, 21))
        self.leManufacturer.setText(_fromUtf8(""))
        self.leManufacturer.setReadOnly(True)
        self.leManufacturer.setObjectName(_fromUtf8("leManufacturer"))
        self.pbGoModule = QtGui.QPushButton(Form)
        self.pbGoModule.setGeometry(QtCore.QRect(170, 140, 41, 21))
        self.pbGoModule.setObjectName(_fromUtf8("pbGoModule"))
        self.pbSensorCancel = QtGui.QPushButton(Form)
        self.pbSensorCancel.setGeometry(QtCore.QRect(290, 40, 71, 21))
        self.pbSensorCancel.setObjectName(_fromUtf8("pbSensorCancel"))
        self.pbSensorEdit = QtGui.QPushButton(Form)
        self.pbSensorEdit.setGeometry(QtCore.QRect(290, 10, 71, 21))
        self.pbSensorEdit.setObjectName(_fromUtf8("pbSensorEdit"))
        self.pbSensorNew = QtGui.QPushButton(Form)
        self.pbSensorNew.setGeometry(QtCore.QRect(210, 10, 71, 21))
        self.pbSensorNew.setObjectName(_fromUtf8("pbSensorNew"))
        self.pbSensorSave = QtGui.QPushButton(Form)
        self.pbSensorSave.setGeometry(QtCore.QRect(210, 40, 71, 21))
        self.pbSensorSave.setObjectName(_fromUtf8("pbSensorSave"))
        self.dsbSize = QtGui.QDoubleSpinBox(Form)
        self.dsbSize.setGeometry(QtCore.QRect(90, 70, 81, 21))
        self.dsbSize.setReadOnly(True)
        self.dsbSize.setMinimum(-1.0)
        self.dsbSize.setMaximum(2147483647.0)
        self.dsbSize.setObjectName(_fromUtf8("dsbSize"))
        self.sbChannels = QtGui.QSpinBox(Form)
        self.sbChannels.setGeometry(QtCore.QRect(90, 90, 81, 21))
        self.sbChannels.setReadOnly(True)
        self.sbChannels.setMinimum(-1)
        self.sbChannels.setMaximum(2147483647)
        self.sbChannels.setObjectName(_fromUtf8("sbChannels"))
        self.sbOnModule = QtGui.QSpinBox(Form)
        self.sbOnModule.setGeometry(QtCore.QRect(90, 140, 81, 21))
        self.sbOnModule.setReadOnly(True)
        self.sbOnModule.setMinimum(-1)
        self.sbOnModule.setMaximum(2147483647)
        self.sbOnModule.setObjectName(_fromUtf8("sbOnModule"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.lineEdit.setText(_translate("Form", "Sensor ID", None))
        self.lineEdit_2.setText(_translate("Form", "Identifier", None))
        self.lineEdit_4.setText(_translate("Form", "Type", None))
        self.lineEdit_5.setText(_translate("Form", "Size", None))
        self.lineEdit_6.setText(_translate("Form", "Channels", None))
        self.lineEdit_7.setText(_translate("Form", "Manufacturer", None))
        self.lineEdit_8.setText(_translate("Form", "On module", None))
        self.pbGoModule.setText(_translate("Form", "Go to", None))
        self.pbSensorCancel.setText(_translate("Form", "Cancel", None))
        self.pbSensorEdit.setText(_translate("Form", "Edit", None))
        self.pbSensorNew.setText(_translate("Form", "New", None))
        self.pbSensorSave.setText(_translate("Form", "Save", None))

