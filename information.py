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
        return json.dumps(self.__dict__, cls=JSONEncoder)

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


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'isoformat'): #handles both date and datetime objects
            return obj.strftime('%Y-%m-%dT%H:%M:%S+00:00')
        else:
            return json.JSONEncoder.default(self, obj)

