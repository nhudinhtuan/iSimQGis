# -*- coding: utf-8 -*-
"""
/***************************************************************************
 iSimGis
                                 A QGIS plugin
 iSim converter
                              -------------------
        begin                : 2014-02-03
        copyright            : (C) 2014 by nhudinhtuan
        email                : nhudinhtuan@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import QgsMessageBar, QgsMapToolEmitPoint, QgsMapToolPan
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from converter_dialog import ConverterDialog
from os import listdir, path, getenv, getcwd
#import from others
import shutil
from xmlToShapefile import XmlToShapefile
from actionHandler import ActionHandler

class iSimGis:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # reference to map canvas
        self.canvas = self.iface.mapCanvas() 
        # this QGIS tool emits as QgsPoint after each click on the map canvas
        self.clickTool = QgsMapToolEmitPoint(self.canvas)
        # create a pan tool
        self.toolPan = QgsMapToolPan(self.canvas)
        #comverter dialog
        self.converterdlg = None
        # initialize plugin directory
        self.plugin_dir = path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = path.join(self.plugin_dir, 'i18n', 'isimgis_{}.qm'.format(locale))
        if path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        QSettings().setValue( "/Projections/defaultBehaviour", "useGlobal" )
        # crs
        self.crs = QgsCoordinateReferenceSystem(3168)

    def initGui(self):

        self.new_action = QAction(
            QIcon(":/plugins/isimgis/icons/notepad-icon.png"),
            u"create an empty shapefile directory", self.iface.mainWindow())

        self.open_action = QAction(
            QIcon(":/plugins/isimgis/icons/open.png"),
            u"open iSim shapefile directory", self.iface.mainWindow())

        self.converter_action = QAction(
            QIcon(":/plugins/isimgis/icons/converter.png"),
            u"iSim converter", self.iface.mainWindow())

        self.add_action = QAction(
            QIcon(":/plugins/isimgis/icons/add.png"),
            u"add features to current active layer.", self.iface.mainWindow())

        self.delete_action = QAction(
            QIcon(":/plugins/isimgis/icons/delete.png"),
            u"delete features from current active layer.", self.iface.mainWindow())

        # connect the action to the run method
        self.new_action.triggered.connect(self.new)
        self.open_action.triggered.connect(self.open)
        self.converter_action.triggered.connect(self.converter)
        self.add_action.triggered.connect(self.addFeature)
        self.delete_action.triggered.connect(self.deleteFeature)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.new_action)
        self.iface.addToolBarIcon(self.open_action)
        self.iface.addToolBarIcon(self.converter_action)
        self.iface.addToolBarIcon(self.add_action)
        self.iface.addToolBarIcon(self.delete_action)
        self.iface.addPluginToMenu(u"&iSimGis", self.new_action)
        self.iface.addPluginToMenu(u"&iSimGis", self.open_action)
        self.iface.addPluginToMenu(u"&iSimGis", self.converter_action)
        self.iface.addPluginToMenu(u"&iSimGis", self.add_action)
        self.iface.addPluginToMenu(u"&iSimGis", self.delete_action)

        self.clickTool.canvasClicked.connect(self.addNewFeature)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&iSimGis", self.open_action)
        self.iface.removePluginMenu(u"&iSimGis", self.converter_action)
        self.iface.removePluginMenu(u"&iSimGis", self.add_action)
        self.iface.removeToolBarIcon(self.open_action)
        self.iface.removeToolBarIcon(self.converter_action)
        self.iface.removeToolBarIcon(self.add_action)

    def new(self):
        sh_dir = QFileDialog.getExistingDirectory(None, 'Create new iSim Shapefile Directory', getenv('HOME'))
        if sh_dir == "":
            return
        prefix = path.basename(sh_dir)

        # find the template
        current_full_path = path.realpath(__file__)
        current_dir, current_file = path.split(current_full_path)
        template_dir = path.join(current_dir, "template")

        xml_path = path.join(template_dir, "template.xml")
        xmlToShapefile = XmlToShapefile(xml_path, sh_dir, ["x", "y"])
        xmlToShapefile.run()

        # open layer
        self.open(sh_dir)


    def open(self, sh_dir):
        if isinstance(sh_dir, bool) or sh_dir == "":
            sh_dir = QFileDialog.getExistingDirectory(None, 'Open iSim Shapefile Directory', getenv('HOME'))
            if sh_dir == "":
                return
        for filenames in listdir(sh_dir):
            full_path = path.join(sh_dir, filenames)
            names = filenames.split(".")
            if path.isfile(full_path) and names[1] == "shp":
                layer = QgsVectorLayer(full_path, names[0], "ogr")
                if layer.isValid():
                    layer.setCrs(self.crs)
                    QgsMapLayerRegistry.instance().addMapLayer(layer)

    # open convert dialog
    def converter(self):
        if self.converterdlg is not None:
            self.converterdlg.raise_()
            self.converterdlg.activateWindow()
            return
        self.converterdlg = ConverterDialog()
        self.converterdlg.open_sig.connect(self.open)
        self.converterdlg.show()
        # Run the dialog event loop
        self.converterdlg.exec_()
        self.converterdlg = None

    #return isValid, sh_dir, layer_name 
    def checkActiveLayerInfo(self):
        active_layer = self.iface.activeLayer()
        if active_layer is None:
            return False, "", ""
        uri = active_layer.dataProvider().dataSourceUri()
        sh_dir = path.dirname(uri)
        layer_name = path.basename(uri).split(".")[0]
        data_file = path.join(sh_dir, "data.xml")
        if path.isfile(data_file):
            return True, sh_dir, layer_name
        else:
            return False, sh_dir, layer_name

    def addFeature(self):
        # make our clickTool the tool that we'll use for now
        self.canvas.setMapTool(self.clickTool)
        isValidLayer, sh_dir, layer_name = self.checkActiveLayerInfo()
        if not isValidLayer:
            QMessageBox.critical(self.iface.mainWindow(),"iSim Error", "There is no active layer or the active layer is not iSim shapefile layer.")
            return

        '''
        #self.iface.messageBar().pushMessage("Info", "there is no active layer, so you can not add any feature!", level=QgsMessageBar.CRITICAL)
        uri = active_layer.dataProvider().dataSourceUri()
        sh_dir = path.dirname(uri)
        filename = path.basename(uri).split(".")[0]
        data_file = path.join(sh_dir, "data.xml")
        if path.isfile(data_file):
            QgsMessageLog.logMessage("find data file data.xml - %s" % filename)
        else:
            QgsMessageLog.logMessage("can not file data.xml")
        '''
        return

    def addNewFeature(self, point, button):
        QMessageBox.information(self.iface.mainWindow(),"Info", "X,Y = %s,%s" % (str(point.x()),str(point.y())))
        self.canvas.setMapTool(self.toolPan)

    def deleteFeature(self):
        # verify the current layer
        isValidLayer, sh_dir, active_layer_name = self.checkActiveLayerInfo()
        if not isValidLayer:
            QMessageBox.critical(self.iface.mainWindow(),"iSim Error", "The active layer is not iSim shapefile layer.")
            return

        # make sure there is a selected feature
        active_layer = self.iface.activeLayer()
        selected_features = active_layer.selectedFeatures()
        if len(selected_features) == 0:
            QMessageBox.critical(self.iface.mainWindow(),"iSim Error", "No feature is selected.")
            return

        # confirm message
        reply = QMessageBox.question(self.iface.mainWindow(), "Are you sure?", "Are you sure to delete the selected features ? It is NOT possible to undo this action.", 
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No);
        if reply == QMessageBox.No:
            return

        handler = ActionHandler(sh_dir, self.canvas)
        # remove data dependency
        handler.delete(selected_features)
        handler.save()
            
        self.canvas.refresh()
        


