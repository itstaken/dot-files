dot-files
=========

These are just my dot files.  I was getting tired of setting these up all over
the place, so I'm using this as a semi-convenient location for them.

Features
--------

* Vim Config
    - Too many to mention, see comments in .vimrc and contents of .vim
      directory
* Xmodmap Settings
    - Converts Caps lock into `Super_L`
    - Convers Windows key into Escape

Installation
------------

Copy the various dot-files to your home directory. (or use `make install`)

### BSPWM/SXHKD

Requires:

 * rofi
 * kitty (terminal)

The keybindings (see sxhkdrc) are fairly standard, but I also incorporate rofi:

 * *Mod* + *space* or *Mod* + *semicolon*
    - like finder, displays a sort of run dialog
 * *Mod* + *backslash*
    - Show the window dialog, a bit like *alt* + *tab* with substring search

And keys to shove windows left or right by a desk:

 * *Mod* + *left brace* (*shift* + *[*)
     - shoves the focused node left a desk
 * *Mod* + right brace* (*shift* + *]*)
     - shoves the focused node left a desk

### Vim plugins

The `Makefile` has a target for `vim-plugins`, use `make vim-plugins` to get
all of them.

 * [ale](https://github.com/w0rp/ale) for syntax checking while editing
 * [snipmate](clone https://github.com/garbas/vim-snipmate) for templates
    - [mw-utils](https://github.com/marcweber/vim-addon-mw-utils) dep of snipmate
    - [tlib](https://github.com/tomtom/tlib_vim) dep of snipmate
 * [vim-snippets](https://github.com/honza/vim-snippets) to provide snippets for snipmate
 * [vim-markdown](https://github.com/preservim/vim-markdown) niceties for markdown
 * [vim-fugitive](https://github.com/tpope/vim-fugitive) great for git commands

After installing plugins, run `:helptags ~/.vim/pack` for updated `:help`.

You may want to look at `:help vim-markdown-disable-folding` or even `set
nofold` if you're not accustomed to folding in markdown files.  Also, `zR` to
unfold all the folds in a markdown file.  See `:help vim-markdown`.

Support
-------

There really isn't any, these are just some dot file.

License
-------

Github didn't let me pick it, but unless noted elsewhere, content here is
released under the [WTFPL](http://www.wtfpl.net).  Seriously.
