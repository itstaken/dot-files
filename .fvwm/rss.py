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


def escape_title(text):
    '''
    Escape the provided string so that when it is interpretted by FVWM as a
    title it will correctly dispay @ ^ % &.
    '''
    return (text.replace('@', '@@').
                 replace('^', '^^').
                 replace('*', '**').
                 replace('%', '%%').
                 replace('&', '&&'))

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
    parser.add_argument('-c, --thumbnail-scale',
                        dest='thumbscale', default='128x128',
                        help="When thumbnails are bigger than this, scale them"
                        " down to this.")  # prevents insanely large menu entry
    parser.add_argument('-l, --limit',
                        dest='limit', default=160,
                        help="Limit the text length of RSS entries")

    return parser


def get_text(node):
    '''
    Fetches the text from the specified node.
    '''
    text = ''
    for child in node.childNodes:
        text += child.data
    return text


def fetch_rss(url):
    '''
    Fetch the xml at the specified location and return it as a dom.
    '''
    opener = urllib2.build_opener()
    opener.addheaders = [('User-Agent', 'feeds.py')]
    feed = opener.open(url)
    data = feed.read()
    feed.close()
    dom = parseString(data)
    return dom


def add_suffix(name):
    '''
    Rename the provided file by appending a suffix based on the file type.
    '''
    file_typer = magic.open(magic.MAGIC_MIME)
    file_typer.load()
    mime_info = file_typer.file(name)

    # mime_info should match the pattern:
    # foo/bar; optional-stuff
    match = re.match(r'[a-z]+/([a-z]+);.*', mime_info)
    suffix = None
    if match is not None:
        suffix = match.groups()[0]
    new_name = name + '.' + suffix

    return new_name


def fetch_media(url, scale=None):
    '''
    Fetch the document stored at the specified url and save it to a tmp file,
    then return the name of that new file.
    '''
    stream = urllib2.urlopen(url)
    data = stream.read()
    stream.close()

    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(data)
    temp.close()

    new_name = add_suffix(temp.name)
    os.rename(temp.name, new_name)

    image = Image(new_name)
    # rescale the image if option looks good and image exceeds the size
    if scale is not None:
        match = re.match(r'([0-9]+)(x([0-9]+))?', scale)
        if match.groups() > 0:
            scale_width = int(match.groups()[0])
            if image.size().width() > scale_width:
                image.transform(scale)
            elif match.groups() > 1:
                scale_height = int(match.groups()[2])
                if image.size().height() > scale_height:
                    image.transform(scale)

    png_path = new_name+".png"
    image.write(png_path)
    os.unlink(new_name)

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
    if entries:
        entry = get_text(entries[0])
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

ENTRY_IMAGE_LEFT = (u"AddToMenu \"{menu}\" \"%{media}%{title}\" "
                    "Exec exec x-www-browser {opts} \"{link}\"")
ENTRY_IMAGE_ABOVE = (u"AddToMenu \"{menu}\" \"*{media}*{title}\" "
                     "Exec exec x-www-browser {opts} \"{link}\"")
ENTRY_NO_IMAGE = (u"AddToMenu \"{menu}\" \"{title}\" "
                  "Exec exec x-www-browser {opts} \"{link}\"")
ENTRY_TITLE = u"AddToMenu \"{menu}\" \"{title}\" Title"
ENTRY_PARENT = u"AddToMenu \"{parent}\" \"{title}\" Popup \"{menu}\""
ENTRY_ERROR = u'AddToMenu \"{menu}\" \"{title}\" "Nop"'
ERROR_CONNECT = "Error connecting to feed"

ENTRY_REFRESH = u"AddToMenu \"{menu}\" \"Refresh\" DestroyMenu \"{menu}\""

DESTROY_MENU = u"DestroyMenu \"{menu}\""

OUTPUT_FILE = tempfile.NamedTemporaryFile(delete=False)


def output(line):
    '''
    Outputs the provided line (carriage return will be appended) to the
    globally designated output file.
    '''
    OUTPUT_FILE.write("%s\n" % line)


def main(args):  # pylint: disable=missing-docstring
    options = build_arguments().parse_args(args[1:])
    for url in options.url:
        if options.menu is None:
            menu = url
        else:
            menu = options.menu
        try:
            dom = fetch_rss(url)
            if options.title:
                title = options.title
            else:
                title = limit(sanitize(get_single_tag(dom, "title")), options.limit)

            items = dom.getElementsByTagName("item") or dom.getElementsByTagName("entry")
            if options.parent is not None:
                output(
                    ENTRY_PARENT.format(
                        parent=options.parent,
                        title=title, menu=menu).encode("utf-8"))
            output(DESTROY_MENU.format(menu=menu).encode("utf-8"))
            output(ENTRY_TITLE.format(menu=menu,
                                      title=title).encode("utf-8"))
            for item in items:
                title = get_single_tag(item, 'title')

                content = get_single_tag(item, 'content')
                if content:
                    ##
                    # If it's reddit, good chance all the details are stuffed in an html entity...
                    content = parseString(content)
                    title = get_single_tag_attr(content, 'img', 'alt')
                    link = get_single_tag_attr(content, 'a', 'href')
                    media = get_single_tag_attr(content, 'img', 'src')

                else:

                    title = limit(escape_title(sanitize(title)),
                                  options.limit)
                    link = sanitize_link(get_single_tag(item, 'link'))
                    # media:thumbnail is what reddit uses
                    media = get_single_tag_attr(item, 'media:thumbnail', 'url')

                # FIXME: if media is None: try something else for thumb uri
                if media is not None:
                    png_path = fetch_media(media, options.thumbscale)
                    output(ENTRY_IMAGE_LEFT.format(menu=menu,
                           opts=options.browseopt, title=title, link=link,
                           media=png_path).encode("utf-8"))
                else:
                    #enclosure is what nasa uses
                    media = get_single_tag_attr(item, 'enclosure', 'url')
                    if media is not None:
                        png_path = fetch_media(media, options.scale)
                        output(ENTRY_IMAGE_ABOVE.format(menu=menu,
                               opts=options.browseopt, title=title,
                               link=link, media=png_path).encode("utf-8"))
                    else:
                        output(ENTRY_NO_IMAGE.format(menu=menu,
                               opts=options.browseopt,
                               title=title,
                               link=link).encode("utf-8"))
            output(ENTRY_REFRESH.format(menu=menu).encode("utf-8"))
        except urllib2.URLError:
            output(ENTRY_ERROR.format(menu=menu, title=ERROR_CONNECT))
    OUTPUT_FILE.close()
    os.system("FvwmCommand 'Read %s'" % OUTPUT_FILE.name)
    #immediately follow with os.unlink and read wont have time
    #to actually happen before the unlink, so tell fvwm to rm it
    os.system("FvwmCommand 'Exec exec rm %s'" % OUTPUT_FILE.name)

if __name__ == "__main__":
    main(sys.argv)
