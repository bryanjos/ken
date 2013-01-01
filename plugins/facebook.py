#!/usr/bin/env python

from abstractplugin import AbsPlugin
import requests
import time
from information import Information

class FacebookPlugin(AbsPlugin):
    def __init__(self):
        pass

    def get_data(self, job, since):
        url = u'https://graph.facebook.com/search?q='
        url = url + ' OR '.join(job.tags)
        url = url + '&type=post'
        if job.lat > 0 and job.lon > 0:
            url = url + '&center=' + job.lat + ',' + job.lon
            url = url + '&distance=' + job.distance
        response = requests.get(url)
        data = []
        for item in response.json()['data']:
            date =  time.strptime(item['created_time'], '%Y-%m-%dT%H:%M:%S+0000')
            data.append(
                Information('facebook',
                    item['id'],
                    item['from']['name'],
                    int(time.strftime('%s',date)),
                    item['message'],
                    location = u'',
                    lat = 0.0,
                    lon = 0.0)
            )

        print data
        return data


# Each plugin must provide a load method at module level that will be
# used to instantiate the plugin
def load():
    """ Loads the current plugin """
    return FacebookPlugin()