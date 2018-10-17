# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'view_baseplate.ui'
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
        self.lineEdit.setGeometry(QtCore.QRect(10, 10, 81, 21))
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.sbBaseplateID = QtGui.QSpinBox(Form)
        self.sbBaseplateID.setGeometry(QtCore.QRect(90, 10, 81, 21))
        self.sbBaseplateID.setMaximum(65535)
        self.sbBaseplateID.setObjectName(_fromUtf8("sbBaseplateID"))
        self.lineEdit_2 = QtGui.QLineEdit(Form)
        self.lineEdit_2.setGeometry(QtCore.QRect(10, 30, 81, 21))
        self.lineEdit_2.setReadOnly(True)
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.lineEdit_3 = QtGui.QLineEdit(Form)
        self.lineEdit_3.setGeometry(QtCore.QRect(10, 50, 81, 21))
        self.lineEdit_3.setReadOnly(True)
        self.lineEdit_3.setObjectName(_fromUtf8("lineEdit_3"))
        self.lineEdit_4 = QtGui.QLineEdit(Form)
        self.lineEdit_4.setGeometry(QtCore.QRect(10, 70, 81, 21))
        self.lineEdit_4.setReadOnly(True)
        self.lineEdit_4.setObjectName(_fromUtf8("lineEdit_4"))
        self.lineEdit_5 = QtGui.QLineEdit(Form)
        self.lineEdit_5.setGeometry(QtCore.QRect(10, 90, 81, 21))
        self.lineEdit_5.setReadOnly(True)
        self.lineEdit_5.setObjectName(_fromUtf8("lineEdit_5"))
        self.lineEdit_6 = QtGui.QLineEdit(Form)
        self.lineEdit_6.setGeometry(QtCore.QRect(10, 110, 81, 21))
        self.lineEdit_6.setReadOnly(True)
        self.lineEdit_6.setObjectName(_fromUtf8("lineEdit_6"))
        self.lineEdit_7 = QtGui.QLineEdit(Form)
        self.lineEdit_7.setGeometry(QtCore.QRect(10, 130, 81, 21))
        self.lineEdit_7.setReadOnly(True)
        self.lineEdit_7.setObjectName(_fromUtf8("lineEdit_7"))
        self.leIdentifier = QtGui.QLineEdit(Form)
        self.leIdentifier.setGeometry(QtCore.QRect(90, 30, 81, 21))
        self.leIdentifier.setReadOnly(True)
        self.leIdentifier.setObjectName(_fromUtf8("leIdentifier"))
        self.leMaterial = QtGui.QLineEdit(Form)
        self.leMaterial.setGeometry(QtCore.QRect(90, 50, 81, 21))
        self.leMaterial.setReadOnly(True)
        self.leMaterial.setObjectName(_fromUtf8("leMaterial"))
        self.leNomThickness = QtGui.QLineEdit(Form)
        self.leNomThickness.setGeometry(QtCore.QRect(90, 70, 81, 21))
        self.leNomThickness.setReadOnly(True)
        self.leNomThickness.setObjectName(_fromUtf8("leNomThickness"))
        self.leFlatness = QtGui.QLineEdit(Form)
        self.leFlatness.setGeometry(QtCore.QRect(90, 90, 81, 21))
        self.leFlatness.setReadOnly(True)
        self.leFlatness.setObjectName(_fromUtf8("leFlatness"))
        self.leSize = QtGui.QLineEdit(Form)
        self.leSize.setGeometry(QtCore.QRect(90, 110, 81, 21))
        self.leSize.setReadOnly(True)
        self.leSize.setObjectName(_fromUtf8("leSize"))
        self.leManufacturer = QtGui.QLineEdit(Form)
        self.leManufacturer.setGeometry(QtCore.QRect(90, 130, 81, 21))
        self.leManufacturer.setReadOnly(True)
        self.leManufacturer.setObjectName(_fromUtf8("leManufacturer"))
        self.lineEdit_8 = QtGui.QLineEdit(Form)
        self.lineEdit_8.setGeometry(QtCore.QRect(10, 160, 81, 21))
        self.lineEdit_8.setReadOnly(True)
        self.lineEdit_8.setObjectName(_fromUtf8("lineEdit_8"))
        self.leOnModule = QtGui.QLineEdit(Form)
        self.leOnModule.setGeometry(QtCore.QRect(90, 160, 81, 21))
        self.leOnModule.setReadOnly(True)
        self.leOnModule.setObjectName(_fromUtf8("leOnModule"))
        self.pbGoModule = QtGui.QPushButton(Form)
        self.pbGoModule.setGeometry(QtCore.QRect(170, 160, 41, 21))
        self.pbGoModule.setObjectName(_fromUtf8("pbGoModule"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.lineEdit.setText(_translate("Form", "Baseplate ID", None))
        self.lineEdit_2.setText(_translate("Form", "Identifier", None))
        self.lineEdit_3.setText(_translate("Form", "Material", None))
        self.lineEdit_4.setText(_translate("Form", "Nom Thickness", None))
        self.lineEdit_5.setText(_translate("Form", "Flatness", None))
        self.lineEdit_6.setText(_translate("Form", "Size", None))
        self.lineEdit_7.setText(_translate("Form", "Manufacturer", None))
        self.lineEdit_8.setText(_translate("Form", "On module", None))
        self.pbGoModule.setText(_translate("Form", "Go to", None))

