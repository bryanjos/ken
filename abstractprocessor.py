#!/usr/bin/env python

class AbsProcessor:

    def get_keys(self, job):
        raise NotImplementedError()

    def get_data_paged(self, parameters, page_size, page):
        raise NotImplementedError()

    def get_data_since(self, parameters, since_unix_time):
        raise NotImplementedError()