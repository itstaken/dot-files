#!/bin/bash

##
# This script generates some font family and size selection menus.

MIN_SIZE=5
MAX_SIZE=36

##
# Create function for updating fonts so that restarting isn't needed
cat << "EOF"
DestroyFunc Refont
AddToFunc Refont
+ I SetEnv DEFAULT_FONT "xft:$[DEFAULT_FONT_FAMILY]:size=$[DEFAULT_FONT_SIZE]"
+ I SetEnv MENU_FONT "xft:$[MENU_FONT_FAMILY]:size=$[MENU_FONT_SIZE]"
+ I DefaultFont "$[DEFAULT_FONT]"
+ I MenuStyle "*" Font "$[MENU_FONT]"
+ I Schedule 250 PipeRead '$[FVWM_USERDIR]/font_helper.sh'
EOF

##
# Create a menu that is (lamely) menu font size numbers
cat << "EOF"
DestroyMenu MenuFontSizeMenu
AddToMenu MenuFontSizeMenu
EOF
for ((i=${MIN_SIZE};i<${MAX_SIZE};i++)); do
cat << EOF
+ "$i" SetMenuFontSize "$i"
EOF
done

##
# Create a menu that is (lamely) default font size numbers
cat << "EOF"
DestroyMenu DefaultFontSizeMenu
AddToMenu DefaultFontSizeMenu
EOF
for ((i=${MIN_SIZE};i<${MAX_SIZE};i++)); do
cat << EOF
+ "$i" SetDefaultFontSize "$i"
EOF
done

cat << "EOF"
DestroyMenu FontsMenu
AddToMenu FontsMenu
+ "Default Font [$[DEFAULT_FONT_FAMILY]]" Popup DefaultFontsMenu
+ "Default Font Size [$[DEFAULT_FONT_SIZE]]" Popup DefaultFontSizeMenu
+ "Menu Font [$[MENU_FONT_FAMILY]]" Popup MenuFontsMenu
+ "Font Menu Size [$[MENU_FONT_SIZE]]" Popup MenuFontSizeMenu

DestroyFunc SetDefaultFontSize
AddToFunc SetDefaultFontSize
+ I SetEnv DEFAULT_FONT_SIZE "$0"
+ I Exec exec echo SetEnv DEFAULT_FONT_SIZE "$0" > "$[fvwm_preferences_dir]"/default_font_size
+ I Refont

DestroyFunc SetMenuFontSize
AddToFunc SetMenuFontSize
+ I SetEnv MENU_FONT_SIZE "$0"
+ I Exec exec echo SetEnv MENU_FONT_SIZE "$0" > "$[fvwm_preferences_dir]"/menu_font_size
+ I Refont

DestroyFunc SetDefaultFontFamily
AddToFunc SetDefaultFontFamily
+ I SetEnv DEFAULT_FONT_FAMILY "$0"
+ I Exec exec echo SetEnv DEFAULT_FONT_FAMILY "$0" > "$[fvwm_preferences_dir]"/default_font
+ I Refont

DestroyFunc SetMenuFontFamily
AddToFunc SetMenuFontFamily
+ I SetEnv MENU_FONT_FAMILY "$0" > "$[fvwm_preferences_dir]"/menu_font
+ I Exec exec echo SetEnv MENU_FONT_FAMILY "$0" > "$[fvwm_preferences_dir]"/menu_font
+ I Refont
EOF


fc-list : family | sort -u | while read FONT ; do
    printf "AddToMenu DefaultFontsMenu \"$FONT\" SetDefaultFontFamily \"$FONT\"\n"
done

fc-list : family | sort -u | while read FONT ; do
    printf "AddToMenu MenuFontsMenu \"$FONT\" SetMenuFontFamily \"$FONT\"\n"
done

