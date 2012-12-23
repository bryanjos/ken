class Information:
    def __init__(self, source, id, creator, unix_time, data, location=u'', lat=0.0, lon=0.0):
        self.source = source
        self.id = id
        self.creator = creator
        self.time = unix_time
        self.data = data
        self.location = location
        self.lat = lat
        self.lon = lon
        self.geom = 'POINT(%s %s)' % (lat,lon)

