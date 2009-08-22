"""
See documentation of class ReadWriteLock defined in this module.
"""

import originalreadwritelock

__all__ = ["ReadWriteLock"]

class ContextManager(object):
    def __init__(self, lock, acquire_func):
        self.lock = lock
        self.acquire_func = acquire_func
    def __enter__(self, *args, **kwargs):
        self.acquire_func()
    def __exit__(self, *args, **kwargs):
        self.lock.release()

class ReadWriteLock(originalreadwritelock.ReadWriteLock):
    """
    A ReadWriteLock subclassed from a different ReadWriteLock class defined
    in the module originalreadwritelock.py, (See the documentation of the
    original class for more details.)
    
    This subclass adds two context managers, one for reading and one for
    writing.
    
    Usage:
    
    lock = ReadWriteLock()
    with lock.read:
        pass #perform read operations here
    with lock.write:
        pass #perform write operations here
    
    """
    def __init__(self, *args, **kwargs):
        originalreadwritelock.ReadWriteLock.__init__(self, *args, **kwargs)
        self.read = ContextManager(self, self.acquireRead)
        self.write = ContextManager(self, self.acquireWrite)