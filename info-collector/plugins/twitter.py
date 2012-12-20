#!/usr/bin/env python

# This is an example plugin that can be used as a
# skeleton for new plugins.
# The documentation string in the plugin class will be used to
# print the help of the plugin.

from abstractplugin import AbsPlugin
import requests
import time


class TwitterPlugin(AbsPlugin):
    """ An example plugin that prints dummy messages """
    def __init__(self):
        pass

    # Public methods will be considered plugin commands.
    # The name of the command will be the method name.
    # The documentation string in command methods will be used to
    # print the help of the command.
    # The arguments are the options given to the command itself
    def get_data(self):
        twit = requests.get('http://search.twitter.com/search.json?q=%40twitterapi')
        data = []
        for tweet in twit.json()['results']:
            date =  time.strptime(tweet['created_at'], '%a, %d %b %Y %H:%M:%S +0000')
            data.append({
                'source': 'twitter',
                'id': str(tweet['id']),
                'creator': tweet['from_user'],
                'time': int(time.strftime('%s',date)),
                'location': tweet['location'] if 'location' in tweet else '',
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