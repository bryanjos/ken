#!/usr/bin/env python

class AbsProcessor:

    """
    Job passed in looks like this
     {
            'name': int,
            'sources': [string],
            'time': int,
            'location': string or None,
            'lat':float or None,
            'lon':float or None,
            'distance':float,
            'tags': [string]
        }
    """
    def get_keys(self, job):
        pass

    def get_data(self, parameters):
        pass