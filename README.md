dot-files
=========

These are just my dot files.  I was getting tired of setting these up all over
the place, so I'm using this as a semi-convenient location for them.

Features
--------

* FVWM
    - Config - see comments, too many to mention
    - Scripts for font selection, XRandR display menu, ...
* Vim Config
    - Too many to mention, see comments in .vimrc and contents of .vim
      directory
* Xresources (RXVT Settings)
    - Foreground/background of white/black
    - Plain scrollbar style (xtermish)
    - Ubuntu Mono and WenQuanYi fonts
    - Key bindings for ctrl+1 to ctrl+0 (change fonts)
* Xmodmap Settings
    - Converts `KP_Enter` into Insert Key (I like Shift+Insert pasting)
    - Converts Caps lock into `Super_L`
    - Convers Windows key into Escape

Installation
------------

Copy the various dot-files to your home directory. (or use make install)

In addition, the FVWM config requires FVWM, ImageMagick for generating
thumbnail menus, and some sort of x-terminal-emulator package.  For Ubuntu,
`sudo apt-get install imagemagick rxvt-unicode`.

The FVWM configuration optionally supports `xcompmgr`, `pavucontrol`,
`blueman-manager`, `bluetooth-wizard`, and any other applications that appear
with a `Test (x foo) ...` entry in the config file.

There are some scripts that I use on my laptop that can be found in the
[scripts](https://github.com/itstaken/scripts) repository.  They should all be
copletely optional...

Support
-------

There really isn't any, these are just some dot file.

License
-------

Github didn't let me pick it, but unless noted elsewhere, content here is
released under the [WTFPL](http://www.wtfpl.net).  Seriously.
