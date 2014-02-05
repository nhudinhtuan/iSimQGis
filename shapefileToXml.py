import os, re
from xml.etree import ElementTree
from xml.dom import minidom
from iSimShapefileIO import ShapefileReader, TYPE as SHTYPE
from PyQt4 import QtCore

class ShapefileToXml(QtCore.QObject):
    # Signal emitted to update progress
    prog_sig = QtCore.pyqtSignal(int)
    def __init__(self, xmlPath, shDir):
        QtCore.QObject.__init__(self)
        self.xmlPath = xmlPath
        self.reader = ShapefileReader(shDir)
        ElementTree.register_namespace('geo', "http://www.smart.mit.edu/geo")
        self.document = ElementTree.parse(os.path.join(shDir, "data.xml"))

    def warnNonExist(self, typeId, id):
        print "Warning: there is not %s whose id is %s in shapefile!" % (typeId, id)
    
    def updateLocation(self, element, data):
        element.find("xPos").text = str(data[0])
        element.find("yPos").text = str(data[1])

    def addXMLLocation(self, parent, pos):
        location = ElementTree.SubElement(parent, 'location')
        ElementTree.SubElement(location, 'xPos').text = str(pos[0])
        ElementTree.SubElement(location, 'yPos').text = str(pos[1])

    def updateUninodes(self, uninodes):
        nodeData = self.reader.getNodes(SHTYPE.UNINODE)
        for uninode in uninodes:
            nodeId = int(uninode.find("nodeID").text)
            if nodeId in nodeData:
                self.updateLocation(uninode.find("location"), nodeData[nodeId])
            else:
                self.warnNonExist("UniNode", nodeId)

    def updateMulnodes(self, mulnodes):
        nodeCoordinates = self.reader.getNodes(SHTYPE.MULNODE)
        for mulnode in mulnodes:
            nodeId = int(mulnode.find("nodeID").text)
            if nodeId in nodeCoordinates:
                self.updateLocation(mulnode.find("location"), nodeCoordinates[nodeId])
            else:
                self.warnNonExist("multiNode", nodeId)

    def updateLane(self, segmentId, lane):
        laneCoordinates = self.reader.getCacheByFirstId(SHTYPE.LANE, int(segmentId))
        laneID = int(lane.find("laneID").text)
        polyline = lane.find("PolyLine")
        if laneID in laneCoordinates:
            for polyPoint in polyline.findall('PolyPoint'):
                polyline.remove(polyPoint)
            index = 0
            for point in laneCoordinates[laneID]:
                polyPoint = ElementTree.SubElement(polyline, 'PolyPoint')
                ElementTree.SubElement(polyPoint, 'pointID').text = str(index)
                self.addXMLLocation(polyPoint, point)
                index = index + 1
        else:
            self.warnNonExist("lane", segmentID)
    
    def updateLaneEdge(self, segmentId, laneEdge):
        laneEdgeCoordinates = self.reader.getCacheByFirstId(SHTYPE.LANEEDGE, int(segmentId))
        laneNumber = int(laneEdge.find("laneNumber").text)
        polyline = laneEdge.find("polyline")
        if laneNumber in laneEdgeCoordinates:
            for polyPoint in polyline.findall('PolyPoint'):
                polyline.remove(polyPoint)
            index = 0
            for point in laneEdgeCoordinates[laneNumber]:
                polyPoint = ElementTree.SubElement(polyline, 'PolyPoint')
                ElementTree.SubElement(polyPoint, 'pointID').text = str(index)
                self.addXMLLocation(polyPoint, point)
                index = index + 1
        else:
            self.warnNonExist("laneEdge", segmentID)

    def updateCrossing(self, segmentId, crossing):
        crossCoordinates = self.reader.getCacheByFirstId(SHTYPE.CROSSING, int(segmentId))
        crossingId = int(crossing.find("id").text)
        if crossingId in crossCoordinates:
            coordinates = crossCoordinates[crossingId]
            nearLine = crossing.find("nearLine")
            self.updateLocation(nearLine.find('first'), coordinates[0])
            self.updateLocation(nearLine.find('second'), coordinates[1])
            farLine = crossing.find("farLine")
            self.updateLocation(farLine.find('first'), coordinates[3])
            self.updateLocation(farLine.find('second'), coordinates[2])            
        else:
            self.warnNonExist("crossing", crossingId)     

    def updateBusstop(self, segmentId, busstop):
        busstopCoordinates = self.reader.getCacheByFirstId(SHTYPE.BUSSTOP, int(segmentId))
        busstopId = int(busstop.find("id").text)
        if busstopId in busstopCoordinates:
           pos = busstopCoordinates[busstopId][0]
           self.updateLocation(busstop, pos) 
        else:
            self.warnNonExist("Busstop", busstopId)   

    def updateSegment(self, linkId, segment):
        segmentCoordinates = self.reader.getCacheByFirstId(SHTYPE.SEGMENT, int(linkId))
        segmentID = int(segment.find("segmentID").text)
        polyline = segment.find("polyline")
        #update segment
        if segmentID in segmentCoordinates:
            for polyPoint in polyline.findall('PolyPoint'):
                polyline.remove(polyPoint)
            segmentCoordinate = segmentCoordinates[segmentID]
            for index in range(0, len(segmentCoordinate)-1):
                point = segmentCoordinate[index]
                polyPoint = ElementTree.SubElement(polyline, 'PolyPoint')
                ElementTree.SubElement(polyPoint, 'pointID').text = str(index)
                self.addXMLLocation(polyPoint, point)
        else:
            self.warnNonExist("segment", segmentID)
        #update lanes
        lanes = segment.find("Lanes")
        for lane in lanes.findall('Lane'):
            self.updateLane(segmentID, lane)
        #update laneEdge
        laneEdges = segment.find("laneEdgePolylines_cached")
        for laneEdge in laneEdges.findall('laneEdgePolyline_cached'):
            self.updateLaneEdge(segmentID, laneEdge)
        #update obstacles
        obstacles = segment.find("Obstacles")
        for obstacle in obstacles.getchildren():
            if obstacle.tag == "Crossing":
                self.updateCrossing(segmentID, obstacle)
            elif obstacle.tag == "BusStop":
                self.updateBusstop(segmentID, obstacle)

    def writePrettyToXml(self):
        roughString = ElementTree.tostring(self.document.getroot(), 'utf-8')
        reparsed = minidom.parseString(roughString)
        pretty_string =  '\n'.join([line for line in reparsed.toprettyxml(indent=' '*4).split('\n') if line.strip()])
        xmlFile = open(self.xmlPath, 'w')
        xmlFile.write(pretty_string)
        xmlFile.close()

    def run(self):
        roadNetwork = self.document.find('GeoSpatial/RoadNetwork')
        #update nodes
        nodes = roadNetwork.find('Nodes')
        self.updateUninodes(nodes.find('UniNodes').findall('UniNode'))
        self.prog_sig.emit(25)
        self.updateMulnodes(nodes.find('Intersections').findall('Intersection'))
        self.prog_sig.emit(50)
        #update segment
        links = roadNetwork.find('Links').findall('Link')
        count = len(links)
        progPercent = 50
        for link in links:
            segments = link.find('Segments')
            linkId = link.find('linkID').text
            for segment in segments.findall('Segment'):
                self.updateSegment(linkId, segment)
            progPercent = progPercent + 25.0/count
            self.prog_sig.emit(progPercent)
        self.writePrettyToXml()
        self.prog_sig.emit(100)
