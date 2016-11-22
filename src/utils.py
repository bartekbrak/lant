"""
Collects utility functions - code not explicitly required to run the core
but helpful in debug, profiling and similar.
Also generic python utils.
"""
from datetime import datetime
from functools import wraps


def elapsed(carrier, msg='elapsed'):
    """
    A decorator that measures time spent in a function and loggs it via logger.info

    """
    def elapsed_decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            start = datetime.now()
            r = func(*args, **kwargs)
            carrier('%s %s' % (msg, datetime.now() - start))
            return r
        return wrapped
    return elapsed_decorator


def split_by_n(seq, n):
    """
    A generator to divide a sequence into chunks of n units.
    The only reason this is a generator is copy paste laziness.
    Generators are not cool, unless you really need them. No, they aren't stop arguing.
    """
    while seq:
        yield seq[:n]
        seq = seq[n:]
