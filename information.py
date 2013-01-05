import json

class Information:
    def __init__(self, source, id, creator, time, data, job_slug, location=u'', lat=0.0, lon=0.0):
        self.source = source
        self.id = id
        self.creator = creator
        self.time = time
        self.data = data
        self.location = location
        self.coordinates = { 'lon':float(lon), 'lat': float(lat)}
        self.coordinate_string = '' if lat == 0 and lon == 0 else '%s %s' % (lat, lon)
        self.job_slug = job_slug

    def __repr__(self):
        return json.dumps(self.__dict__, cls=JSONEncoder)


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'isoformat'): #handles both date and datetime objects
            return obj.strftime('%Y-%m-%dT%H:%M:%S+00:00')
        else:
            return json.JSONEncoder.default(self, obj)

