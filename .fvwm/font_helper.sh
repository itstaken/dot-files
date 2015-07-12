#!/bin/bash

##
# This script generates some font family and size selection menus.

MIN_SIZE=5
MAX_SIZE=36

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

DestroyMenu SetDefaultFontSize
AddToMenu SetDefaultFontSize
+ I Exec exec echo SetEnv DEFAULT_FONT_SIZE "$0" > "$[fvwm_preferences_dir]"/default_font_size
+ I Schedule 250 Restart

DestroyFunc SetMenuFontSize
AddToFunc SetMenuFontSize
+ I Exec exec echo SetEnv MENU_FONT_SIZE "$0" > "$[fvwm_preferences_dir]"/menu_font_size
+ I Schedule 250 Restart

DestroyFunc SetDefaultFontFamily
AddToFunc SetDefaultFontFamily
+ I Exec exec echo SetEnv DEFAULT_FONT_FAMILY "$0" > "$[fvwm_preferences_dir]"/default_font
+ I Schedule 250 Restart

DestroyFunc SetMenuFontFamily
AddToFunc SetMenuFontFamily
+ I Exec exec echo SetEnv MENU_FONT_FAMILY "$0" > "$[fvwm_preferences_dir]"/menu_font
+ I Schedule 250 Restart
EOF


fc-list : family | sort -u | while read FONT ; do
    printf "AddToMenu DefaultFontsMenu \"$FONT\" SetDefaultFontFamily \"$FONT\"\n"
done

fc-list : family | sort -u | while read FONT ; do
    printf "AddToMenu MenuFontsMenu \"$FONT\" SetMenuFontFamily \"$FONT\"\n"
done

