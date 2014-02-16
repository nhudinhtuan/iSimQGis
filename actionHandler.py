import os, re
from xml.etree import ElementTree
from xml.dom import minidom
from iSimShapefileIO import TAGS, TYPE
from qgis.core import *

def getSHTypeFromLayername(layer_name):
    parts = layer_name.split("_")
    if len(parts) < 2:
        return 0
    for typeid, tag in TAGS.iteritems():
        if parts[1] == tag:
            return typeid
    return 0

class ActionHandler():
    def __init__(self, sh_dir, canvas):
        ElementTree.register_namespace('geo', "http://www.smart.mit.edu/geo")
        self.sh_dir = sh_dir
        self.data_path = os.path.join(sh_dir, "data.xml")
        self.document = ElementTree.parse(self.data_path)
        self.layers = {}
        self.active_layer = canvas.currentLayer()
        self.active_layer_id = 0

        # add all layers
        for layer in canvas.layers():
            self.layers[getSHTypeFromLayername(layer.name())] = layer

        # current layer
        current_layer_name = self.active_layer.name()
        self.prefix = current_layer_name.split("_")[0]
        self.active_layer_id = getSHTypeFromLayername(current_layer_name)

    def getLayer(self, typeId):
        if typeId not in self.layers:
            QgsMessageLog.logMessage("load file type %s"%typeId)
            full_path = os.path.join(self.sh_dir, "%s_%s.shp"%(self.prefix, TAGS[typeId]))
            self.layers[typeId] = QgsVectorLayer(full_path, "%s_isim"%typeId, "ogr")
        return self.layers[typeId]


    def delete(self, features):
        if self.active_layer_id == TYPE.UNINODE:
            self.deleteUniNode(features)
        elif self.active_layer_id == TYPE.MULNODE:
            self.deleteMulNode(features)
        elif self.active_layer_id == TYPE.SEGMENT:
            self.deleteSegment(features)
        else:
            self.deleteSegmentComponents(features)

    def deleteUniNode(self, features):
        ids = {}
        # delete from shapefile
        for feature in features:
            self.active_layer.dataProvider().deleteFeatures([feature.id()])
            attrs = feature.attributes()
            ids[int(attrs[0])] = True
        # delete data dependency
        roadNetwork = self.document.find('GeoSpatial/RoadNetwork')
        nodes = roadNetwork.find('Nodes')
        uniNodeParent = nodes.find('UniNodes')
        uniNodes = uniNodeParent.findall('UniNode')
        if uniNodes is not None:
            for uniNode in uniNodes:
                nodeId = int(uniNode.find("nodeID").text)
                if nodeId in ids:
                    uniNodeParent.remove(uniNode)

    def deleteMulNode(self, features):
        ids = {}
        # delete from shapefile
        for feature in features:
            self.active_layer.dataProvider().deleteFeatures([feature.id()])
            attrs = feature.attributes()
            ids[int(attrs[0])] = True
        roadNetwork = self.document.find('GeoSpatial/RoadNetwork')
        nodes = roadNetwork.find('Nodes')
        mulNodeParent = nodes.find('Intersections')
        mulNodes = mulNodeParent.findall('Intersection')
        if mulNodes is not None:
            for mulNode in mulNodes:
                nodeId = int(mulNode.find("nodeID").text)
                if nodeId in ids:
                    mulNodeParent.remove(mulNode)

    def deleteSegmentComponents(self, features):
        ids = {}
        # delete from shapefile
        for feature in features:
            self.active_layer.dataProvider().deleteFeatures([feature.id()])
            attrs = feature.attributes()
            if not ids.has_key(attrs[0]):
                ids[attrs[0]] = {}
            if attrs[1] not in ids[attrs[0]]:
                ids[attrs[0]][attrs[1]] = {}
            ids[attrs[0]][attrs[1]][attrs[2]] = True

        roadNetwork = self.document.find('GeoSpatial/RoadNetwork')
        linkParent = roadNetwork.find('Links')
        links = linkParent.findall('Link')
        if links is not None:
            for link in links:
                linkId = int(link.find('linkID').text)
                if linkId in ids:
                    segmentParent = link.find('Segments')
                    if segmentParent is not None:
                        segments = segmentParent.findall('Segment')
                        for segment in segments:
                            segmentId = int(segment.find("segmentID").text)
                            if segmentId in ids[linkId]:

                                if self.active_layer_id == TYPE.LANE:
                                    laneParent = segment.find("Lanes")
                                    if laneParent is not None:
                                        lanes = laneParent.findall("Lane")
                                        for lane in lanes:
                                            laneId = int(lane.find("laneID").text)
                                            if laneId in ids[linkId][segmentId]:
                                                laneParent.remove(lane)
                                elif self.active_layer_id == TYPE.LANEEDGE:
                                    laneEdgeParent = segment.find("laneEdgePolylines_cached")
                                    if laneEdgeParent is not None:
                                        laneEdges = laneEdgeParent.findall("laneEdgePolyline_cached")
                                        for laneEdge in laneEdges:
                                            laneEdgeNumber = int(laneEdge.find("laneNumber").text)
                                            if laneEdgeNumber in ids[linkId][segmentId]:
                                                laneEdgeParent.remove(laneEdge)
                                elif self.active_layer_id == TYPE.CROSSING:
                                    obstacles = segment.find("Obstacles")
                                    if obstacles is not None:
                                        crossings = obstacles.findall("Crossing")
                                        for crossing in crossings:
                                            crossing_id = int(crossing.find("id").text)
                                            if crossing_id in ids[linkId][segmentId]:
                                                obstacles.remove(crossing)
                                elif self.active_layer_id == TYPE.BUSSTOP:
                                    obstacles = segment.find("Obstacles")
                                    if obstacles is not None:
                                        busstops = obstacles.findall("BusStop")
                                        for busstop in busstops:
                                            busstop_id = int(busstop.find("id").text)
                                            if busstop_id in ids[linkId][segmentId]:
                                                obstacles.remove(busstop)


    def deleteSegment(self, features):
        ids = {}
        # delete from shapefile
        for feature in features:
            self.active_layer.dataProvider().deleteFeatures([feature.id()])
            attrs = feature.attributes()
            if not ids.has_key(attrs[0]):
                ids[attrs[0]] = {}
            ids[attrs[0]][attrs[1]] = True
        # delete inside components
        layers = [self.getLayer(TYPE.LANEEDGE), self.getLayer(TYPE.LANE), self.getLayer(TYPE.CROSSING), self.getLayer(TYPE.BUSSTOP)]
        for layer in layers:
            delete_feature_ids = []
            for feature in layer.getFeatures():
                attrs = feature.attributes()
                if attrs[0] in ids:
                    if attrs[1] in ids[attrs[0]]:
                        delete_feature_ids.append(feature.id())
            if len(delete_feature_ids) > 0:
                layer.dataProvider().deleteFeatures(delete_feature_ids)

        roadNetwork = self.document.find('GeoSpatial/RoadNetwork')
        linkParent = roadNetwork.find('Links')
        links = linkParent.findall('Link')
        if links is not None:
            for link in links:
                linkId = int(link.find('linkID').text)
                if linkId in ids:
                    segmentParent = link.find('Segments')
                    if segmentParent is not None:
                        segments = segmentParent.findall('Segment')
                        for segment in segments:
                            segmentId = int(segment.find("segmentID").text)
                            if segmentId in ids[linkId]:
                                segmentParent.remove(segment)


    def save(self):
        self.document.write(self.data_path, encoding="utf-8", xml_declaration=True, default_namespace=None, method="xml")