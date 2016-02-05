#!/usr/bin/python
# -*- coding: utf-8 -*-
''' Helper script for generationg FVWM display menu

This script uses xrandr (avoids an xlib dependency that might not be installed)
to provide a display settings menu featuring resolution switching and
multi-monitor configurtion.

How it works
------------
The script generates some static functions that are used by dynamic menus to
generate a `DisplaysMenu` that consists of all the detected displays and
sub menus for each display.

The following illustrations show an example of the menus produced when the
display Menu is popped up in FVWM.

DisplaysMenu:
 ┌────────────────────┐
 │ VGA-0            ▷ │
 │ LVDS-0           ▷ │
 │ VGA-1 (primary)  ▷ │
 └────────────────────┘

Sample disconnected menu:
 ┌──────────────┐
 │ disconnected │
 └──────────────┘

Disconnected displays show only a disconnected status in the submenu for that
display.

VGA-0 menu:
 ┌───────────────────┐
 │ Set Primary       │
 │ Mirror          ▷ │
 │ Position        ▷ │
 │ Resolution      ▷ │
 └───────────────────┘

LVDS-0 Mirror menu:
 ┌───────────────────┐
 │       Mirror      │
 │ VGA-0             │
 │ VGA-1 (primary)   │
 └───────────────────┘

The mirror menus pop up a target display to set which display is mirrored by
the currently selected display.

VGA-0 Position Menu:
 ┌───────────────────┐
 │ Above           ▷ │
 │ Below           ▷ │
 │ Left            ▷ │
 │ Right           ▷ │
 └───────────────────┘

The entries for different positions relative to other monitors provide entries
for each attached display so that a user may, for example, place a monitor to
the left of another monitor.

VGA-0 Resolution Menu:
 ┌────────────────────────┐
 │ 1920x1080 (preferred)  │
 │ 1600x1200              │
 │ 800x600                │
 │ 640x480                │
 └────────────────────────┘
The resolution menu provides the output from xrandr and includes a notice to
show preferred resoutions.


How to use it
-------------
Upon FVWM start, `PipeRead` the output from this script and provide a `Menu` or
`Popup` command for `DisplaysMenu`.

For example:

    AddToFunc StartFunction
    + I PipeRead 'python $[FVWM_USERDIR]/display.py'

    AddToMenu MenuFvwmRoot
    + "Displays" Popup DisplaysMenu
'''

from __future__ import print_function
from subprocess import Popen, PIPE
import re
import optparse

def create_parser():
    '''
    Creates a parser for invoking the script in two modes: first mode is to get
    all the relevant functions Second mode is to just generate the display
    menus.

    The first mode should be executed from the start function of FVWM.
    The second mode should be executed by the display menu, so FVWM needs to be
    able to find this script.
    '''
    parser = optparse.OptionParser(usage=
    '''
    %prog [-f|--functions] | [-d|--displays]

This script generates functions and menus so that FVWM can have an XRANDR
aware display configuration menu.

When invoked with no arguments (or -f) generates the top-level functions needed
by successive invocations from FVWM.
if not options.displays and not options.functions:
options.functions = True

How to use it
-------------
Upon FVWM start, `PipeRead` the output from this script and provide a `Menu` or
`Popup` command for `DisplaysMenu`.

For example:

    AddToFunc StartFunction
    + I PipeRead 'python $[FVWM_USERDIR]/display.py'

    AddToMenu MenuFvwmRoot
    + "Displays" Popup DisplaysMenu
    ''')
    parser.add_option('-f', '--functions',
            help='Generate top-level functions needed by FVWM to generate the DisplaysMenu.', #pylint: disable=line-too-long
            action='store_true',
            dest='functions',
            default=False,
            )
    parser.add_option('-d', '--displays',
            help="Generates the DisplaysMenu content.",
            action='store_true',
            dest='displays',
            default=False
            )

    return parser

