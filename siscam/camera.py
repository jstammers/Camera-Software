#!/usr/bin/python
#-*- coding: latin-1 -*-
"""Base classes for cameras"""

class CamTimeoutError(Exception):
    def __init__(self):
        super(CamTimeoutError, self).__init__(self, 'Timeout')


class BaseCam(object):

    def open(self):
        pass

    def close(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def snap(self, n):
        pass

    def set_timing(self, timing):
        pass
    
    



