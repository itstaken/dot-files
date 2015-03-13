" mac doesn't have this on by default:
syntax enable

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

"\l to list buffers and start reading input of which to jump
nnoremap <leader>l :ls<CR>:b<space>

" I can't decide which of these I like better, a constant right margin or a
" margin that only shows up when the line goes too long.
"
"
"Put a line at the right margin so I know when I exceed the right half of the
"screen.
"set colorcolumn=81

call matchadd('ColorColumn', '\%81v', 100)
"exec 'set colorcolumn=' . join(range(2,80,3), ',')
" to set the color of the column:
" highlight ColorColumn ctermbg=magenta

" Project specific settings -
" look for a .vimrc file in the directory from where vim is launched and use
" the settings found there
set exrc

" When editing Chinese text, I'd like it to wrap like English text does.
set formatexpr+=m

" Some colorsets are better about contrast if they know the terminal is dark.
set background=dark

" This enables some unicode characters to highlight features, but doesn't
" effect line content.
set list

" This sets the specific characters used for previous command
set lcs=eol:◀,tab:▷◁,extends:▶,trail:ﬆ
" end of line shows a left arrow
" tab is replaced by ▷◁◁◁
" if text extends beyond the right side of the screen show right arrow
" trailing whitespace shows ﬆ character

" Enable bundles
execute pathogen#infect()

" Toggle the tag bar with F5
cnoremap <F5> :Tagbar<CR>

" Toggle the tag bar with F5, from insert mode, but go back to insert after
inoremap <F5> <Esc>:Tagbar<CR>a

" save on switching buffers, consider it mitigation for set hidden
" set autowrite
