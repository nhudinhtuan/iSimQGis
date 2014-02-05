# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_converter.ui'
#
# Created: Wed Feb 05 22:01:55 2014
#      by: PyQt4 UI code generator 4.10.3
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

class Ui_Converter(object):
    def setupUi(self, Converter):
        Converter.setObjectName(_fromUtf8("Converter"))
        Converter.setEnabled(True)
        Converter.resize(656, 283)
        Converter.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        Converter.setWindowTitle(_fromUtf8("iSimGis Converter"))
        Converter.setWindowOpacity(4.0)
        Converter.setToolTip(_fromUtf8(""))
        Converter.setStatusTip(_fromUtf8(""))
        Converter.setSizeGripEnabled(False)
        self.tabWidget = QtGui.QTabWidget(Converter)
        self.tabWidget.setGeometry(QtCore.QRect(0, 10, 661, 281))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Tahoma"))
        font.setPointSize(10)
        self.tabWidget.setFont(font)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.XMLtoSH = QtGui.QWidget()
        self.XMLtoSH.setObjectName(_fromUtf8("XMLtoSH"))
        self.xmlsh_xml_label = QtGui.QLabel(self.XMLtoSH)
        self.xmlsh_xml_label.setGeometry(QtCore.QRect(20, 20, 131, 31))
        self.xmlsh_xml_label.setObjectName(_fromUtf8("xmlsh_xml_label"))
        self.xmlsh_sh_path = QtGui.QLineEdit(self.XMLtoSH)
        self.xmlsh_sh_path.setEnabled(False)
        self.xmlsh_sh_path.setGeometry(QtCore.QRect(150, 71, 421, 31))
        self.xmlsh_sh_path.setObjectName(_fromUtf8("xmlsh_sh_path"))
        self.xmlsh_sh_label = QtGui.QLabel(self.XMLtoSH)
        self.xmlsh_sh_label.setGeometry(QtCore.QRect(20, 80, 131, 16))
        self.xmlsh_sh_label.setObjectName(_fromUtf8("xmlsh_sh_label"))
        self.xmlsh_xml_path = QtGui.QLineEdit(self.XMLtoSH)
        self.xmlsh_xml_path.setEnabled(False)
        self.xmlsh_xml_path.setGeometry(QtCore.QRect(150, 20, 421, 31))
        self.xmlsh_xml_path.setObjectName(_fromUtf8("xmlsh_xml_path"))
        self.xmlsh_sh_browser = QtGui.QToolButton(self.XMLtoSH)
        self.xmlsh_sh_browser.setGeometry(QtCore.QRect(580, 71, 41, 31))
        self.xmlsh_sh_browser.setObjectName(_fromUtf8("xmlsh_sh_browser"))
        self.xmlsh_xml_browser = QtGui.QToolButton(self.XMLtoSH)
        self.xmlsh_xml_browser.setGeometry(QtCore.QRect(580, 20, 41, 31))
        self.xmlsh_xml_browser.setObjectName(_fromUtf8("xmlsh_xml_browser"))
        self.xmlsh_converter_but = QtGui.QPushButton(self.XMLtoSH)
        self.xmlsh_converter_but.setGeometry(QtCore.QRect(230, 130, 181, 31))
        self.xmlsh_converter_but.setObjectName(_fromUtf8("xmlsh_converter_but"))
        self.xmlsh_progress = QtGui.QProgressBar(self.XMLtoSH)
        self.xmlsh_progress.setGeometry(QtCore.QRect(50, 190, 561, 23))
        self.xmlsh_progress.setProperty("value", 0)
        self.xmlsh_progress.setObjectName(_fromUtf8("xmlsh_progress"))
        self.xmlsh_status = QtGui.QLabel(self.XMLtoSH)
        self.xmlsh_status.setGeometry(QtCore.QRect(20, 190, 611, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Tahoma"))
        font.setPointSize(10)
        font.setItalic(True)
        self.xmlsh_status.setFont(font)
        self.xmlsh_status.setText(_fromUtf8(""))
        self.xmlsh_status.setAlignment(QtCore.Qt.AlignCenter)
        self.xmlsh_status.setObjectName(_fromUtf8("xmlsh_status"))
        self.tabWidget.addTab(self.XMLtoSH, _fromUtf8(""))
        self.SHtoXML = QtGui.QWidget()
        self.SHtoXML.setObjectName(_fromUtf8("SHtoXML"))
        self.shxml_sh_browser = QtGui.QToolButton(self.SHtoXML)
        self.shxml_sh_browser.setGeometry(QtCore.QRect(580, 20, 41, 31))
        self.shxml_sh_browser.setObjectName(_fromUtf8("shxml_sh_browser"))
        self.shxml_xml_path = QtGui.QLineEdit(self.SHtoXML)
        self.shxml_xml_path.setEnabled(False)
        self.shxml_xml_path.setGeometry(QtCore.QRect(150, 71, 421, 31))
        self.shxml_xml_path.setObjectName(_fromUtf8("shxml_xml_path"))
        self.shxml_sh_path = QtGui.QLineEdit(self.SHtoXML)
        self.shxml_sh_path.setEnabled(False)
        self.shxml_sh_path.setGeometry(QtCore.QRect(150, 20, 421, 31))
        self.shxml_sh_path.setObjectName(_fromUtf8("shxml_sh_path"))
        self.shxml_xml_label = QtGui.QLabel(self.SHtoXML)
        self.shxml_xml_label.setGeometry(QtCore.QRect(20, 80, 131, 16))
        self.shxml_xml_label.setObjectName(_fromUtf8("shxml_xml_label"))
        self.shxml_status = QtGui.QLabel(self.SHtoXML)
        self.shxml_status.setGeometry(QtCore.QRect(20, 190, 611, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Tahoma"))
        font.setPointSize(10)
        font.setItalic(True)
        self.shxml_status.setFont(font)
        self.shxml_status.setText(_fromUtf8(""))
        self.shxml_status.setAlignment(QtCore.Qt.AlignCenter)
        self.shxml_status.setObjectName(_fromUtf8("shxml_status"))
        self.shxml_xml_browser = QtGui.QToolButton(self.SHtoXML)
        self.shxml_xml_browser.setGeometry(QtCore.QRect(580, 70, 41, 31))
        self.shxml_xml_browser.setObjectName(_fromUtf8("shxml_xml_browser"))
        self.shxml_sh_label = QtGui.QLabel(self.SHtoXML)
        self.shxml_sh_label.setGeometry(QtCore.QRect(20, 20, 131, 31))
        self.shxml_sh_label.setObjectName(_fromUtf8("shxml_sh_label"))
        self.shxml_converter_but = QtGui.QPushButton(self.SHtoXML)
        self.shxml_converter_but.setGeometry(QtCore.QRect(230, 130, 181, 31))
        self.shxml_converter_but.setObjectName(_fromUtf8("shxml_converter_but"))
        self.shxml_progress = QtGui.QProgressBar(self.SHtoXML)
        self.shxml_progress.setGeometry(QtCore.QRect(50, 190, 561, 23))
        self.shxml_progress.setProperty("value", 0)
        self.shxml_progress.setObjectName(_fromUtf8("shxml_progress"))
        self.tabWidget.addTab(self.SHtoXML, _fromUtf8(""))

        self.retranslateUi(Converter)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Converter)

    def retranslateUi(self, Converter):
        self.xmlsh_xml_label.setText(_translate("Converter", "iSim XML File :", None))
        self.xmlsh_sh_label.setText(_translate("Converter", "Destination Dir :", None))
        self.xmlsh_sh_browser.setText(_translate("Converter", "...", None))
        self.xmlsh_xml_browser.setText(_translate("Converter", " ...", None))
        self.xmlsh_converter_but.setText(_translate("Converter", "XML TO SHAPEFILES", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.XMLtoSH), _translate("Converter", "XML to Shapefiles", None))
        self.shxml_sh_browser.setText(_translate("Converter", " ...", None))
        self.shxml_xml_label.setText(_translate("Converter", "XML output :", None))
        self.shxml_xml_browser.setText(_translate("Converter", "...", None))
        self.shxml_sh_label.setText(_translate("Converter", "Shapefiles Dir :", None))
        self.shxml_converter_but.setText(_translate("Converter", "SHAPEFILES TO XML", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.SHtoXML), _translate("Converter", "Shapefiles to XML", None))