def invoke_xrandr():
    '''
    Invokes xrandr and collects the information into a list of dictionary
    entries.

    Sample return value:
    { 'VGA-0': {
            'resolutions': [{ 'value': '1930x1080',
                            'preferred': True,
                            'active': True },
                            ]
            'primary': True,
            'connected': True,
            },
     'HDMI-0': { 'connected': False, },
    }
    '''
    connected = r'((dis)?connected)'
    primary = r'primary'
    resolution = r'([0-9]+x[0-9]+)'
    active = r'\*'
    preferred = r'\+'

    displays = {}

    #import pdb
    #pdb.set_trace()
    current = None
    xrandr = Popen("xrandr", stdout=PIPE, stderr=PIPE)
    for line in xrandr.stdout.readlines():
        match = re.search(connected, line)
        if match:
            current = line[:match.start()].strip()
            displays[current] = {}
            displays[current]['connected'] = match.groups()[0] == 'connected'
            displays[current]['resolutions'] = []
            match = re.search(primary, line)
            displays[current]['primary'] = match and True
        else:
            match = re.search(resolution, line)
            if match:
                entry = {'resolution': match.groups()[0].strip()}
                match = re.search(preferred, line)
                entry['preferred'] = match and True
                match = re.search(active, line)
                entry['active'] = match and True
                displays[current]['resolutions'].append(entry)

    return displays

def display_active(display):
    '''
    Returns true if the specified displays has a currently active resolution.
    '''
    active = False
    for resolution in display['resolutions']:
        active = resolution['active'] or active
    return active

def count_active(displays):
    '''
    Counts the number of displays that are in a connected and active state.
    '''
    count = 0
    for display in displays.iterkeys():
        count += displays[display]['connected'] and display_active(displays[display]) and 1 or 0
    return count

def count_connected(displays):
    '''
    Counts the number of displays that are in a connected state.
    '''
    count = 0
    for display in displays.iterkeys():
        count += displays[display]['connected'] and 1 or 0
    return count

def do_mirrors_menu(prefix, function, display, displays):
    '''
    Produces sub menu options for the specified display.
    '''
    mirror = 'DestroyMenu recreate "{prefix}-{display}"\n'.format(prefix=prefix, display=display) #pylint: disable=line-too-long
    for current in displays.iterkeys():
        if current != display and displays[current]['connected']:
            mirror += 'AddToMenu "{prefix}-{display}" "{current}" {function} "{display}" "{current}"\n'.format( #pylint: disable=line-too-long
                    prefix=prefix, display=display, current=current,
                    function=function)
    return mirror

def do_position_menu(prefix, function, display, displays):
    '''
    Produces sub menu options for the specified display.
    '''
    directions = [('Left of', '--left-of'),
                  ('Right of', '--right-of'),
                  ('Above', '--above'),
                  ('Below', '--below'),
                 ]
    # AddToMenu "Position-HDMI-0" "Left -> (pop up other displays)
    # AddToMenu "Position-HDMI-0" "Right -> (pop up other displays)
    # AddToMenu "Position-HDMI-0" "Above -> (pop up other displays)
    # AddToMenu "Position-HDMI-0" "Below -> (pop up other displays)
    submenus = ''
    submenu = 'DestroyMenu recreate "{prefix}-{display}"\n'.format(prefix=prefix, display=display) #pylint: disable=line-too-long
    for label, direction in directions:
        submenu += 'AddToMenu "{prefix}-{display}" "{label}" Popup "Pick-{display}-{direction}"\n'.format( #pylint: disable=line-too-long
                prefix=prefix,
                display=display,
                label=label,
                direction=direction)

        submenus += '\n'
        submenus += 'DestroyMenu recreate "Pick-{display}-{direction}"\n'.format( #pylint: disable=line-too-long
                display=display,
                direction=direction)
        for current in displays.iterkeys():
            if current != display and displays[current]['connected']:
                submenus += 'AddToMenu "Pick-{display}-{direction}" "{current}" "{function}" "{display}" "{current}" "{direction}"\n'.format( #pylint: disable=line-too-long
                        current=current,
                        function=function,
                        display=display,
                        direction=direction)

    submenu += submenus
    return submenu

def do_resolution_menu(prefix, function, name, display):
    '''
    Produces the resolutions sub menu for the provided display.
    '''
    submenu = 'DestroyMenu recreate "{prefix}-{name}"\n'.format(
            prefix=prefix,
            name=name)
    for resolution in display['resolutions']:
        label = resolution['resolution']
        if resolution['preferred']:
            label += " (preferred)"
        if resolution['active']:
            label += " (active)"
        submenu += 'AddToMenu "{prefix}-{display}" "{label}" "{function}" "{display}" "{resolution}"\n'.format( #pylint: disable=line-too-long
                prefix=prefix,
                display=name,
                label=label,
                function=function,
                resolution=resolution['resolution'])

    return submenu

