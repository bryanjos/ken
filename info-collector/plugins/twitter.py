#!/usr/bin/env python

from abstractplugin import AbsPlugin
import requests
import time


class TwitterPlugin(AbsPlugin):
    def __init__(self):
        pass

    def get_data(self,job):
        url = u'http://search.twitter.com/search.json?q='
        url = url + ' OR '.join(job.tags.split(' '))
        url = url + "&count=100"
        if job.lat > 0 and job.lon > 0:
            url = url + '&geocode=' + job.lat + ',' + job.lon + ',' + str(job.distance) + 'mi'
        twit = requests.get(url)
        data = []
        for tweet in twit.json()['results']:
            date =  time.strptime(tweet['created_at'], '%a, %d %b %Y %H:%M:%S +0000')
            data.append({
                'source': 'twitter',
                'id': str(tweet['id']),
                'creator': tweet['from_user'],
                'time': int(time.strftime('%s',date)),
                'location': tweet['location'] if 'location' in tweet else u'',
                'lat': tweet['geo']['coordinates'][0] if tweet['geo'] and 'coordinates' in tweet['geo'] else 0.0,
                'lon': tweet['geo']['coordinates'][1] if tweet['geo'] and 'coordinates' in tweet['geo'] else 0.0,
                'data': tweet['text']
            })

        return data


# Each plugin must provide a load method at module level that will be
# used to instantiate the plugin
def load():
    """ Loads the current plugin """
    return TwitterPlugin()