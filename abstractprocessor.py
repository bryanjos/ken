#!/usr/bin/env python

class AbsProcessor:

    def process(self, job, data):
        raise NotImplementedError()