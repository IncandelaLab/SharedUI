# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'view_protomodule.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1097, 705)
        self.frame_2 = QtWidgets.QFrame(Form)
        self.frame_2.setGeometry(QtCore.QRect(10, 100, 261, 531))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_2.setLineWidth(2)
        self.frame_2.setMidLineWidth(2)
        self.frame_2.setObjectName("frame_2")
        self.pbGoShipment = QtWidgets.QPushButton(self.frame_2)
        self.pbGoShipment.setGeometry(QtCore.QRect(120, 59, 141, 21))
        self.pbGoShipment.setObjectName("pbGoShipment")
        self.lineEdit_9 = QtWidgets.QLineEdit(self.frame_2)
        self.lineEdit_9.setGeometry(QtCore.QRect(1, 40, 121, 20))
        self.lineEdit_9.setReadOnly(True)
        self.lineEdit_9.setObjectName("lineEdit_9")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.frame_2)
        self.lineEdit_3.setGeometry(QtCore.QRect(1, 59, 121, 21))
        self.lineEdit_3.setReadOnly(True)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.leLocation = QtWidgets.QLineEdit(self.frame_2)
        self.leLocation.setGeometry(QtCore.QRect(120, 40, 141, 20))
        self.leLocation.setText("")
        self.leLocation.setReadOnly(True)
        self.leLocation.setObjectName("leLocation")
        self.listShipments = QtWidgets.QListWidget(self.frame_2)
        self.listShipments.setGeometry(QtCore.QRect(0, 79, 261, 91))
        self.listShipments.setObjectName("listShipments")
        self.lineEdit_10 = QtWidgets.QLineEdit(self.frame_2)
        self.lineEdit_10.setGeometry(QtCore.QRect(1, 229, 181, 21))
        self.lineEdit_10.setReadOnly(True)
        self.lineEdit_10.setObjectName("lineEdit_10")
        self.sbChannels = QtWidgets.QSpinBox(self.frame_2)
        self.sbChannels.setGeometry(QtCore.QRect(180, 209, 81, 21))
        self.sbChannels.setReadOnly(True)
        self.sbChannels.setMinimum(-1)
        self.sbChannels.setMaximum(2147483647)
        self.sbChannels.setObjectName("sbChannels")
        self.lineEdit_6 = QtWidgets.QLineEdit(self.frame_2)
        self.lineEdit_6.setGeometry(QtCore.QRect(1, 209, 181, 21))
        self.lineEdit_6.setReadOnly(True)
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.pbAddComment = QtWidgets.QPushButton(self.frame_2)
        self.pbAddComment.setGeometry(QtCore.QRect(0, 510, 101, 21))
        self.pbAddComment.setObjectName("pbAddComment")
        self.lineEdit_14 = QtWidgets.QLineEdit(self.frame_2)
        self.lineEdit_14.setGeometry(QtCore.QRect(1, 290, 141, 21))
        self.lineEdit_14.setReadOnly(True)
        self.lineEdit_14.setObjectName("lineEdit_14")
        self.pbDeleteComment = QtWidgets.QPushButton(self.frame_2)
        self.pbDeleteComment.setGeometry(QtCore.QRect(140, 290, 121, 21))
        self.pbDeleteComment.setObjectName("pbDeleteComment")
        self.pteWriteComment = QtWidgets.QPlainTextEdit(self.frame_2)
        self.pteWriteComment.setGeometry(QtCore.QRect(0, 440, 261, 71))
        self.pteWriteComment.setObjectName("pteWriteComment")
        self.listComments = QtWidgets.QListWidget(self.frame_2)
        self.listComments.setGeometry(QtCore.QRect(0, 310, 261, 121))
        self.listComments.setObjectName("listComments")
        self.lineEdit_15 = QtWidgets.QLineEdit(self.frame_2)
        self.lineEdit_15.setGeometry(QtCore.QRect(1, 249, 181, 21))
        self.lineEdit_15.setReadOnly(True)
        self.lineEdit_15.setObjectName("lineEdit_15")
        self.cbChirality = QtWidgets.QComboBox(self.frame_2)
        self.cbChirality.setGeometry(QtCore.QRect(180, 249, 81, 21))
        self.cbChirality.setObjectName("cbChirality")
        self.cbChirality.addItem("")
        self.cbChirality.addItem("")
        self.cbChirality.addItem("")
        self.lineEdit_4 = QtWidgets.QLineEdit(self.frame_2)
        self.lineEdit_4.setGeometry(QtCore.QRect(1, 189, 181, 21))
        self.lineEdit_4.setReadOnly(True)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.dsbThickness = QtWidgets.QDoubleSpinBox(self.frame_2)
        self.dsbThickness.setGeometry(QtCore.QRect(180, 189, 81, 21))
        self.dsbThickness.setReadOnly(True)
        self.dsbThickness.setMinimum(-1.0)
        self.dsbThickness.setMaximum(2147483647.0)
        self.dsbThickness.setSingleStep(0.1)
        self.dsbThickness.setObjectName("dsbThickness")
        self.cbShape = QtWidgets.QComboBox(self.frame_2)
        self.cbShape.setGeometry(QtCore.QRect(180, 229, 81, 21))
        self.cbShape.setObjectName("cbShape")
        self.cbShape.addItem("")
        self.cbShape.addItem("")
        self.cbShape.addItem("")
        self.cbShape.addItem("")
        self.cbShape.addItem("")
        self.cbShape.addItem("")
        self.cbShape.addItem("")
        self.lineEdit_52 = QtWidgets.QLineEdit(self.frame_2)
        self.lineEdit_52.setGeometry(QtCore.QRect(1, 20, 121, 21))
        self.lineEdit_52.setReadOnly(True)
        self.lineEdit_52.setObjectName("lineEdit_52")
        self.cbInstitution = QtWidgets.QComboBox(self.frame_2)
        self.cbInstitution.setGeometry(QtCore.QRect(120, 19, 141, 21))
        self.cbInstitution.setObjectName("cbInstitution")
        self.cbInstitution.addItem("")
        self.cbInstitution.addItem("")
        self.cbInstitution.addItem("")
        self.cbInstitution.addItem("")
        self.cbInstitution.addItem("")
        self.leInsertUser = QtWidgets.QLineEdit(self.frame_2)
        self.leInsertUser.setGeometry(QtCore.QRect(120, 1, 141, 20))
        self.leInsertUser.setText("")
        self.leInsertUser.setReadOnly(True)
        self.leInsertUser.setObjectName("leInsertUser")
        self.lineEdit_38 = QtWidgets.QLineEdit(self.frame_2)
        self.lineEdit_38.setGeometry(QtCore.QRect(1, 1, 121, 20))
        self.lineEdit_38.setReadOnly(True)
        self.lineEdit_38.setObjectName("lineEdit_38")
        self.lineEdit_9.raise_()
        self.lineEdit_3.raise_()
        self.leLocation.raise_()
        self.listShipments.raise_()
        self.lineEdit_10.raise_()
        self.lineEdit_6.raise_()
        self.pbAddComment.raise_()
        self.lineEdit_14.raise_()
        self.pbDeleteComment.raise_()
        self.pteWriteComment.raise_()
        self.listComments.raise_()
        self.lineEdit_15.raise_()
        self.cbChirality.raise_()
        self.lineEdit_4.raise_()
        self.dsbThickness.raise_()
        self.cbShape.raise_()
        self.sbChannels.raise_()
        self.pbGoShipment.raise_()
        self.lineEdit_52.raise_()
        self.cbInstitution.raise_()
        self.lineEdit_38.raise_()
        self.leInsertUser.raise_()
        self.frame_3 = QtWidgets.QFrame(Form)
        self.frame_3.setGeometry(QtCore.QRect(10, 10, 261, 71))
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_3.setObjectName("frame_3")
        self.pbSave = QtWidgets.QPushButton(self.frame_3)
        self.pbSave.setGeometry(QtCore.QRect(90, 30, 71, 21))
        self.pbSave.setObjectName("pbSave")
        self.pbEdit = QtWidgets.QPushButton(self.frame_3)
        self.pbEdit.setGeometry(QtCore.QRect(0, 30, 81, 21))
        self.pbEdit.setObjectName("pbEdit")
        self.pbCancel = QtWidgets.QPushButton(self.frame_3)
        self.pbCancel.setGeometry(QtCore.QRect(170, 30, 71, 21))
        self.pbCancel.setObjectName("pbCancel")
        self.lineEdit = QtWidgets.QLineEdit(self.frame_3)
        self.lineEdit.setGeometry(QtCore.QRect(1, 1, 151, 19))
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName("lineEdit")
        self.leID = QtWidgets.QLineEdit(self.frame_3)
        self.leID.setGeometry(QtCore.QRect(150, 0, 111, 20))
        self.leID.setText("")
        self.leID.setReadOnly(True)
        self.leID.setObjectName("leID")
        self.leStatus = QtWidgets.QLineEdit(self.frame_3)
        self.leStatus.setGeometry(QtCore.QRect(0, 50, 111, 20))
        self.leStatus.setText("")
        self.leStatus.setReadOnly(True)
        self.leStatus.setObjectName("leStatus")
        self.pbGoStepSensor = QtWidgets.QPushButton(Form)
        self.pbGoStepSensor.setGeometry(QtCore.QRect(530, 100, 51, 21))
        self.pbGoStepSensor.setObjectName("pbGoStepSensor")
        self.pbGoModule = QtWidgets.QPushButton(Form)
        self.pbGoModule.setGeometry(QtCore.QRect(500, 380, 51, 21))
        self.pbGoModule.setObjectName("pbGoModule")
        self.sbSensor = QtWidgets.QSpinBox(Form)
        self.sbSensor.setGeometry(QtCore.QRect(450, 120, 81, 21))
        self.sbSensor.setReadOnly(True)
        self.sbSensor.setMinimum(-1)
        self.sbSensor.setMaximum(2147483647)
        self.sbSensor.setObjectName("sbSensor")
        self.lineEdit_12 = QtWidgets.QLineEdit(Form)
        self.lineEdit_12.setGeometry(QtCore.QRect(330, 120, 121, 21))
        self.lineEdit_12.setReadOnly(True)
        self.lineEdit_12.setObjectName("lineEdit_12")
        self.lineEdit_8 = QtWidgets.QLineEdit(Form)
        self.lineEdit_8.setGeometry(QtCore.QRect(330, 380, 91, 21))
        self.lineEdit_8.setReadOnly(True)
        self.lineEdit_8.setObjectName("lineEdit_8")
        self.sbModule = QtWidgets.QSpinBox(Form)
        self.sbModule.setGeometry(QtCore.QRect(420, 380, 81, 21))
        self.sbModule.setReadOnly(True)
        self.sbModule.setMinimum(-1)
        self.sbModule.setMaximum(2147483647)
        self.sbModule.setObjectName("sbModule")
        self.lineEdit_13 = QtWidgets.QLineEdit(Form)
        self.lineEdit_13.setGeometry(QtCore.QRect(330, 100, 121, 21))
        self.lineEdit_13.setReadOnly(True)
        self.lineEdit_13.setObjectName("lineEdit_13")
        self.pbGoSensor = QtWidgets.QPushButton(Form)
        self.pbGoSensor.setGeometry(QtCore.QRect(530, 120, 51, 21))
        self.pbGoSensor.setObjectName("pbGoSensor")
        self.sbStepSensor = QtWidgets.QSpinBox(Form)
        self.sbStepSensor.setGeometry(QtCore.QRect(450, 100, 81, 21))
        self.sbStepSensor.setReadOnly(True)
        self.sbStepSensor.setMinimum(-1)
        self.sbStepSensor.setMaximum(2147483647)
        self.sbStepSensor.setObjectName("sbStepSensor")
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(330, 340, 111, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(330, 80, 121, 16))
        self.label_2.setObjectName("label_2")
        self.lineEdit_17 = QtWidgets.QLineEdit(Form)
        self.lineEdit_17.setGeometry(QtCore.QRect(330, 140, 121, 21))
        self.lineEdit_17.setReadOnly(True)
        self.lineEdit_17.setObjectName("lineEdit_17")
        self.pbGoBaseplate = QtWidgets.QPushButton(Form)
        self.pbGoBaseplate.setGeometry(QtCore.QRect(530, 140, 51, 21))
        self.pbGoBaseplate.setObjectName("pbGoBaseplate")
        self.sbBaseplate = QtWidgets.QSpinBox(Form)
        self.sbBaseplate.setGeometry(QtCore.QRect(450, 140, 81, 21))
        self.sbBaseplate.setReadOnly(True)
        self.sbBaseplate.setMinimum(-1)
        self.sbBaseplate.setMaximum(2147483647)
        self.sbBaseplate.setObjectName("sbBaseplate")
        self.sbStepPcb = QtWidgets.QSpinBox(Form)
        self.sbStepPcb.setGeometry(QtCore.QRect(420, 360, 81, 21))
        self.sbStepPcb.setReadOnly(True)
        self.sbStepPcb.setMinimum(-1)
        self.sbStepPcb.setMaximum(2147483647)
        self.sbStepPcb.setObjectName("sbStepPcb")
        self.lineEdit_18 = QtWidgets.QLineEdit(Form)
        self.lineEdit_18.setGeometry(QtCore.QRect(330, 360, 91, 21))
        self.lineEdit_18.setReadOnly(True)
        self.lineEdit_18.setObjectName("lineEdit_18")
        self.pbGoStepPcb = QtWidgets.QPushButton(Form)
        self.pbGoStepPcb.setGeometry(QtCore.QRect(500, 360, 51, 21))
        self.pbGoStepPcb.setObjectName("pbGoStepPcb")
        self.lineEdit_19 = QtWidgets.QLineEdit(Form)
        self.lineEdit_19.setGeometry(QtCore.QRect(330, 210, 181, 21))
        self.lineEdit_19.setReadOnly(True)
        self.lineEdit_19.setObjectName("lineEdit_19")
        self.lineEdit_20 = QtWidgets.QLineEdit(Form)
        self.lineEdit_20.setGeometry(QtCore.QRect(330, 230, 181, 21))
        self.lineEdit_20.setReadOnly(True)
        self.lineEdit_20.setObjectName("lineEdit_20")
        self.lineEdit_21 = QtWidgets.QLineEdit(Form)
        self.lineEdit_21.setGeometry(QtCore.QRect(330, 250, 181, 21))
        self.lineEdit_21.setReadOnly(True)
        self.lineEdit_21.setObjectName("lineEdit_21")
        self.lineEdit_22 = QtWidgets.QLineEdit(Form)
        self.lineEdit_22.setGeometry(QtCore.QRect(330, 270, 181, 21))
        self.lineEdit_22.setReadOnly(True)
        self.lineEdit_22.setObjectName("lineEdit_22")
        self.lineEdit_23 = QtWidgets.QLineEdit(Form)
        self.lineEdit_23.setGeometry(QtCore.QRect(330, 290, 181, 21))
        self.lineEdit_23.setReadOnly(True)
        self.lineEdit_23.setObjectName("lineEdit_23")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(330, 190, 181, 16))
        self.label_3.setObjectName("label_3")
        self.dsbOffsetTranslation = QtWidgets.QDoubleSpinBox(Form)
        self.dsbOffsetTranslation.setGeometry(QtCore.QRect(510, 210, 81, 21))
        self.dsbOffsetTranslation.setReadOnly(True)
        self.dsbOffsetTranslation.setMinimum(-1.0)
        self.dsbOffsetTranslation.setMaximum(2147483647.0)
        self.dsbOffsetTranslation.setSingleStep(0.1)
        self.dsbOffsetTranslation.setObjectName("dsbOffsetTranslation")
        self.dsbOffsetRotation = QtWidgets.QDoubleSpinBox(Form)
        self.dsbOffsetRotation.setGeometry(QtCore.QRect(510, 230, 81, 21))
        self.dsbOffsetRotation.setReadOnly(True)
        self.dsbOffsetRotation.setMinimum(-1.0)
        self.dsbOffsetRotation.setMaximum(2147483647.0)
        self.dsbOffsetRotation.setSingleStep(0.1)
        self.dsbOffsetRotation.setObjectName("dsbOffsetRotation")
        self.dsbFlatness = QtWidgets.QDoubleSpinBox(Form)
        self.dsbFlatness.setGeometry(QtCore.QRect(510, 250, 81, 21))
        self.dsbFlatness.setReadOnly(True)
        self.dsbFlatness.setMinimum(-1.0)
        self.dsbFlatness.setMaximum(2147483647.0)
        self.dsbFlatness.setSingleStep(0.1)
        self.dsbFlatness.setObjectName("dsbFlatness")
        self.cbCheckCracks = QtWidgets.QComboBox(Form)
        self.cbCheckCracks.setGeometry(QtCore.QRect(510, 270, 81, 20))
        self.cbCheckCracks.setObjectName("cbCheckCracks")
        self.cbCheckCracks.addItem("")
        self.cbCheckCracks.addItem("")
        self.cbCheckGlueSpill = QtWidgets.QComboBox(Form)
        self.cbCheckGlueSpill.setGeometry(QtCore.QRect(510, 290, 81, 20))
        self.cbCheckGlueSpill.setObjectName("cbCheckGlueSpill")
        self.cbCheckGlueSpill.addItem("")
        self.cbCheckGlueSpill.addItem("")
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setGeometry(QtCore.QRect(330, 10, 271, 51))
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName("label_4")

        self.retranslateUi(Form)
        self.cbChirality.setCurrentIndex(-1)
        self.cbShape.setCurrentIndex(-1)
        self.cbInstitution.setCurrentIndex(-1)
        self.cbCheckCracks.setCurrentIndex(-1)
        self.cbCheckGlueSpill.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pbGoShipment.setText(_translate("Form", "Go to selected"))
        self.lineEdit_9.setText(_translate("Form", "Location"))
        self.lineEdit_3.setText(_translate("Form", "Shipments"))
        self.listShipments.setToolTip(_translate("Form", "ID (date sent) (SENDER to RECEIVER)"))
        self.lineEdit_10.setText(_translate("Form", "Shape"))
        self.lineEdit_6.setText(_translate("Form", "Channels"))
        self.pbAddComment.setText(_translate("Form", "Add comment"))
        self.lineEdit_14.setText(_translate("Form", "Comments"))
        self.pbDeleteComment.setText(_translate("Form", "Delete selected"))
        self.lineEdit_15.setText(_translate("Form", "Chirality"))
        self.cbChirality.setItemText(0, _translate("Form", "achiral"))
        self.cbChirality.setItemText(1, _translate("Form", "left"))
        self.cbChirality.setItemText(2, _translate("Form", "right"))
        self.lineEdit_4.setText(_translate("Form", "Thickness (mm)"))
        self.cbShape.setItemText(0, _translate("Form", "full"))
        self.cbShape.setItemText(1, _translate("Form", "half"))
        self.cbShape.setItemText(2, _translate("Form", "five"))
        self.cbShape.setItemText(3, _translate("Form", "three"))
        self.cbShape.setItemText(4, _translate("Form", "semi"))
        self.cbShape.setItemText(5, _translate("Form", "semi(-)"))
        self.cbShape.setItemText(6, _translate("Form", "choptwo"))
        self.lineEdit_52.setText(_translate("Form", "Institution"))
        self.cbInstitution.setItemText(0, _translate("Form", "CERN"))
        self.cbInstitution.setItemText(1, _translate("Form", "FNAL"))
        self.cbInstitution.setItemText(2, _translate("Form", "UCSB"))
        self.cbInstitution.setItemText(3, _translate("Form", "UMN"))
        self.cbInstitution.setItemText(4, _translate("Form", "NTU"))
        self.lineEdit_38.setToolTip(_translate("Form", "height difference between highest and lowers corners"))
        self.lineEdit_38.setText(_translate("Form", "User name"))
        self.pbSave.setText(_translate("Form", "Save"))
        self.pbEdit.setText(_translate("Form", "Edit"))
        self.pbCancel.setText(_translate("Form", "Cancel"))
        self.lineEdit.setText(_translate("Form", "Protomodule ID"))
        self.pbGoStepSensor.setText(_translate("Form", "Go to"))
        self.pbGoModule.setText(_translate("Form", "Go to"))
        self.lineEdit_12.setText(_translate("Form", "Sensor"))
        self.lineEdit_8.setText(_translate("Form", "On module"))
        self.lineEdit_13.setText(_translate("Form", "Placement step"))
        self.pbGoSensor.setText(_translate("Form", "Go to"))
        self.label.setText(_translate("Form", "PCB placement"))
        self.label_2.setText(_translate("Form", "Sensor placement"))
        self.lineEdit_17.setText(_translate("Form", "Baseplate"))
        self.pbGoBaseplate.setText(_translate("Form", "Go to"))
        self.lineEdit_18.setText(_translate("Form", "PCB step"))
        self.pbGoStepPcb.setText(_translate("Form", "Go to"))
        self.lineEdit_19.setText(_translate("Form", "Translational offset (μm)"))
        self.lineEdit_20.setText(_translate("Form", "Rotational offset (°)"))
        self.lineEdit_21.setText(_translate("Form", "Flatness (mm)"))
        self.lineEdit_22.setText(_translate("Form", "Check for cracks"))
        self.lineEdit_23.setText(_translate("Form", "Check glue spillage"))
        self.label_3.setText(_translate("Form", "Protomodule qualification"))
        self.cbCheckCracks.setItemText(0, _translate("Form", "pass"))
        self.cbCheckCracks.setItemText(1, _translate("Form", "fail"))
        self.cbCheckGlueSpill.setItemText(0, _translate("Form", "pass"))
        self.cbCheckGlueSpill.setItemText(1, _translate("Form", "fail"))
        self.label_4.setText(_translate("Form", "Note:  protomodules are automatically created upon completion of a sensor step."))

