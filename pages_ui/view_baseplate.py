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
        Form.resize(874, 643)
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
        self.leManufacturer = QtGui.QLineEdit(Form)
        self.leManufacturer.setGeometry(QtCore.QRect(90, 130, 81, 21))
        self.leManufacturer.setReadOnly(True)
        self.leManufacturer.setObjectName(_fromUtf8("leManufacturer"))
        self.lineEdit_8 = QtGui.QLineEdit(Form)
        self.lineEdit_8.setGeometry(QtCore.QRect(10, 160, 81, 21))
        self.lineEdit_8.setReadOnly(True)
        self.lineEdit_8.setObjectName(_fromUtf8("lineEdit_8"))
        self.pbGoModule = QtGui.QPushButton(Form)
        self.pbGoModule.setGeometry(QtCore.QRect(170, 160, 41, 21))
        self.pbGoModule.setObjectName(_fromUtf8("pbGoModule"))
        self.label = QtGui.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(330, 190, 481, 411))
        self.label.setText(_fromUtf8(""))
        self.label.setPixmap(QtGui.QPixmap(_fromUtf8("pages_ui/baseplate_frame_80.png")))
        self.label.setObjectName(_fromUtf8("label"))
        self.dsbC4 = QtGui.QDoubleSpinBox(Form)
        self.dsbC4.setEnabled(False)
        self.dsbC4.setGeometry(QtCore.QRect(420, 610, 62, 22))
        self.dsbC4.setDecimals(2)
        self.dsbC4.setMinimum(-8192.0)
        self.dsbC4.setMaximum(8191.0)
        self.dsbC4.setSingleStep(0.05)
        self.dsbC4.setObjectName(_fromUtf8("dsbC4"))
        self.dsbC5 = QtGui.QDoubleSpinBox(Form)
        self.dsbC5.setEnabled(False)
        self.dsbC5.setGeometry(QtCore.QRect(650, 610, 62, 22))
        self.dsbC5.setDecimals(2)
        self.dsbC5.setMinimum(-8192.0)
        self.dsbC5.setMaximum(8191.0)
        self.dsbC5.setSingleStep(0.05)
        self.dsbC5.setObjectName(_fromUtf8("dsbC5"))
        self.dsbC2 = QtGui.QDoubleSpinBox(Form)
        self.dsbC2.setEnabled(False)
        self.dsbC2.setGeometry(QtCore.QRect(420, 160, 62, 22))
        self.dsbC2.setDecimals(2)
        self.dsbC2.setMinimum(-8192.0)
        self.dsbC2.setMaximum(8191.0)
        self.dsbC2.setSingleStep(0.05)
        self.dsbC2.setObjectName(_fromUtf8("dsbC2"))
        self.dsbC1 = QtGui.QDoubleSpinBox(Form)
        self.dsbC1.setEnabled(False)
        self.dsbC1.setGeometry(QtCore.QRect(650, 160, 62, 22))
        self.dsbC1.setDecimals(2)
        self.dsbC1.setMinimum(-8192.0)
        self.dsbC1.setMaximum(8191.0)
        self.dsbC1.setSingleStep(0.05)
        self.dsbC1.setObjectName(_fromUtf8("dsbC1"))
        self.dsbC0 = QtGui.QDoubleSpinBox(Form)
        self.dsbC0.setEnabled(False)
        self.dsbC0.setGeometry(QtCore.QRect(710, 390, 62, 22))
        self.dsbC0.setDecimals(2)
        self.dsbC0.setMinimum(-8192.0)
        self.dsbC0.setMaximum(8191.0)
        self.dsbC0.setSingleStep(0.05)
        self.dsbC0.setObjectName(_fromUtf8("dsbC0"))
        self.dsbC3 = QtGui.QDoubleSpinBox(Form)
        self.dsbC3.setEnabled(False)
        self.dsbC3.setGeometry(QtCore.QRect(260, 390, 62, 22))
        self.dsbC3.setDecimals(2)
        self.dsbC3.setMinimum(-8192.0)
        self.dsbC3.setMaximum(8191.0)
        self.dsbC3.setSingleStep(0.05)
        self.dsbC3.setObjectName(_fromUtf8("dsbC3"))
        self.lineEdit_9 = QtGui.QLineEdit(Form)
        self.lineEdit_9.setGeometry(QtCore.QRect(500, 390, 131, 20))
        self.lineEdit_9.setReadOnly(True)
        self.lineEdit_9.setObjectName(_fromUtf8("lineEdit_9"))
        self.pbEditCornerHeights = QtGui.QPushButton(Form)
        self.pbEditCornerHeights.setGeometry(QtCore.QRect(500, 410, 131, 21))
        self.pbEditCornerHeights.setObjectName(_fromUtf8("pbEditCornerHeights"))
        self.pbSaveCorners = QtGui.QPushButton(Form)
        self.pbSaveCorners.setEnabled(False)
        self.pbSaveCorners.setGeometry(QtCore.QRect(500, 430, 61, 21))
        self.pbSaveCorners.setObjectName(_fromUtf8("pbSaveCorners"))
        self.pbCancelCorners = QtGui.QPushButton(Form)
        self.pbCancelCorners.setEnabled(False)
        self.pbCancelCorners.setGeometry(QtCore.QRect(570, 430, 61, 21))
        self.pbCancelCorners.setObjectName(_fromUtf8("pbCancelCorners"))
        self.pbBaseplateNew = QtGui.QPushButton(Form)
        self.pbBaseplateNew.setGeometry(QtCore.QRect(210, 10, 71, 21))
        self.pbBaseplateNew.setObjectName(_fromUtf8("pbBaseplateNew"))
        self.pbBaseplateEdit = QtGui.QPushButton(Form)
        self.pbBaseplateEdit.setGeometry(QtCore.QRect(290, 10, 71, 21))
        self.pbBaseplateEdit.setObjectName(_fromUtf8("pbBaseplateEdit"))
        self.pbBaseplateCancel = QtGui.QPushButton(Form)
        self.pbBaseplateCancel.setGeometry(QtCore.QRect(290, 40, 71, 21))
        self.pbBaseplateCancel.setObjectName(_fromUtf8("pbBaseplateCancel"))
        self.pbBaseplateSave = QtGui.QPushButton(Form)
        self.pbBaseplateSave.setGeometry(QtCore.QRect(210, 40, 71, 21))
        self.pbBaseplateSave.setObjectName(_fromUtf8("pbBaseplateSave"))
        self.dsbNomThickness = QtGui.QDoubleSpinBox(Form)
        self.dsbNomThickness.setGeometry(QtCore.QRect(90, 70, 81, 21))
        self.dsbNomThickness.setReadOnly(True)
        self.dsbNomThickness.setMinimum(-1.0)
        self.dsbNomThickness.setMaximum(2147483647.0)
        self.dsbNomThickness.setSingleStep(0.05)
        self.dsbNomThickness.setObjectName(_fromUtf8("dsbNomThickness"))
        self.dsbFlatness = QtGui.QDoubleSpinBox(Form)
        self.dsbFlatness.setGeometry(QtCore.QRect(90, 90, 81, 21))
        self.dsbFlatness.setReadOnly(True)
        self.dsbFlatness.setMinimum(-1.0)
        self.dsbFlatness.setMaximum(2147483647.0)
        self.dsbFlatness.setSingleStep(0.05)
        self.dsbFlatness.setObjectName(_fromUtf8("dsbFlatness"))
        self.dsbSize = QtGui.QDoubleSpinBox(Form)
        self.dsbSize.setGeometry(QtCore.QRect(90, 110, 81, 21))
        self.dsbSize.setReadOnly(True)
        self.dsbSize.setMinimum(-1.0)
        self.dsbSize.setMaximum(2147483647.0)
        self.dsbSize.setSingleStep(0.05)
        self.dsbSize.setObjectName(_fromUtf8("dsbSize"))
        self.sbOnModule = QtGui.QSpinBox(Form)
        self.sbOnModule.setGeometry(QtCore.QRect(90, 160, 81, 21))
        self.sbOnModule.setMinimum(-1)
        self.sbOnModule.setMaximum(2147483647)
        self.sbOnModule.setObjectName(_fromUtf8("sbOnModule"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.lineEdit.setText(_translate("Form", "Baseplate ID", None))
        self.lineEdit_2.setText(_translate("Form", "Identifier", None))
        self.lineEdit_3.setText(_translate("Form", "Material", None))
        self.lineEdit_4.setText(_translate("Form", "Nom Thickness", None))
        self.lineEdit_5.setToolTip(_translate("Form", "height difference between highest and lowers corners", None))
        self.lineEdit_5.setText(_translate("Form", "Flatness", None))
        self.lineEdit_6.setText(_translate("Form", "Size", None))
        self.lineEdit_7.setText(_translate("Form", "Manufacturer", None))
        self.lineEdit_8.setText(_translate("Form", "On module", None))
        self.pbGoModule.setText(_translate("Form", "Go to", None))
        self.dsbC4.setToolTip(_translate("Form", "Corner 4", None))
        self.dsbC5.setToolTip(_translate("Form", "Corner 5", None))
        self.dsbC2.setToolTip(_translate("Form", "Corner 2", None))
        self.dsbC1.setToolTip(_translate("Form", "Corner 1", None))
        self.dsbC0.setToolTip(_translate("Form", "Corner 0 (the corner with the oblong hole)", None))
        self.dsbC3.setToolTip(_translate("Form", "Corner 3", None))
        self.lineEdit_9.setText(_translate("Form", "Baseplate corner heights", None))
        self.pbEditCornerHeights.setText(_translate("Form", "Edit corner heights", None))
        self.pbSaveCorners.setText(_translate("Form", "Save", None))
        self.pbCancelCorners.setText(_translate("Form", "Cancel", None))
        self.pbBaseplateNew.setText(_translate("Form", "New", None))
        self.pbBaseplateEdit.setText(_translate("Form", "Edit", None))
        self.pbBaseplateCancel.setText(_translate("Form", "Cancel", None))
        self.pbBaseplateSave.setText(_translate("Form", "Save", None))

