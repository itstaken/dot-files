
" Perform indenting according to syntax of the file type and turn on other
" language perks
filetype plugin indent on

" Lets you do :Man [section] manpage
runtime ftplugin/man.vim

" This can be annoying, but it makes it hilight the search terms
" It can be (temporarily) turned off with :nohl
set hlsearch

" This can also be annoying, performs incremental searching, which jumps the
" editor around as you're typing in a search phrase, but you still have to hit
" return to perform the search
set incsearch

" Turn on line numbers
set nu
" Make the spelling match for english US instead of those heathen variants ;-)
set spelllang=en_us

" This will use 4 spaces for tabs and indents and replace tab with spaces
set sw=4
set ts=4
set expandtab

" This usually doesn't work, but set title string so that xterms are renamed
" to Vim - filename
autocmd BufEnter * let &titlestring = "Vim - " . expand("%:t")

" This is awesome: enables closing (hiding) buffers with unwritten changes
" and then when closed buffers are re-opened, the entire undo history is still
" available!
set hidden

" Stop visual wrapping of text, toggle with :set wrap!
set nowrap

" I like a clean top-level project directory with a src beneath that, this
" setting enables me to still use tags and `gf` shortcuts while editing from
" such a top level.
set path=src/,usr/include,.
