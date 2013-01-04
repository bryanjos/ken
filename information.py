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
        self.coordinate_string = '' if lat is 0.0 and lon is 0.0 else '%s %s' % (lat, lon)

    def __repr__(self):
        return repr((self.source, self.id, self.creator, self.time, self.data, self.location, self.lat, self.lon, self.coordinate_string))

    def to_json(self):
        return {
            'source': self.source,
            'id': self.id,
            'creator':self.creator,
            'time':self.time,
            'data':self.data,
            'location':self.location,
            'lat': float(self.lat),
            'lon': float(self.lon),
            'coordinates': { 'x':float(self.lon), 'y': float(self.lat)}
        }

