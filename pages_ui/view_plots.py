# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'view_plots.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1199, 756)
        self.label_7 = QtWidgets.QLabel(Form)
        self.label_7.setEnabled(True)
        self.label_7.setGeometry(QtCore.QRect(10, 140, 241, 16))
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(Form)
        self.label_8.setEnabled(True)
        self.label_8.setGeometry(QtCore.QRect(450, 140, 241, 16))
        self.label_8.setObjectName("label_8")
        self.frame = QtWidgets.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(10, 440, 351, 201))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.pbAddCommentPCB = QtWidgets.QPushButton(self.frame)
        self.pbAddCommentPCB.setGeometry(QtCore.QRect(0, 180, 111, 21))
        self.pbAddCommentPCB.setObjectName("pbAddCommentPCB")
        self.pteWriteCommentPCB = QtWidgets.QPlainTextEdit(self.frame)
        self.pteWriteCommentPCB.setGeometry(QtCore.QRect(0, 120, 351, 61))
        self.pteWriteCommentPCB.setPlainText("")
        self.pteWriteCommentPCB.setObjectName("pteWriteCommentPCB")
        self.lineEdit_16 = QtWidgets.QLineEdit(self.frame)
        self.lineEdit_16.setGeometry(QtCore.QRect(0, 0, 231, 21))
        self.lineEdit_16.setReadOnly(True)
        self.lineEdit_16.setObjectName("lineEdit_16")
        self.pbDeleteCommentPCB = QtWidgets.QPushButton(self.frame)
        self.pbDeleteCommentPCB.setGeometry(QtCore.QRect(230, 0, 121, 21))
        self.pbDeleteCommentPCB.setObjectName("pbDeleteCommentPCB")
        self.listCommentsPCB = QtWidgets.QListWidget(self.frame)
        self.listCommentsPCB.setGeometry(QtCore.QRect(0, 20, 351, 91))
        self.listCommentsPCB.setObjectName("listCommentsPCB")
        self.frame_2 = QtWidgets.QFrame(Form)
        self.frame_2.setGeometry(QtCore.QRect(450, 440, 351, 201))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.pbDeleteCommentMod = QtWidgets.QPushButton(self.frame_2)
        self.pbDeleteCommentMod.setGeometry(QtCore.QRect(230, 0, 121, 21))
        self.pbDeleteCommentMod.setObjectName("pbDeleteCommentMod")
        self.pteWriteCommentMod = QtWidgets.QPlainTextEdit(self.frame_2)
        self.pteWriteCommentMod.setGeometry(QtCore.QRect(0, 120, 351, 61))
        self.pteWriteCommentMod.setPlainText("")
        self.pteWriteCommentMod.setObjectName("pteWriteCommentMod")
        self.lineEdit_19 = QtWidgets.QLineEdit(self.frame_2)
        self.lineEdit_19.setGeometry(QtCore.QRect(0, 0, 231, 21))
        self.lineEdit_19.setReadOnly(True)
        self.lineEdit_19.setObjectName("lineEdit_19")
        self.pbAddCommentMod = QtWidgets.QPushButton(self.frame_2)
        self.pbAddCommentMod.setGeometry(QtCore.QRect(0, 180, 111, 21))
        self.pbAddCommentMod.setObjectName("pbAddCommentMod")
        self.listCommentsMod = QtWidgets.QListWidget(self.frame_2)
        self.listCommentsMod.setGeometry(QtCore.QRect(0, 20, 351, 91))
        self.listCommentsMod.setObjectName("listCommentsMod")
        self.frame_3 = QtWidgets.QFrame(Form)
        self.frame_3.setGeometry(QtCore.QRect(450, 160, 351, 211))
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.pbDeleteFilesMod = QtWidgets.QPushButton(self.frame_3)
        self.pbDeleteFilesMod.setGeometry(QtCore.QRect(220, 0, 131, 21))
        self.pbDeleteFilesMod.setObjectName("pbDeleteFilesMod")
        self.listFilesMod = QtWidgets.QListWidget(self.frame_3)
        self.listFilesMod.setGeometry(QtCore.QRect(0, 20, 351, 111))
        self.listFilesMod.setObjectName("listFilesMod")
        self.lineEdit_18 = QtWidgets.QLineEdit(self.frame_3)
        self.lineEdit_18.setGeometry(QtCore.QRect(1, 0, 221, 21))
        self.lineEdit_18.setReadOnly(True)
        self.lineEdit_18.setObjectName("lineEdit_18")
        self.pbAddPedTestMod = QtWidgets.QPushButton(self.frame_3)
        self.pbAddPedTestMod.setGeometry(QtCore.QRect(20, 140, 141, 31))
        self.pbAddPedTestMod.setObjectName("pbAddPedTestMod")
        self.pbAddPedPlotsMod = QtWidgets.QPushButton(self.frame_3)
        self.pbAddPedPlotsMod.setGeometry(QtCore.QRect(180, 140, 141, 31))
        self.pbAddPedPlotsMod.setObjectName("pbAddPedPlotsMod")
        self.pbAddIVTestMod = QtWidgets.QPushButton(self.frame_3)
        self.pbAddIVTestMod.setGeometry(QtCore.QRect(20, 170, 141, 31))
        self.pbAddIVTestMod.setObjectName("pbAddIVTestMod")
        self.frame_4 = QtWidgets.QFrame(Form)
        self.frame_4.setGeometry(QtCore.QRect(10, 160, 351, 181))
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.pbAddPedTestPCB = QtWidgets.QPushButton(self.frame_4)
        self.pbAddPedTestPCB.setGeometry(QtCore.QRect(90, 140, 161, 31))
        self.pbAddPedTestPCB.setObjectName("pbAddPedTestPCB")
        self.listFilesPCB = QtWidgets.QListWidget(self.frame_4)
        self.listFilesPCB.setGeometry(QtCore.QRect(0, 20, 351, 111))
        self.listFilesPCB.setObjectName("listFilesPCB")
        self.lineEdit_17 = QtWidgets.QLineEdit(self.frame_4)
        self.lineEdit_17.setGeometry(QtCore.QRect(1, 0, 221, 21))
        self.lineEdit_17.setReadOnly(True)
        self.lineEdit_17.setObjectName("lineEdit_17")
        self.pbDeleteFilesPCB = QtWidgets.QPushButton(self.frame_4)
        self.pbDeleteFilesPCB.setGeometry(QtCore.QRect(220, 0, 131, 21))
        self.pbDeleteFilesPCB.setObjectName("pbDeleteFilesPCB")
        self.frame_6 = QtWidgets.QFrame(Form)
        self.frame_6.setGeometry(QtCore.QRect(450, 10, 261, 111))
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_6.setObjectName("frame_6")
        self.pbSaveMod = QtWidgets.QPushButton(self.frame_6)
        self.pbSaveMod.setGeometry(QtCore.QRect(50, 60, 71, 21))
        self.pbSaveMod.setObjectName("pbSaveMod")
        self.pbEditMod = QtWidgets.QPushButton(self.frame_6)
        self.pbEditMod.setGeometry(QtCore.QRect(130, 30, 71, 21))
        self.pbEditMod.setObjectName("pbEditMod")
        self.pbCancelMod = QtWidgets.QPushButton(self.frame_6)
        self.pbCancelMod.setGeometry(QtCore.QRect(130, 60, 71, 21))
        self.pbCancelMod.setObjectName("pbCancelMod")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.frame_6)
        self.lineEdit_3.setGeometry(QtCore.QRect(1, 1, 81, 19))
        self.lineEdit_3.setReadOnly(True)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.leIDMod = QtWidgets.QLineEdit(self.frame_6)
        self.leIDMod.setGeometry(QtCore.QRect(80, 0, 111, 20))
        self.leIDMod.setText("")
        self.leIDMod.setReadOnly(True)
        self.leIDMod.setObjectName("leIDMod")
        self.leStatusMod = QtWidgets.QLineEdit(self.frame_6)
        self.leStatusMod.setGeometry(QtCore.QRect(80, 90, 171, 20))
        self.leStatusMod.setText("")
        self.leStatusMod.setReadOnly(True)
        self.leStatusMod.setObjectName("leStatusMod")
        self.pbLoadMod = QtWidgets.QPushButton(self.frame_6)
        self.pbLoadMod.setGeometry(QtCore.QRect(50, 30, 71, 21))
        self.pbLoadMod.setObjectName("pbLoadMod")
        self.lineEdit_27 = QtWidgets.QLineEdit(self.frame_6)
        self.lineEdit_27.setGeometry(QtCore.QRect(10, 90, 71, 20))
        self.lineEdit_27.setReadOnly(True)
        self.lineEdit_27.setObjectName("lineEdit_27")
        self.pbGoMod = QtWidgets.QPushButton(self.frame_6)
        self.pbGoMod.setGeometry(QtCore.QRect(190, 0, 71, 21))
        self.pbGoMod.setObjectName("pbGoMod")
        self.frame_7 = QtWidgets.QFrame(Form)
        self.frame_7.setGeometry(QtCore.QRect(10, 10, 261, 111))
        self.frame_7.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_7.setObjectName("frame_7")
        self.pbSavePCB = QtWidgets.QPushButton(self.frame_7)
        self.pbSavePCB.setGeometry(QtCore.QRect(50, 60, 71, 21))
        self.pbSavePCB.setObjectName("pbSavePCB")
        self.pbEditPCB = QtWidgets.QPushButton(self.frame_7)
        self.pbEditPCB.setGeometry(QtCore.QRect(130, 30, 71, 21))
        self.pbEditPCB.setObjectName("pbEditPCB")
        self.pbCancelPCB = QtWidgets.QPushButton(self.frame_7)
        self.pbCancelPCB.setGeometry(QtCore.QRect(130, 60, 71, 21))
        self.pbCancelPCB.setObjectName("pbCancelPCB")
        self.lineEdit_4 = QtWidgets.QLineEdit(self.frame_7)
        self.lineEdit_4.setGeometry(QtCore.QRect(1, 1, 91, 19))
        self.lineEdit_4.setReadOnly(True)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.leIDPCB = QtWidgets.QLineEdit(self.frame_7)
        self.leIDPCB.setGeometry(QtCore.QRect(90, 0, 101, 20))
        self.leIDPCB.setText("")
        self.leIDPCB.setReadOnly(True)
        self.leIDPCB.setObjectName("leIDPCB")
        self.leStatusPCB = QtWidgets.QLineEdit(self.frame_7)
        self.leStatusPCB.setGeometry(QtCore.QRect(80, 90, 171, 20))
        self.leStatusPCB.setText("")
        self.leStatusPCB.setReadOnly(True)
        self.leStatusPCB.setObjectName("leStatusPCB")
        self.pbLoadPCB = QtWidgets.QPushButton(self.frame_7)
        self.pbLoadPCB.setGeometry(QtCore.QRect(50, 30, 71, 21))
        self.pbLoadPCB.setObjectName("pbLoadPCB")
        self.lineEdit_28 = QtWidgets.QLineEdit(self.frame_7)
        self.lineEdit_28.setGeometry(QtCore.QRect(10, 90, 71, 20))
        self.lineEdit_28.setReadOnly(True)
        self.lineEdit_28.setObjectName("lineEdit_28")
        self.pbGoPCB = QtWidgets.QPushButton(self.frame_7)
        self.pbGoPCB.setGeometry(QtCore.QRect(190, 0, 71, 21))
        self.pbGoPCB.setObjectName("pbGoPCB")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_7.setText(_translate("Form", "PCB plots"))
        self.label_8.setText(_translate("Form", "Module plots"))
        self.pbAddCommentPCB.setText(_translate("Form", "Add comment"))
        self.lineEdit_16.setText(_translate("Form", "Hexaboard comments"))
        self.pbDeleteCommentPCB.setText(_translate("Form", "Delete selected"))
        self.pbDeleteCommentMod.setText(_translate("Form", "Delete selected"))
        self.lineEdit_19.setText(_translate("Form", "Module comments"))
        self.pbAddCommentMod.setText(_translate("Form", "Add comment"))
        self.pbDeleteFilesMod.setText(_translate("Form", "Delete selected"))
        self.listFilesMod.setToolTip(_translate("Form", "ID (date sent) (SENDER to RECEIVER)"))
        self.lineEdit_18.setText(_translate("Form", "Module files"))
        self.pbAddPedTestMod.setText(_translate("Form", "Add pedestal_test"))
        self.pbAddPedPlotsMod.setText(_translate("Form", "Add pedestal_plots"))
        self.pbAddIVTestMod.setText(_translate("Form", "Add iv_test"))
        self.pbAddPedTestPCB.setText(_translate("Form", "Add pedestal_test"))
        self.listFilesPCB.setToolTip(_translate("Form", "ID (date sent) (SENDER to RECEIVER)"))
        self.lineEdit_17.setText(_translate("Form", "Hexaboard files"))
        self.pbDeleteFilesPCB.setText(_translate("Form", "Delete selected"))
        self.pbSaveMod.setText(_translate("Form", "Save"))
        self.pbEditMod.setText(_translate("Form", "Edit"))
        self.pbCancelMod.setText(_translate("Form", "Cancel"))
        self.lineEdit_3.setText(_translate("Form", "Module ID"))
        self.pbLoadMod.setText(_translate("Form", "Load"))
        self.lineEdit_27.setText(_translate("Form", "Status:"))
        self.pbGoMod.setText(_translate("Form", "Go to"))
        self.pbSavePCB.setText(_translate("Form", "Save"))
        self.pbEditPCB.setText(_translate("Form", "Edit"))
        self.pbCancelPCB.setText(_translate("Form", "Cancel"))
        self.lineEdit_4.setText(_translate("Form", "Hexaboard ID"))
        self.pbLoadPCB.setText(_translate("Form", "Load"))
        self.lineEdit_28.setText(_translate("Form", "Status:"))
        self.pbGoPCB.setText(_translate("Form", "Go to"))
