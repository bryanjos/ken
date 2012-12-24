class Job:
    def __init__(self, name, slug, unix_time, tags, lat=None, lon=None, distance = 1.0):
        self.name = name
        self.slug = slug
        self.time = unix_time
        self.tags = tags
        self.lat = lat
        self.lon = lon
        self.distance = distance