import re
from xml.etree import ElementTree
from iSimShapefileIO import ShapefileWriter, TYPE as SHTYPE
from PyQt4 import QtCore

class XmlToShapefile(QtCore.QObject):
    # Signal emitted to update progress
    prog_sig = QtCore.pyqtSignal(int)
    def __init__(self, xml_path, sh_dir):
        QtCore.QObject.__init__(self)
        self.document = None
        self.writer = ShapefileWriter(sh_dir)
        ElementTree.register_namespace('geo', "http://www.smart.mit.edu/geo")
        self.document = ElementTree.parse(xml_path)

    def parseLocation(self, data):
        pos = [float(data.find("xPos").text), float(data.find("yPos").text)]
        data.find("xPos").text = "--"
        data.find("yPos").text = "--"
        return pos

    def parseUninode(self, uninode):
        pos = self.parseLocation(uninode.find("location"))
        info = [uninode.find("nodeID").text]
        self.writer.addPoint(SHTYPE.UNINODE, pos, info)

    def parseMulnode(self, mulnode):
        pos = self.parseLocation(mulnode.find("location"))
        info = [mulnode.find("nodeID").text]
        self.writer.addPoint(SHTYPE.MULNODE, pos, info)

    def parseLane(self, segmentId, lane):
        info = [segmentId, lane.find("laneID").text]
        coordinates = []
        polyLine = lane.find("PolyLine")
        for polypoint in polyLine.findall('PolyPoint'):
            coordinates.append(self.parseLocation(polypoint.find('location')))
        self.writer.addPolyline(SHTYPE.LANE, coordinates, info)

    def parseLaneEdge(self, segmentId, laneEdge):
        info = [segmentId, laneEdge.find("laneNumber").text]
        coordinates = []
        polyLine = laneEdge.find("polyline")
        for polypoint in polyLine.findall('PolyPoint'):
            coordinates.append(self.parseLocation(polypoint.find('location')))
        self.writer.addPolyline(SHTYPE.LANEEDGE, coordinates, info)
    
    def parseCrossing(self, segmentId, crossing):
        info = [segmentId, crossing.find("id").text]
        coordinates = [[0, 0], [0, 0], [0, 0], [0, 0]]
        nearLine = crossing.find("nearLine")
        coordinates[0] = self.parseLocation(nearLine.find('first'))
        coordinates[1] = self.parseLocation(nearLine.find('second'))
        farLine = crossing.find("farLine")
        coordinates[3] = self.parseLocation(farLine.find('first'))
        coordinates[2] = self.parseLocation(farLine.find('second'))
        self.writer.addPolygon(SHTYPE.CROSSING, coordinates, info)

    def parseBusstop(self, segmentId, busstop):
        pos = self.parseLocation(busstop)
        info = [segmentId, busstop.find("id").text]
        self.writer.addPoint(SHTYPE.BUSSTOP, pos, info) 

    def parseSegment(self, linkId, segment):
        info = [linkId, segment.find("segmentID").text]
        coordinates = [] 
        polyline = segment.find("polyline")
        for polypoint in polyline.findall('PolyPoint'):
            coordinates.append(self.parseLocation(polypoint.find('location')))
        #parse Lane
        lanes = segment.find("Lanes")
        for lane in lanes.findall('Lane'):
            self.parseLane(info[1], lane)
        #parse Lane Egde
        laneEdges = segment.find("laneEdgePolylines_cached")
        for laneEdge in laneEdges.findall('laneEdgePolyline_cached'):
            self.parseLaneEdge(info[1], laneEdge)
        #parse obstacles
        obstacles = segment.find("Obstacles")
        for obstacle in obstacles.getchildren():
            if obstacle.tag == "Crossing":
                self.parseCrossing(info[1], obstacle)
            elif obstacle.tag == "BusStop":
                self.parseBusstop(info[1], obstacle)
        self.writer.addPolygon(SHTYPE.SEGMENT, coordinates, info)

    def run(self):
        if self.document == None:
            return
        progPercent = 0
        roadNetwork = self.document.find('GeoSpatial/RoadNetwork')
        #parse nodes
        nodes = roadNetwork.find('Nodes')
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