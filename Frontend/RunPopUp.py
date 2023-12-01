# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'runpopup.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_RunOptionsDialog(object):
    def setupUi(self, RunOptionsDialog):
        RunOptionsDialog.setObjectName("RunOptionsDialog")
        RunOptionsDialog.resize(400, 300)
        self.mainVerticalLayout = QtWidgets.QVBoxLayout(RunOptionsDialog)
        self.mainVerticalLayout.setObjectName("mainVerticalLayout")
        self.headerLabel = QtWidgets.QLabel(RunOptionsDialog)
        self.headerLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.headerLabel.setObjectName("headerLabel")
        self.mainVerticalLayout.addWidget(self.headerLabel)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBoxType = QtWidgets.QGroupBox(RunOptionsDialog)
        self.groupBoxType.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBoxType.setFlat(True)
        self.groupBoxType.setObjectName("groupBoxType")
        self.verticalLayoutType = QtWidgets.QVBoxLayout(self.groupBoxType)
        self.verticalLayoutType.setContentsMargins(10, 10, 10, 10)
        self.verticalLayoutType.setSpacing(10)
        self.verticalLayoutType.setObjectName("verticalLayoutType")
        self.radioButtonSteps = QtWidgets.QRadioButton(self.groupBoxType)
        self.radioButtonSteps.setObjectName("radioButtonSteps")
        self.verticalLayoutType.addWidget(self.radioButtonSteps)
        self.radioButtonFiles = QtWidgets.QRadioButton(self.groupBoxType)
        self.radioButtonFiles.setObjectName("radioButtonFiles")
        self.verticalLayoutType.addWidget(self.radioButtonFiles)
        self.radioButtonAxisControl = QtWidgets.QRadioButton(self.groupBoxType)
        self.radioButtonAxisControl.setObjectName("radioButtonAxisControl")
        self.verticalLayoutType.addWidget(self.radioButtonAxisControl)
        self.horizontalLayout.addWidget(self.groupBoxType)
        self.groupBoxFiles = QtWidgets.QGroupBox(RunOptionsDialog)
        self.groupBoxFiles.setFlat(True)
        self.groupBoxFiles.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBoxFiles.setObjectName("groupBoxFiles")
        self.verticalLayoutFiles = QtWidgets.QVBoxLayout(self.groupBoxFiles)
        self.verticalLayoutFiles.setSpacing(6)
        self.verticalLayoutFiles.setObjectName("verticalLayoutFiles")
        self.checkBoxAllFiles = QtWidgets.QCheckBox(self.groupBoxFiles)
        self.checkBoxAllFiles.setObjectName("checkBoxAllFiles")
        self.verticalLayoutFiles.addWidget(self.checkBoxAllFiles)
        self.horizontalLayout.addWidget(self.groupBoxFiles)
        self.mainVerticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayoutButtons = QtWidgets.QHBoxLayout()
        self.horizontalLayoutButtons.setObjectName("horizontalLayoutButtons")
        self.pushButtonStart = QtWidgets.QPushButton(RunOptionsDialog)
        self.pushButtonStart.setObjectName("pushButtonStart")
        self.horizontalLayoutButtons.addWidget(self.pushButtonStart)
        self.pushButtonCancel = QtWidgets.QPushButton(RunOptionsDialog)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.horizontalLayoutButtons.addWidget(self.pushButtonCancel)
        self.mainVerticalLayout.addLayout(self.horizontalLayoutButtons)

        self.fileListWidget = QtWidgets.QListWidget(self.groupBoxFiles)
        self.fileListWidget.setObjectName("fileListWidget")
        self.verticalLayoutFiles.addWidget(self.fileListWidget)

        self.retranslateUi(RunOptionsDialog)
        QtCore.QMetaObject.connectSlotsByName(RunOptionsDialog)

    def retranslateUi(self, RunOptionsDialog):
        _translate = QtCore.QCoreApplication.translate
        RunOptionsDialog.setWindowTitle(_translate("RunOptionsDialog", "Run Options"))
        self.headerLabel.setText(_translate("RunOptionsDialog", "Run Options"))
        self.groupBoxType.setTitle(_translate("RunOptionsDialog", "Type"))
        self.radioButtonSteps.setText(_translate("RunOptionsDialog", "Steps"))
        self.radioButtonFiles.setText(_translate("RunOptionsDialog", "Files"))
        self.radioButtonAxisControl.setText(_translate("RunOptionsDialog", "Axis Control"))
        self.groupBoxFiles.setTitle(_translate("RunOptionsDialog", "Select File(s)"))
        self.checkBoxAllFiles.setText(_translate("RunOptionsDialog", "All Files"))
        self.pushButtonStart.setText(_translate("RunOptionsDialog", "Start"))
        self.pushButtonCancel.setText(_translate("RunOptionsDialog", "Cancel"))
