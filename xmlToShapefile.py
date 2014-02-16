import re
from xml.etree import ElementTree
from iSimShapefileIO import ShapefileWriter, TYPE as SHTYPE
from PyQt4.QtCore import *
from qgis.core import *

class XmlToShapefile(QObject):
    # Signal emitted to update progress
    prog_sig = pyqtSignal(int)
    def __init__(self, xml_path, sh_dir, formula):
        QObject.__init__(self)
        self.document = None
        self.writer = ShapefileWriter(sh_dir)
        ElementTree.register_namespace('geo', "http://www.smart.mit.edu/geo")
        self.document = ElementTree.parse(xml_path)
        self.formula = formula

    def parseLocation(self, data):
        x = float(data.find("xPos").text)
        y = float(data.find("yPos").text)
        
        pos = QgsPoint(eval(self.formula[0]), eval(self.formula[1]))
        data.find("xPos").text = "--"
        data.find("yPos").text = "--"
        return pos

    def parseUninode(self, uninode):
        point = self.parseLocation(uninode.find("location"))
        attr = [uninode.find("nodeID").text]
        self.writer.addPoint(SHTYPE.UNINODE, point, attr)

    def parseMulnode(self, mulnode):
        point = self.parseLocation(mulnode.find("location"))
        attr = [mulnode.find("nodeID").text]
        self.writer.addPoint(SHTYPE.MULNODE, point, attr)

    def parseLane(self, linkId, segmentId, lane):
        attr = [linkId, segmentId, lane.find("laneID").text]
        coordinates = []
        polyLine = lane.find("PolyLine")
        if polyLine is None:
            return
        for polypoint in polyLine.findall('PolyPoint'):
            coordinates.append(self.parseLocation(polypoint.find('location')))
        self.writer.addPolyline(SHTYPE.LANE, coordinates, attr)

    def parseLaneEdge(self, linkId, segmentId, laneEdge):
        attr = [linkId, segmentId, laneEdge.find("laneNumber").text]
        coordinates = []
        polyLine = laneEdge.find("polyline")
        for polypoint in polyLine.findall('PolyPoint'):
            coordinates.append(self.parseLocation(polypoint.find('location')))
        self.writer.addPolyline(SHTYPE.LANEEDGE, coordinates, attr)
    
    def parseCrossing(self, linkId, segmentId, crossing):
        attr = [linkId, segmentId, crossing.find("id").text]
        coordinates = [0, 1, 2, 3]
        nearLine = crossing.find("nearLine")
        coordinates[0] = self.parseLocation(nearLine.find('first'))
        coordinates[1] = self.parseLocation(nearLine.find('second'))
        farLine = crossing.find("farLine")
        coordinates[3] = self.parseLocation(farLine.find('first'))
        coordinates[2] = self.parseLocation(farLine.find('second'))
        self.writer.addPolygon(SHTYPE.CROSSING, coordinates, attr)

    def parseBusstop(self, linkId, segmentId, busstop):
        point = self.parseLocation(busstop)
        attr = [linkId, segmentId, busstop.find("id").text]
        self.writer.addPoint(SHTYPE.BUSSTOP, point, attr) 

    def parseSegment(self, linkId, segment):
        segmentId = segment.find("segmentID").text
        attr = [linkId, segmentId]
        coordinates = [] 
        polyline = segment.find("polyline")
        for polypoint in polyline.findall('PolyPoint'):
            coordinates.append(self.parseLocation(polypoint.find('location')))
        #parse Lane
        lanes = segment.find("Lanes")
        for lane in lanes.findall('Lane'):
            self.parseLane(linkId, segmentId, lane)
        #parse Lane Egde
        laneEdges = segment.find("laneEdgePolylines_cached")
        for laneEdge in laneEdges.findall('laneEdgePolyline_cached'):
            self.parseLaneEdge(linkId, segmentId, laneEdge)
        #parse obstacles
        obstacles = segment.find("Obstacles")
        for obstacle in obstacles.iter():
            if obstacle.tag == "Crossing":
                self.parseCrossing(linkId, segmentId, obstacle)
            elif obstacle.tag == "BusStop":
                self.parseBusstop(linkId, segmentId, obstacle)
        self.writer.addPolygon(SHTYPE.SEGMENT, coordinates, attr)

    def run(self):
        if self.document == None:
            return
        progPercent = 0
        roadNetwork = self.document.find('GeoSpatial/RoadNetwork')
        #parse nodes
        nodes = roadNetwork.find('Nodes')
        if nodes is not None:
            uniNodes = nodes.find('UniNodes').findall('UniNode')
            mulNodes = nodes.find('Intersections').findall('Intersection')
            count = len(uniNodes) + len(mulNodes)
            for uninode in uniNodes:
                self.parseUninode(uninode)
                progPercent = progPercent + 50.0/count
                self.prog_sig.emit(progPercent)
            for mulNode in mulNodes:
                self.parseMulnode(mulNode)
                progPercent = progPercent + 50.0/count
                self.prog_sig.emit(progPercent)

        #parse segment
        links = roadNetwork.find('Links').findall('Link')
        count = len(links)
        for link in links:
            segments = link.find('Segments')
            linkId = link.find('linkID').text
            for segment in segments.findall('Segment'):
                self.parseSegment(linkId, segment)
            progPercent = progPercent + 50.0/count
            self.prog_sig.emit(progPercent)
        
        #save shapefiles
        self.writer.save()
        #save the rest of xml file
        xmlRemainPath = "%s/data.xml" % self.writer.path
        self.document.write(xmlRemainPath, encoding="utf-8", xml_declaration=True, default_namespace=None, method="xml")