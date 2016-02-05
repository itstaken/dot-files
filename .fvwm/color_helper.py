#!/usr/bin/python
# -*- coding: utf-8 -*-
''' Helper script for generating FVWM color schemes

Given an input color, this script generates a set of output SetEnv statements
that can be PipeRead by fvwm to set up a color scheme.

For example:

    PipeRead `color_helper.py #4A516A`

Will result in the following statements being consumed by Fvwm:

    FIXME: update this

'''

import sys


def inc_mask(value, amt, mask=0xff):
    '''
    Increments the provided value by the specified amount and masks it by the
    provided mask.
    '''
    v = value + amt
    v &= mask
    return v


def join_color(red, green, blue):
    '''
    Joins the provided red, green, and blue into a color value.
    '''
    return red << 16 | green << 8 | blue


def split_color(color):
    '''
    Converts the provided hex color into a 3 tuple of red, green, and blue.
    '''
    return color >> 16, color >> 8 & 0xff, color & 0xff


def lighter(color):
    '''
    Given an input color, return a slightly lighter color.
    '''
    r, g, b = split_color(color)
    r = inc_mask(r, 0x33)
    g = inc_mask(g, 0x33)
    b = inc_mask(b, 0x33)
    color = join_color(r, g, b)
    return color


def main(argv):
    color = argv[0]
    #FIXME: if color is a name, convert it to hex
    if color.startswith('#'):
        color = color[1:]
    color = int(color, 16)
    print('SetEnv FG_COLOR white')
    print('SetEnv FG_COLOR_INACTIVE grey')
    print('SetEnv BG_COLOR #%06x' % color)
    print('SetEnv BG_COLOR_LIGHTER #%06x' % lighter(color))

if __name__ == "__main__":
    main(sys.argv[1:])
