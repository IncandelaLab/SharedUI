# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'view_baseplate.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1097, 720)
        font = QtGui.QFont()
        font.setFamily("Arial")
        Form.setFont(font)
        self.frame_2 = QtWidgets.QFrame(Form)
        self.frame_2.setGeometry(QtCore.QRect(20, 10, 251, 111))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_2.setObjectName("frame_2")
        self.pbSave = QtWidgets.QPushButton(self.frame_2)
        self.pbSave.setGeometry(QtCore.QRect(50, 60, 71, 21))
        self.pbSave.setObjectName("pbSave")
        self.lineEdit = QtWidgets.QLineEdit(self.frame_2)
        self.lineEdit.setGeometry(QtCore.QRect(0, 1, 121, 20))
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName("lineEdit")
        self.pbCancel = QtWidgets.QPushButton(self.frame_2)
        self.pbCancel.setGeometry(QtCore.QRect(130, 60, 71, 21))
        self.pbCancel.setObjectName("pbCancel")
        self.pbNew = QtWidgets.QPushButton(self.frame_2)
        self.pbNew.setGeometry(QtCore.QRect(90, 30, 71, 21))
        self.pbNew.setObjectName("pbNew")
        self.pbEdit = QtWidgets.QPushButton(self.frame_2)
        self.pbEdit.setGeometry(QtCore.QRect(170, 30, 71, 21))
        self.pbEdit.setObjectName("pbEdit")
        self.leID = QtWidgets.QLineEdit(self.frame_2)
        self.leID.setGeometry(QtCore.QRect(120, 0, 131, 20))
        self.leID.setText("")
        self.leID.setReadOnly(True)
        self.leID.setObjectName("leID")
        self.lineEdit_6 = QtWidgets.QLineEdit(self.frame_2)
        self.lineEdit_6.setGeometry(QtCore.QRect(10, 90, 71, 20))
        self.lineEdit_6.setReadOnly(True)
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.leStatus = QtWidgets.QLineEdit(self.frame_2)
        self.leStatus.setGeometry(QtCore.QRect(80, 90, 161, 20))
        self.leStatus.setText("")
        self.leStatus.setReadOnly(True)
        self.leStatus.setObjectName("leStatus")
        self.pbLoad = QtWidgets.QPushButton(self.frame_2)
        self.pbLoad.setGeometry(QtCore.QRect(10, 30, 71, 21))
        self.pbLoad.setObjectName("pbLoad")
        self.frame_3 = QtWidgets.QFrame(Form)
        self.frame_3.setGeometry(QtCore.QRect(20, 160, 261, 441))
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_3.setObjectName("frame_3")
        self.lineEdit_11 = QtWidgets.QLineEdit(self.frame_3)
        self.lineEdit_11.setGeometry(QtCore.QRect(1, 41, 121, 20))
        self.lineEdit_11.setReadOnly(True)
        self.lineEdit_11.setObjectName("lineEdit_11")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.frame_3)
        self.lineEdit_3.setGeometry(QtCore.QRect(1, 99, 161, 21))
        self.lineEdit_3.setReadOnly(True)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.leLocation = QtWidgets.QLineEdit(self.frame_3)
        self.leLocation.setGeometry(QtCore.QRect(119, 41, 141, 20))
        self.leLocation.setText("")
        self.leLocation.setReadOnly(True)
        self.leLocation.setObjectName("leLocation")
        self.lineEdit_15 = QtWidgets.QLineEdit(self.frame_3)
        self.lineEdit_15.setGeometry(QtCore.QRect(1, 120, 161, 20))
        self.lineEdit_15.setReadOnly(True)
        self.lineEdit_15.setObjectName("lineEdit_15")
        self.cbMaterial = QtWidgets.QComboBox(self.frame_3)
        self.cbMaterial.setGeometry(QtCore.QRect(160, 99, 101, 21))
        self.cbMaterial.setObjectName("cbMaterial")
        self.cbMaterial.addItem("")
        self.cbMaterial.addItem("")
        self.lineEdit_39 = QtWidgets.QLineEdit(self.frame_3)
        self.lineEdit_39.setGeometry(QtCore.QRect(1, 21, 121, 20))
        self.lineEdit_39.setReadOnly(True)
        self.lineEdit_39.setObjectName("lineEdit_39")
        self.lineEdit_38 = QtWidgets.QLineEdit(self.frame_3)
        self.lineEdit_38.setGeometry(QtCore.QRect(1, 1, 121, 20))
        self.lineEdit_38.setReadOnly(True)
        self.lineEdit_38.setObjectName("lineEdit_38")
        self.leBarcode = QtWidgets.QLineEdit(self.frame_3)
        self.leBarcode.setGeometry(QtCore.QRect(159, 80, 101, 20))
        self.leBarcode.setText("")
        self.leBarcode.setReadOnly(True)
        self.leBarcode.setObjectName("leBarcode")
        self.lineEdit_9 = QtWidgets.QLineEdit(self.frame_3)
        self.lineEdit_9.setGeometry(QtCore.QRect(1, 80, 161, 21))
        self.lineEdit_9.setReadOnly(True)
        self.lineEdit_9.setObjectName("lineEdit_9")
        self.cbInsertUser = QtWidgets.QComboBox(self.frame_3)
        self.cbInsertUser.setGeometry(QtCore.QRect(120, 0, 141, 21))
        self.cbInsertUser.setObjectName("cbInsertUser")
        self.cbShape = QtWidgets.QComboBox(self.frame_3)
        self.cbShape.setGeometry(QtCore.QRect(160, 120, 101, 20))
        self.cbShape.setObjectName("cbShape")
        self.cbShape.addItem("")
        self.cbShape.addItem("")
        self.cbShape.addItem("")
        self.cbShape.addItem("")
        self.cbShape.addItem("")
        self.cbShape.addItem("")
        self.cbShape.addItem("")
        self.cbShape.addItem("")
        self.pbAddComment = QtWidgets.QPushButton(self.frame_3)
        self.pbAddComment.setGeometry(QtCore.QRect(0, 420, 111, 21))
        self.pbAddComment.setObjectName("pbAddComment")
        self.pbDeleteComment = QtWidgets.QPushButton(self.frame_3)
        self.pbDeleteComment.setGeometry(QtCore.QRect(140, 180, 121, 21))
        self.pbDeleteComment.setObjectName("pbDeleteComment")
        self.listComments = QtWidgets.QListWidget(self.frame_3)
        self.listComments.setGeometry(QtCore.QRect(0, 200, 261, 141))
        self.listComments.setObjectName("listComments")
        self.lineEdit_14 = QtWidgets.QLineEdit(self.frame_3)
        self.lineEdit_14.setGeometry(QtCore.QRect(1, 180, 141, 21))
        self.lineEdit_14.setReadOnly(True)
        self.lineEdit_14.setObjectName("lineEdit_14")
        self.pteWriteComment = QtWidgets.QPlainTextEdit(self.frame_3)
        self.pteWriteComment.setGeometry(QtCore.QRect(0, 350, 261, 71))
        self.pteWriteComment.setPlainText("")
        self.pteWriteComment.setObjectName("pteWriteComment")
        self.cbChannelDensity = QtWidgets.QComboBox(self.frame_3)
        self.cbChannelDensity.setGeometry(QtCore.QRect(160, 140, 101, 20))
        self.cbChannelDensity.setObjectName("cbChannelDensity")
        self.cbChannelDensity.addItem("")
        self.cbChannelDensity.addItem("")
        self.lineEdit_16 = QtWidgets.QLineEdit(self.frame_3)
        self.lineEdit_16.setGeometry(QtCore.QRect(0, 140, 161, 20))
        self.lineEdit_16.setReadOnly(True)
        self.lineEdit_16.setObjectName("lineEdit_16")
        self.cbInstitution = QtWidgets.QComboBox(self.frame_3)
        self.cbInstitution.setGeometry(QtCore.QRect(120, 20, 141, 21))
        self.cbInstitution.setObjectName("cbInstitution")
        self.cbInstitution.addItem("")
        self.cbInstitution.addItem("")
        self.cbInstitution.addItem("")
        self.cbInstitution.addItem("")
        self.cbInstitution.addItem("")
        self.cbInstitution.addItem("")
        self.cbInstitution.addItem("")
        self.cbInstitution.addItem("")
        self.cbInstitution.addItem("")
        self.cbInstitution.addItem("")
        self.cbInstitution.addItem("")
        self.cbInstitution.addItem("")
        self.lineEdit_11.raise_()
        self.lineEdit_3.raise_()
        self.leLocation.raise_()
        self.lineEdit_15.raise_()
        self.cbMaterial.raise_()
        self.lineEdit_39.raise_()
        self.lineEdit_38.raise_()
        self.lineEdit_9.raise_()
        self.leBarcode.raise_()
        self.cbInsertUser.raise_()
        self.cbShape.raise_()
        self.pbAddComment.raise_()
        self.pbDeleteComment.raise_()
        self.listComments.raise_()
        self.lineEdit_14.raise_()
        self.pteWriteComment.raise_()
        self.cbChannelDensity.raise_()
        self.lineEdit_16.raise_()
        self.cbInstitution.raise_()
        self.label_8 = QtWidgets.QLabel(Form)
        self.label_8.setGeometry(QtCore.QRect(310, 250, 211, 16))
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(Form)
        self.label_9.setGeometry(QtCore.QRect(310, 340, 211, 16))
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(Form)
        self.label_10.setGeometry(QtCore.QRect(630, 50, 201, 16))
        self.label_10.setObjectName("label_10")
        self.label_13 = QtWidgets.QLabel(Form)
        self.label_13.setGeometry(QtCore.QRect(760, 90, 21, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(16)
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")
        self.label_5 = QtWidgets.QLabel(Form)
        self.label_5.setGeometry(QtCore.QRect(310, 140, 261, 16))
        self.label_5.setObjectName("label_5")
        self.frame_4 = QtWidgets.QFrame(Form)
        self.frame_4.setGeometry(QtCore.QRect(310, 160, 241, 61))
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_4.setObjectName("frame_4")
        self.lineEdit_12 = QtWidgets.QLineEdit(self.frame_4)
        self.lineEdit_12.setGeometry(QtCore.QRect(0, 20, 161, 20))
        self.lineEdit_12.setReadOnly(True)
        self.lineEdit_12.setObjectName("lineEdit_12")
        self.dsbFlatness = QtWidgets.QDoubleSpinBox(self.frame_4)
        self.dsbFlatness.setGeometry(QtCore.QRect(160, 20, 80, 21))
        self.dsbFlatness.setReadOnly(False)
        self.dsbFlatness.setDecimals(3)
        self.dsbFlatness.setMinimum(-1.0)
        self.dsbFlatness.setMaximum(2147483647.0)
        self.dsbFlatness.setSingleStep(0.05)
        self.dsbFlatness.setObjectName("dsbFlatness")
        self.lineEdit_13 = QtWidgets.QLineEdit(self.frame_4)
        self.lineEdit_13.setGeometry(QtCore.QRect(0, 40, 161, 20))
        self.lineEdit_13.setReadOnly(True)
        self.lineEdit_13.setObjectName("lineEdit_13")
        self.lineEdit_4 = QtWidgets.QLineEdit(self.frame_4)
        self.lineEdit_4.setGeometry(QtCore.QRect(0, 0, 161, 21))
        self.lineEdit_4.setReadOnly(True)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.dsbThickness = QtWidgets.QDoubleSpinBox(self.frame_4)
        self.dsbThickness.setGeometry(QtCore.QRect(160, 0, 80, 21))
        self.dsbThickness.setReadOnly(False)
        self.dsbThickness.setDecimals(3)
        self.dsbThickness.setMinimum(-1.0)
        self.dsbThickness.setMaximum(2147483647.0)
        self.dsbThickness.setSingleStep(0.05)
        self.dsbThickness.setObjectName("dsbThickness")
        self.label_17 = QtWidgets.QLabel(Form)
        self.label_17.setGeometry(QtCore.QRect(740, 120, 81, 16))
        self.label_17.setObjectName("label_17")
        self.label_14 = QtWidgets.QLabel(Form)
        self.label_14.setGeometry(QtCore.QRect(670, 250, 21, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(16)
        self.label_14.setFont(font)
        self.label_14.setObjectName("label_14")
        self.label_15 = QtWidgets.QLabel(Form)
        self.label_15.setGeometry(QtCore.QRect(750, 400, 21, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(16)
        self.label_15.setFont(font)
        self.label_15.setObjectName("label_15")
        self.label_16 = QtWidgets.QLabel(Form)
        self.label_16.setGeometry(QtCore.QRect(930, 400, 21, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(16)
        self.label_16.setFont(font)
        self.label_16.setObjectName("label_16")
        self.label_18 = QtWidgets.QLabel(Form)
        self.label_18.setGeometry(QtCore.QRect(1020, 250, 21, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(16)
        self.label_18.setFont(font)
        self.label_18.setObjectName("label_18")
        self.label_19 = QtWidgets.QLabel(Form)
        self.label_19.setGeometry(QtCore.QRect(930, 90, 21, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(16)
        self.label_19.setFont(font)
        self.label_19.setObjectName("label_19")
        self.label_11 = QtWidgets.QLabel(Form)
        self.label_11.setGeometry(QtCore.QRect(830, 240, 51, 16))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.plt_image = QtWidgets.QLabel(Form)
        self.plt_image.setGeometry(QtCore.QRect(630, 70, 441, 381))
        self.plt_image.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.plt_image.setText("")
        self.plt_image.setPixmap(QtGui.QPixmap("pages_ui/pages_ui/new_baseplate.png"))
        self.plt_image.setScaledContents(True)
        self.plt_image.setObjectName("plt_image")
        self.cbGrade = QtWidgets.QComboBox(Form)
        self.cbGrade.setGeometry(QtCore.QRect(470, 200, 81, 21))
        self.cbGrade.setObjectName("cbGrade")
        self.cbGrade.addItem("")
        self.cbGrade.addItem("")
        self.cbGrade.addItem("")
        self.frame = QtWidgets.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(310, 270, 301, 41))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.leProtomodule = QtWidgets.QLineEdit(self.frame)
        self.leProtomodule.setGeometry(QtCore.QRect(120, 20, 131, 20))
        self.leProtomodule.setReadOnly(True)
        self.leProtomodule.setObjectName("leProtomodule")
        self.lineEdit_17 = QtWidgets.QLineEdit(self.frame)
        self.lineEdit_17.setGeometry(QtCore.QRect(0, 20, 121, 21))
        self.lineEdit_17.setReadOnly(True)
        self.lineEdit_17.setObjectName("lineEdit_17")
        self.pbGoProtomodule = QtWidgets.QPushButton(self.frame)
        self.pbGoProtomodule.setGeometry(QtCore.QRect(250, 20, 51, 21))
        self.pbGoProtomodule.setObjectName("pbGoProtomodule")
        self.lineEdit_19 = QtWidgets.QLineEdit(self.frame)
        self.lineEdit_19.setGeometry(QtCore.QRect(0, 0, 121, 21))
        self.lineEdit_19.setReadOnly(True)
        self.lineEdit_19.setObjectName("lineEdit_19")
        self.sbStepSensor = QtWidgets.QSpinBox(self.frame)
        self.sbStepSensor.setGeometry(QtCore.QRect(200, 0, 51, 21))
        self.sbStepSensor.setReadOnly(True)
        self.sbStepSensor.setMinimum(-1)
        self.sbStepSensor.setMaximum(2147483647)
        self.sbStepSensor.setProperty("value", 0)
        self.sbStepSensor.setObjectName("sbStepSensor")
        self.pbGoStepSensor = QtWidgets.QPushButton(self.frame)
        self.pbGoStepSensor.setGeometry(QtCore.QRect(250, 0, 51, 21))
        self.pbGoStepSensor.setObjectName("pbGoStepSensor")
        self.cbInstitutionStep = QtWidgets.QComboBox(self.frame)
        self.cbInstitutionStep.setEnabled(False)
        self.cbInstitutionStep.setGeometry(QtCore.QRect(120, 0, 81, 21))
        self.cbInstitutionStep.setObjectName("cbInstitutionStep")
        self.cbInstitutionStep.addItem("")
        self.cbInstitutionStep.addItem("")
        self.cbInstitutionStep.addItem("")
        self.cbInstitutionStep.addItem("")
        self.cbInstitutionStep.addItem("")
        self.cbInstitutionStep.addItem("")
        self.frame_5 = QtWidgets.QFrame(Form)
        self.frame_5.setGeometry(QtCore.QRect(310, 360, 301, 21))
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.pbGoModule = QtWidgets.QPushButton(self.frame_5)
        self.pbGoModule.setGeometry(QtCore.QRect(250, 0, 51, 21))
        self.pbGoModule.setObjectName("pbGoModule")
        self.lineEdit_8 = QtWidgets.QLineEdit(self.frame_5)
        self.lineEdit_8.setGeometry(QtCore.QRect(0, 0, 121, 21))
        self.lineEdit_8.setReadOnly(True)
        self.lineEdit_8.setObjectName("lineEdit_8")
        self.leModule = QtWidgets.QLineEdit(self.frame_5)
        self.leModule.setGeometry(QtCore.QRect(120, 0, 131, 20))
        self.leModule.setReadOnly(True)
        self.leModule.setObjectName("leModule")
        self.label_6 = QtWidgets.QLabel(Form)
        self.label_6.setGeometry(QtCore.QRect(20, 140, 151, 16))
        self.label_6.setObjectName("label_6")
        self.frame_2.raise_()
        self.frame_3.raise_()
        self.label_8.raise_()
        self.label_9.raise_()
        self.label_10.raise_()
        self.label_5.raise_()
        self.frame_4.raise_()
        self.plt_image.raise_()
        self.label_16.raise_()
        self.label_18.raise_()
        self.label_19.raise_()
        self.label_13.raise_()
        self.label_17.raise_()
        self.label_14.raise_()
        self.label_15.raise_()
        self.label_11.raise_()
        self.cbGrade.raise_()
        self.frame.raise_()
        self.frame_5.raise_()
        self.label_6.raise_()

        self.retranslateUi(Form)
        self.cbMaterial.setCurrentIndex(-1)
        self.cbInsertUser.setCurrentIndex(-1)
        self.cbShape.setCurrentIndex(-1)
        self.cbChannelDensity.setCurrentIndex(-1)
        self.cbInstitution.setCurrentIndex(-1)
        self.cbGrade.setCurrentIndex(-1)
        self.cbInstitutionStep.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pbSave.setText(_translate("Form", "Save"))
        self.lineEdit.setText(_translate("Form", "Baseplate ID"))
        self.pbCancel.setText(_translate("Form", "Cancel"))
        self.pbNew.setText(_translate("Form", "New"))
        self.pbEdit.setText(_translate("Form", "Edit"))
        self.lineEdit_6.setText(_translate("Form", "Status:"))
        self.pbLoad.setText(_translate("Form", "Load"))
        self.lineEdit_11.setText(_translate("Form", "Location"))
        self.lineEdit_3.setText(_translate("Form", "Material / type"))
        self.lineEdit_15.setText(_translate("Form", "Geometry"))
        self.cbMaterial.setItemText(0, _translate("Form", "CuW/Kapton"))
        self.cbMaterial.setItemText(1, _translate("Form", "PCB/Kapton"))
        self.lineEdit_39.setText(_translate("Form", "Institution"))
        self.lineEdit_38.setToolTip(_translate("Form", "height difference between highest and lowers corners"))
        self.lineEdit_38.setText(_translate("Form", "User name"))
        self.lineEdit_9.setText(_translate("Form", "Barcode"))
        self.cbShape.setItemText(0, _translate("Form", "Full"))
        self.cbShape.setItemText(1, _translate("Form", "Top"))
        self.cbShape.setItemText(2, _translate("Form", "Bottom"))
        self.cbShape.setItemText(3, _translate("Form", "Left"))
        self.cbShape.setItemText(4, _translate("Form", "Right"))
        self.cbShape.setItemText(5, _translate("Form", "Five"))
        self.cbShape.setItemText(6, _translate("Form", "Full"))
        self.cbShape.setItemText(7, _translate("Form", "Three"))
        self.pbAddComment.setText(_translate("Form", "Add comment"))
        self.pbDeleteComment.setText(_translate("Form", "Delete selected"))
        self.lineEdit_14.setText(_translate("Form", "Comments"))
        self.cbChannelDensity.setItemText(0, _translate("Form", "HD"))
        self.cbChannelDensity.setItemText(1, _translate("Form", "LD"))
        self.lineEdit_16.setText(_translate("Form", "Sensor resolution"))
        self.cbInstitution.setItemText(0, _translate("Form", "CERN"))
        self.cbInstitution.setItemText(1, _translate("Form", "FNAL"))
        self.cbInstitution.setItemText(2, _translate("Form", "UCSB"))
        self.cbInstitution.setItemText(3, _translate("Form", "UMN"))
        self.cbInstitution.setItemText(4, _translate("Form", "HEPHY"))
        self.cbInstitution.setItemText(5, _translate("Form", "HPK"))
        self.cbInstitution.setItemText(6, _translate("Form", "CMU"))
        self.cbInstitution.setItemText(7, _translate("Form", "TTU"))
        self.cbInstitution.setItemText(8, _translate("Form", "IHEP"))
        self.cbInstitution.setItemText(9, _translate("Form", "TIFR"))
        self.cbInstitution.setItemText(10, _translate("Form", "NTU"))
        self.cbInstitution.setItemText(11, _translate("Form", "FSU"))
        self.label_8.setText(_translate("Form", "Sensor placement"))
        self.label_9.setText(_translate("Form", "Module"))
        self.label_10.setText(_translate("Form", "Corner numbering reference"))
        self.label_13.setText(_translate("Form", "A"))
        self.label_5.setText(_translate("Form", "Baseplate qualification & preparation"))
        self.lineEdit_12.setToolTip(_translate("Form", "height difference between highest and lowers corners"))
        self.lineEdit_12.setText(_translate("Form", "Flatness (mm)"))
        self.lineEdit_13.setToolTip(_translate("Form", "height difference between highest and lowers corners"))
        self.lineEdit_13.setText(_translate("Form", "Baseplate grade"))
        self.lineEdit_4.setText(_translate("Form", "Thickness (mm)"))
        self.label_17.setText(_translate("Form", "(Channel 1)"))
        self.label_14.setText(_translate("Form", "B"))
        self.label_15.setText(_translate("Form", "C"))
        self.label_16.setText(_translate("Form", "D"))
        self.label_18.setText(_translate("Form", "E"))
        self.label_19.setText(_translate("Form", "F"))
        self.label_11.setText(_translate("Form", "Front"))
        self.cbGrade.setItemText(0, _translate("Form", "Green"))
        self.cbGrade.setItemText(1, _translate("Form", "Yellow"))
        self.cbGrade.setItemText(2, _translate("Form", "Red"))
        self.lineEdit_17.setText(_translate("Form", "On protomodule"))
        self.pbGoProtomodule.setText(_translate("Form", "Go to"))
        self.lineEdit_19.setText(_translate("Form", "Sensor step"))
        self.pbGoStepSensor.setText(_translate("Form", "Go to"))
        self.cbInstitutionStep.setItemText(0, _translate("Form", "CERN"))
        self.cbInstitutionStep.setItemText(1, _translate("Form", "FNAL"))
        self.cbInstitutionStep.setItemText(2, _translate("Form", "UCSB"))
        self.cbInstitutionStep.setItemText(3, _translate("Form", "UMN"))
        self.cbInstitutionStep.setItemText(4, _translate("Form", "HEPHY"))
        self.cbInstitutionStep.setItemText(5, _translate("Form", "HPK"))
        self.pbGoModule.setText(_translate("Form", "Go to"))
        self.lineEdit_8.setText(_translate("Form", "On module"))
        self.label_6.setText(_translate("Form", "Standard information"))
