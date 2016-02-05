#!/bin/bash

##
# This script generates some window border settings menus

MAX_SIZE=20
MENU_BORDER_SIZE=${MENU_BORDER_SIZE:-0}
WINDOW_BORDER_SIZE=${WINDOW_BORDER_SIZE:-0}

##
# Create a menu that is (lamely) menu border size numbers
cat << "EOF"
DestroyMenu MenuBorderSizeMenu
AddToMenu MenuBorderSizeMenu
EOF
for ((i=0;i<${MAX_SIZE};i++)); do
    if [ $i -eq ${MENU_BORDER_SIZE} ] ; then
cat << EOF
+ "$i (current)" Nop
EOF
    else
cat << EOF
+ "$i" SetMenuBorderSize "$i"
EOF
    fi
done

##
# And window border size numbers...
cat << "EOF"
DestroyMenu WindowBorderSizeMenu
AddToMenu WindowBorderSizeMenu
EOF
for ((i=0;i<${MAX_SIZE};i++)); do
    if [ $i -eq ${WINDOW_BORDER_SIZE} ] ; then
cat << EOF
+ "$i (current)" Nop
EOF
    else
cat << EOF
+ "$i" SetWindowBorderSize "$i"
EOF
    fi
done


cat << "EOF"
DestroyMenu BordersMenu
AddToMenu BordersMenu
+ "Menu Border Size" Popup MenuBorderSizeMenu
+ "Window Border Size" Popup WindowBorderSizeMenu

DestroyFunc SetMenuBorderSize
AddToFunc SetMenuBorderSize
+ I SetEnv MENU_BORDER_SIZE "$0"
+ I Exec exec echo SetEnv MENU_BORDER_SIZE "$0" > "$[fvwm_preferences_dir]"/menu_border_size
+ I Schedule 250 PipeRead '$[FVWM_USERDIR]/border_helper.sh'
+ I Schedule 250 FinishColorUpdate

DestroyFunc SetWindowBorderSize
AddToFunc SetWindowBorderSize
+ I SetEnv WINDOW_BORDER_SIZE "$0"
+ I Exec exec echo SetEnv WINDOW_BORDER_SIZE "$0" > "$[fvwm_preferences_dir]"/window_border_size
+ I Schedule 250 PipeRead '$[FVWM_USERDIR]/border_helper.sh'
+ I Schedule 250 FinishColorUpdate
EOF
