from ._resolver import *


def Resolver(file=PUBLICCONF):
    return _Resolver(file)

__resolver = _Resolver(PRIVATECONF)