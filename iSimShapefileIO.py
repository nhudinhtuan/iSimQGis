import shapefile, os

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

# Constants
TYPE = enum('UNINODE', 'MULNODE', 'SEGMENT', 'LANE', 'CROSSING', 'BUSSTOP', 'LANEEDGE')
TAGS = {TYPE.UNINODE: "uninode", TYPE.MULNODE: "mulnode", TYPE.SEGMENT: "segment", 
        TYPE.LANE: "lane", TYPE.CROSSING: "crossing", TYPE.BUSSTOP: "busstop", TYPE.LANEEDGE: "laneegde"}
SCHEMA = {}
SCHEMA[TYPE.UNINODE] = [shapefile.POINT, [['id', 'N', '10']]]
SCHEMA[TYPE.MULNODE] = [shapefile.POINT, [['id', 'N', '10']]]
SCHEMA[TYPE.SEGMENT] = [shapefile.POLYGON, [['link-id', 'N', '10'], ['segmentID', 'N', '10']]]
SCHEMA[TYPE.LANE] = [shapefile.POLYLINE, [['segment-id', 'N', '10'], ['laneID', 'N', '10']]]
SCHEMA[TYPE.CROSSING] = [shapefile.POLYGON, [['segment-id', 'N', '10'], ['id', 'N', '10']]]
SCHEMA[TYPE.BUSSTOP] = [shapefile.POINT, [['segment-id', 'N', '10'], ['id', 'N', '10']]]    
SCHEMA[TYPE.LANEEDGE] = [shapefile.POLYLINE, [['segment-id', 'N', '10'], ['number', 'N', '10']]] 

class ShapefileWriter:
    def __init__(self, path):
        self.path = path
        self.prefix = os.path.basename(path)
        self.count = {}
        self.shape = {}
        for typeid in SCHEMA:
            self.count[typeid] = 0
            self.shape[typeid] = shapefile.Writer(SCHEMA[typeid][0])
            for data in SCHEMA[typeid][1]:
                 self.shape[typeid].field(data[0], data[1], data[2])
        
    def addPoint(self, typeid, pos, info):       
        if SCHEMA[typeid][0] == shapefile.POINT:
            self.shape[typeid].point(pos[0], pos[1])
            self.shape[typeid].record(*info)
            self.count[typeid] += 1

    def addPolygon(self, typeid, coordinates, info):      
        if SCHEMA[typeid][0] == shapefile.POLYGON:
            self.shape[typeid].poly(parts=[coordinates])
            self.shape[typeid].record(*info)
            self.count[typeid] += 1            

    def addPolyline(self, typeid, coordinates, info):     
        if SCHEMA[typeid][0] == shapefile.POLYLINE:
            self.shape[typeid].line(parts=[coordinates])
            self.shape[typeid].record(*info)
            self.count[typeid] += 1

    def save(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        #save to shapefiles 
        for typeid, tag in TAGS.iteritems():
            if self.count[typeid] > 0:
                print "Total %s: " % tag, self.count[typeid]
                self.shape[typeid].save("%s/%s_%s"%(self.path, self.prefix, tag))

class ShapefileReader:
    def __init__(self, path):
        self.path = path
        self.prefix = os.path.basename(path)
        self.shape = {}
        self.cache = {}
        for typeid, tag in TAGS.iteritems():
            filepath = os.path.join(self.path, "%s_%s.shp" % (self.prefix, tag))
            if os.path.isfile(filepath):
                self.shape[typeid] = shapefile.Reader(filepath)
            else:
                self.shape[typeid] = None
            self.cache[typeid] = None

    def getNodes(self, typeid):
        nodes = {}
        if self.shape[typeid] != None and SCHEMA[typeid][0] == shapefile.POINT:
            for feature in self.shape[typeid].shapeRecords():
                nodes[feature.record[0]] = feature.shape.points[0]
        return nodes

    def getCacheData(self, typeid):
        if self.cache[typeid] != None:
            return self.cache[typeid]
        self.cache[typeid] = {}
        if self.shape[typeid] != None:
            for feature in self.shape[typeid].shapeRecords():
                if feature.record[0] not in self.cache[typeid]:
                    self.cache[typeid][feature.record[0]] = {}
                self.cache[typeid][feature.record[0]][feature.record[1]] = feature.shape.points
        return self.cache[typeid]

    def getCacheByFirstId(self, typeid, firstId):
        data = self.getCacheData(typeid)
        if firstId in data:
            return data[firstId]
        else:
            return {}
