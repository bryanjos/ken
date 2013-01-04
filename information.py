import json

class Information:
    def __init__(self, source, id, creator, time, data, job_slug, location=u'', lat=0.0, lon=0.0):
        self.source = source
        self.id = id
        self.creator = creator
        self.time = time
        self.data = data
        self.location = location
        self.lat = lat
        self.lon = lon
        self.coordinate_string = '' if lat == 0 and lon == 0 else '%s %s' % (lat, lon)
        self.job_slug = job_slug

    def __repr__(self):
        return json.dumps(self.__dict__)

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
            'coordinates': { 'x':float(self.lon), 'y': float(self.lat)},
            'job_slug' : self.job_slug
        }