def do_top_level(menu, displays):
    '''
    Produces the top-level DisplaysMenu featuring one display per entry.
    '''
    menu_text = 'DestroyMenu recreate %s\n' % menu
    for display in displays.iterkeys():
        if not displays[display]['primary']:
            menu_text += 'AddToMenu %s "%s" Popup "%s"\n' % (menu, display, display) #pylint: disable=line-too-long
        else:
            menu_text += 'AddToMenu %s "%s (primary)" Popup "%s"\n' % (menu, display, display) #pylint: disable=line-too-long
    return menu_text

def functions():
    '''
    Generates the one-time functions needed for configuring the dynamic
    DisplaysMenu.

    Invoke this once per FVWM (re)load.
    '''
    print('DestroyFunc SetDisplayPosition')
    print('AddToFunc SetDisplayPosition')
    print('+ I Exec exec xrandr --output "$0" "$2" "$1"')
    print('+ I Schedule 250 Restart')
    print()
    print('DestroyFunc SetPrimaryDisplay')
    print('AddToFunc SetPrimaryDisplay')
    print('+ I Exec exec xrandr --output "$0" --primary')
    print('+ I Schedule 250 Restart')
    print()
    print('DestroyFunc TurnOnDisplay')
    print('AddToFunc TurnOnDisplay')
    print('+ I Exec exec xrandr --output "$0" --auto')
    print()
    print('DestroyFunc TurnOffDisplay')
    print('AddToFunc TurnOffDisplay')
    print('+ I Exec exec xrandr --output "$0" --off')
    print('+ I Schedule 250 Restart')
    print()
    print('DestroyFunc SetResolution')
    print('AddToFunc SetResolution')
    print('+ I Exec exec xrandr --output "$0" --mode "$1"')
    print('+ I Schedule 250 Restart')
    print()
    print('DestroyFunc SetMirrorMode')
    print('AddToFunc SetMirrorMode')
    print('+ I Exec exec xrandr --output "$0" --same-as "$1"')
    print('+ I Schedule 250 Restart')
    print()
    print('DestroyMenu DisplaysMenu')
    print('AddToMenu DisplaysMenu')
    print('+ DynamicPopupAction PipeRead \'"$[FVWM_USERDIR]"/display.py -d\'')
    #print('+ "Displays" Title')


def menus():
    '''
    Creates the DisplaysMenu menu and sub menus.
    '''
    displays = invoke_xrandr()
    menu_name = 'DisplaysMenu'
    mirrors = ''
    positions = ''
    resolutions = ''
    ##
    # Top-level menu
    menu = ''
    menu += do_top_level(menu_name, displays)

    ##
    # Individual display menu
    for display in displays.iterkeys():
        menu += '\n'
        menu += 'DestroyMenu recreate "%s"\n' % display
        if displays[display]['connected']:
            if not displays[display]['primary']:
                menu += 'AddToMenu "%s" "Set Primary" SetPrimaryDisplay "%s"\n' % (display, display) #pylint: disable=line-too-long
            if count_connected(displays) > 1:
                if count_active(displays) > 1 and display_active(displays[display]):
                    menu += 'AddToMenu "%s" "Turn off" TurnOffDisplay "%s"\n' % (display, display)
                elif not display_active(displays[display]):
                    menu += 'AddToMenu "%s" "Turn on" TurnOnDisplay "%s"\n' % (display, display)
                menu += 'AddToMenu "%s" "Mirror" Popup "Mirror-%s"\n' % (display, display) #pylint: disable=line-too-long
                mirrors += do_mirrors_menu("Mirror", 'SetMirrorMode', display, displays) #pylint: disable=line-too-long
                menu += 'AddToMenu "%s" Position Popup "Position-%s"\n' % (display, display) #pylint: disable=line-too-long
                positions += do_position_menu('Position', 'SetDisplayPosition', display, displays) #pylint: disable=line-too-long
            menu += 'AddToMenu "%s" Resolution Popup "Resolution-%s"\n'% (display, display) #pylint: disable=line-too-long
            resolutions += do_resolution_menu('Resolution', 'SetResolution', display, displays[display]) #pylint: disable=line-too-long
        else:
            menu += 'AddToMenu "%s" "disconnected" Title\n' % display

    menu += '\n'
    menu += mirrors
    menu += '\n'
    menu += positions
    menu += '\n'
    menu += resolutions
    print(menu)

def main():
    '''
    Generates the FVWM config content based on xrandr output to create the
    menus and functions for the display.
    '''
    options, args = create_parser().parse_args() #pylint: disable=unused-variable
    if not options.displays and not options.functions:
        options.functions = True

    if options.functions:
        functions()

    if options.displays:
        menus()

if __name__ == "__main__":
    main()
