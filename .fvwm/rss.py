#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Fetches rss headlines and produces an FVWM menu from them.

Any images available in the RSS will also be fetched and converted to PNG so
they may be used in an FVWM menu.

This program may be used to generate a single menu or multiple menus.

When providing multiple URLs, it's best to just specify a parent menu and let
the script decide the titles and menu names for the different sub menus.

Requirements:

    * PythonMagic (python-pythonmagick ubuntu package) for image conversion
    * python magic (python-magic) for file type detection


'''

from argparse import ArgumentParser
from PythonMagick import Image
from xml.dom.minidom import parseString
import magic
import os
import re
import sys
import tempfile
import urllib2


def limit(text, length):
    '''
    Limits the length of the provided text and appends elipsis.
    '''
    if len(text)-3 > length:
        return '%s...' % text[:length-3]
    return text


def build_arguments():
    '''
    Creates the argument parser for extracting command-line arguments.
    '''
    parser = ArgumentParser(description='Generate an FVWM menu from RSS')
    parser.add_argument('-t, --title',
                        dest='title',
                        help="Title to place on the top-level menu, "
                        "default behavior is to use the title found on the "
                        "feed itself.")
    parser.add_argument('-b, --browser-option',
                        dest='browseopt',
                        help="Any options to include in the call to "
                             "x-www-browser when opening a URL (for example "
                             "-incognito or -private)", default='-incognito')
    parser.add_argument('-m, --menu',
                        dest='menu',
                        help="The name of the menu to which the "
                        "feed entries should be added")
    parser.add_argument('-p, --parent',
                        dest='parent',
                        help="Add the generated menu to this parent menu")
    parser.add_argument('url', nargs='+',
                        help="The URL containing the RSS feed")
    parser.add_argument('-s, --scale',
                        dest='scale', default='256x256',
                        help="When enclosure images are bigger than this, "
                        "scale them down to this.")  # like image of the day
    parser.add_argument('-ts, --thumbnail-scale',
                        dest='thumbscale', default='128x128',
                        help="When thumbnails are bigger than this, scale them"
                        " down to this.")  # prevents insanely large menu entry
    parser.add_argument('-d, --destroy',
                        dest='destroy', action='store_true', default=False,
                        help="Destroy the target menu before adding entries")
    parser.add_argument('-l, --limit',
                        dest='limit', default=160,
                        help="Limit the text length of RSS entries")

    return parser


def getText(node):
    '''
    Fetches the text from the specified node.
    '''
    text = ''
    for n in node.childNodes:
        text += n.data
    return text


def fetch_rss(url):
    '''
    Fetch the xml at the specified location and return it as a dom.
    '''
    feed = urllib2.urlopen(url)
    data = feed.read()
    feed.close()
    dom = parseString(data)
    return dom


def add_suffix(name):
    '''
    Rename the provided file by appending a suffix based on the file type.
    '''
    m = magic.open(magic.MAGIC_MIME)
    m.load()
    mime_info = m.file(name)

    # mime_info should match the pattern:
    # foo/bar; optional-stuff
    m = re.match(r'[a-z]+/([a-z]+);.*', mime_info)
    suffix = None
    if m is not None:
        suffix = m.groups()[0]
    new_name = name + '.' + suffix

    return new_name


def fetch_media(url, scale=None):
    '''
    Fetch the document stored at the specified url and save it to a tmp file,
    then return the name of that new file.
    '''
    f = urllib2.urlopen(url)
    data = f.read()
    f.close()

    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(data)
    f.close()

    new_name = add_suffix(f.name)
    os.rename(f.name, new_name)

    image = Image(new_name)
    # rescale the image if option looks good and image exceeds the size
    if scale is not None:
        m = re.match(r'([0-9]+)(x([0-9]+))?', scale)
        if m.groups() > 0:
            scale_width = int(m.groups()[0])
            if image.size().width() > scale_width:
                image.transform(scale)
            elif m.groups() > 1:
                scale_height = int(m.groups()[2])
                if image.size().height() > scale_height:
                    image.transform(scale)

    png_path = new_name+".png"
    image.write(png_path)

    return png_path


def sanitize(text):
    '''
    Removes double quotes from the provided text.
    This is a place holder for removing other syntax that might break an FVWM
    title/entry.
    '''
    return text.replace('"', '').replace('\n', '').replace('\r', '')


def sanitize_link(link):
    '''
    Everything is quoted in the output, so if quotes are encountered in the
    link string, turn them into %25s.

    This is a place holder for removing other syntax that might break an FVWM
    Exec entry or provide a path of execution to something other than the web
    browser via a link.
    '''
    return link.replace('"', '%27').replace('\n', '%0A').replace('\r', '%0D')


def get_single_tag(element, tag):
    '''
    Fetches the text from the first tag found with the given name.
    '''
    entry = None
    entries = element.getElementsByTagName(tag)
    if len(entries) > 0:
        entry = getText(entries[0])
    return entry


def get_single_tag_attr(element, tag, attr):
    '''
    Fetches the attribute from the first tag found with the given name.
    '''
    entry = None
    entries = element.getElementsByTagName(tag)
    if len(entries) > 0:
        entry = entries[0]
    if entry is not None:
        entry = entry.getAttribute(attr)

    return entry

# FIXME: add more sanitizing!

ENTRY_IMAGE_LEFT = (u"AddToMenu {menu} \"%{media}%{title}\" "
                    "Exec exec x-www-browser {opts} \"{link}\"")
ENTRY_IMAGE_ABOVE = (u"AddToMenu {menu} \"*{media}*{title}\" "
                     "Exec exec x-www-browser {opts} \"{link}\"")
ENTRY_NO_IMAGE = (u"AddToMenu {menu} \"{title}\" "
                  "Exec exec x-www-browser {opts} \"{link}\"")
ENTRY_TITLE = u"AddToMenu {menu} \"{title}\" Title"
ENTRY_PARENT = u"AddToMenu {parent} \"{title}\" Popup \"{menu}\""

DESTROY_MENU = u"DestroyMenu {menu}"


def main(args):
    options = build_arguments().parse_args(args[1:])
    for url in options.url:
        dom = fetch_rss(url)
        if options.title is None:
            title = limit(sanitize(get_single_tag(dom, "title")),
                          options.limit)
        else:
            title = options.title

        if options.menu is None:
            menu = url
        else:
            menu = options.menu

        items = dom.getElementsByTagName("item")
        if options.parent is not None:
            print(ENTRY_PARENT.format(
                  parent=options.parent,
                  title=title, menu=menu).encode("utf-8"))
        if options.destroy:
            print(DESTROY_MENU.format(menu=menu).encode("utf-8"))
        print(ENTRY_TITLE.format(menu=menu,
              title=title).encode("utf-8"))
        for item in items:
            title = limit(sanitize(get_single_tag(item, 'title')),
                          options.limit)
            link = sanitize_link(get_single_tag(item, 'link'))
            # media:thumbnail is what reddit uses
            media = get_single_tag_attr(item, 'media:thumbnail', 'url')
            # FIXME: if media is None: try something else for the thumbnail uri
            if media is not None:
                png_path = fetch_media(media, options.thumbscale)
                print(ENTRY_IMAGE_LEFT.format(menu=menu,
                      opts=options.browseopt, title=title, link=link,
                      media=png_path).encode("utf-8"))
            else:
                #enclosure is what nasa uses
                media = get_single_tag_attr(item, 'enclosure', 'url')
                if media is not None:
                    png_path = fetch_media(media, options.scale)
                    print(ENTRY_IMAGE_ABOVE.format(menu=menu,
                          opts=options.browseopt, title=title,
                          link=link, media=png_path).encode("utf-8"))
                else:
                    print(ENTRY_NO_IMAGE.format(menu=menu,
                          opts=options.browseopt,
                          title=title,
                          link=link).encode("utf-8"))

if __name__ == "__main__":
    main(sys.argv)