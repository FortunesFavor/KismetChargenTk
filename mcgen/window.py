from __future__ import print_function, absolute_import


def main(argv):
    return ', '.join(repr(x) for x in argv)
