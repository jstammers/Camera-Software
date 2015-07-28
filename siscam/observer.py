#!/usr/bin/python
#-*- coding: latin-1 -*-#
"""Provides mixin classes for the observer design pattern."""

import functools

def changes_state(f):
    """decorator for methods which adds call 'update_observers' after
    completion of method."""
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        result = f(self, *args, **kwargs)
        if not self._batchcount:
            self.update_observers()
        return result
    return wrapper

class Subject(object):
    """Mixin class to implement observer/subject design pattern for
    subject. Decorate methods which change state with
    L{changes_state}. This will call 'update' on all observers, with
    subject as argument.""" 

    def add_observer(self, observer):
        "add observer. Observer must implement 'update(subject)'"
        try:
            self.observers.add(observer)
        except AttributeError:
            self.observers = set((observer,))

        observer.update(self)

    def remove_observer(self, observer):
        "remove observer"
        self.observers.discard(observer)

    def update_observers(self):
        """call update(self) on all observers. Instead of calling this
        method you can also decorate your methods with
        L{changes_state}"""
        for o in getattr(self, 'observers', []):
            o.update(self)

    def begin_batch(self):
        self._batchcount += 1

    def end_batch(self):
        self._batchcount -= 1
        if self._batchcount <= 0:
            self._batchcount = 0
            self.update_observers()

    def get_batchcount(self):
        #return getattr(self, '__batchcount') #ok?
        try:
            value = self.__batchcount
        except AttributeError:
            self.__batchcount = 0
            value = 0
        return value

    def set_batchcount(self, value):
        self.__batchcount = value

    _batchcount = property(get_batchcount,
                           set_batchcount)

    def __getstate__(self):
        odict = self.__dict__.copy()
        del odict['observers']
        return odict

