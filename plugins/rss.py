#!/usr/bin/env python

from abstractplugin import AbsPlugin
import datetime
from information import Information
import feedparser
import re
import time

class RSSPlugin(AbsPlugin):
    def __init__(self):
        self.source_and_url = None
        pass

    def set_extra_data(self, data):
        self.source_and_url = data

    def get_data(self, job, since):
        data = []
        if self.source_and_url:
            to_find = re.compile('|'.join(job.tags))
            feed = feedparser.parse(self.source_and_url[1])
            for entry in feed.entries:
                if time.mktime(entry.published_parsed) > since:
                    if to_find.search(entry.summary) is not None or to_find.search(entry.title) is not None:

                        if 'author' in entry:
                            creator = entry.author.name
                        else:
                            creator = self.source_and_url[0]

                        i = Information(self.source_and_url[0],
                            entry.id,
                            creator,
                            datetime.datetime.strptime(entry.updated, '%Y-%m-%dT%H:%M:%SZ'),
                            entry.title + ' | ' + entry.summary,
                            job.slug,
                            location = u'',
                            lat = 0.0,
                            lon = 0.0)

                        data.append(i)

        return data


# Each plugin must provide a load method at module level that will be
# used to instantiate the plugin
def load():
    """ Loads the current plugin """
    return RSSPlugin()
