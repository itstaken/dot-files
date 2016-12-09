#!/bin/bash

##
# This script generates some color selection menus for customizing the color
# schemes.
#
# This script relies heavily on content in my personal FVWM configuration.  To
# make it work with your own config you would have to copy large chunks of my
# configuration.  Essentially, the Block of "Color Preferences" from the
# beginning of my configuration (including window borders, BORDER_ACTIVE and
# BORDER_INACTIVE), the SetEnv of fvwm_color_preferences and
# fvwm_preferences_dir, the ChangeColor function, the DoColorSets function, and
# the FinishColorUpdate function would all need to be copied from my config.
#
# Then, add a call to this script to read the function and append the menu.
# For example:
#
#     AddToFunc StartFunction
#     + I Module FvwmCommandS
#     + I PipeRead bash $[FVWM_USERDIR]/theme_customize.sh -m ThemeMenu
#     AddToMenu MenuFvwmRoot
#     + "Change Color Settings" Popup ThemeMenu
#

##
# And fuck you very much zenity for not having a consistent return value on
# different versions of ubuntu and no documented place of what it will be...
fix_color(){
    VALUE=${1}
    if [[ "${VALUE}" =~ "#[0-9A-Fa-f]{12}" ]] ; then
        COLOR=$(echo $COLOR | sed 's/\(#\?..\)../\1/g')
    elif [[ "${VALUE}" =~ rgb\(([0-9]+),([0-9]+),([0-9]+)\) ]] ; then
        COLOR="$(printf "#%02x%02x%02x" ${BASH_REMATCH[1]} ${BASH_REMATCH[2]} ${BASH_REMATCH[3]})"
    fi
    echo "${COLOR}"
}

do_color_pick(){
    COLOR=$(zenity --color-selection --color=$(eval "echo \$${TAG}") --title "Choose a color for ${NV_COLOR[${TAG}]}")
    if [ $? -eq 0 ] ; then
        COLOR=$(fix_color ${COLOR})
        #Note, this would work, too, but wouldn't save the color:
        #FvwmCommand "SetEnv ${TAG} ${COLOR}"
        #FvwmCommand FinishColorUpdate
        ##
        # So I opted for this, instead:
        eval "export ${TAG}=${COLOR}"
        FvwmCommand "ChangeColor ${FG_COLOR} ${BG_COLOR} ${FG_COLOR_INACTIVE} ${BG_COLOR_INACTIVE} ${HILIGHT_FORE} ${HILIGHT_BACK} ${SHADE} ${FGSHADOW} ${BORDER_ACTIVE} ${BORDER_INACTIVE}"
    fi
}

update_images(){
    for KEY in FG_COLOR BG_COLOR FG_COLOR_INACTIVE BG_COLOR_INACTIVE HILIGHT_FORE HILIGHT_BACK SHADE FGSHADOW BORDER_ACTIVE BORDER_INACTIVE ; do
        eval "export COLOR=\$${KEY}"
        convert -size 64x64 xc:${COLOR} /tmp/${KEY}.png
    done
}


do_menu(){
    update_images

for KEY in FG_COLOR BG_COLOR FG_COLOR_INACTIVE BG_COLOR_INACTIVE HILIGHT_FORE HILIGHT_BACK SHADE FGSHADOW BORDER_ACTIVE BORDER_INACTIVE ; do

    cat << EOF
AddToMenu ${MENU} "%/tmp/${KEY}.png%${NV_COLOR[${KEY}]}" Exec exec bash "$0" -p ${KEY}
EOF

done
}

do_func(){
    cat << EOF

DestroyMenu ${MENU}
AddToMenu ${MENU}
+ DynamicPopupAction CustomColorFunc

DestroyFunc CustomColorFunc
AddToFunc CustomColorFunc
+ I DestroyMenu recreate ${MENU}
+ I PipeRead 'bash "$0" -m ${MENU}'
EOF

}

do_help(){
    cat << EOF
This script generates a menu for FVWM that lets the user pick new colors for
different aspects of the colorset being used.  The back-end will shell out to
zenity for color picking and then issue commands back to FVWM via the
FvwmCommand module.

Invoke with -m MenuName, for example: theme_customize.sh -m ThemeMenu
To generate a top-level menu.

The menu will then invoke the script via the -p VARIABLE option which will
display zenity.  If the user picks a color, it will be sent back to fvwm via
FvwmCommand and call ChangeColor to effect the change.
EOF
}

declare -A NV_COLOR
NV_COLOR["FG_COLOR"]="Foreground"
NV_COLOR["BG_COLOR"]="Background"
NV_COLOR["FG_COLOR_INACTIVE"]="Inactive Foreground"
NV_COLOR["BG_COLOR_INACTIVE"]="Inactive Background"
NV_COLOR["HILIGHT_FORE"]="Hilight Foreground"
NV_COLOR["HILIGHT_BACK"]="Hilight Background"
NV_COLOR["SHADE"]="Shade color"
NV_COLOR["FGSHADOW"]="Shadow Color"
NV_COLOR["BORDER_ACTIVE"]="Active Window Border Color"
NV_COLOR["BORDER_INACTIVE"]="Inactive Window Border Color"

while getopts "f:p:m:h" OPT ; do
    case "${OPT}" in
        f) #generate the function for generating the menus
            ACTION=function
            MENU=${OPTARG}
            ;;
        p) #pick a color for the specified variable
            TAG=${OPTARG}
            ACTION=pick
            ;;
        m)
            ACTION=menu
            MENU=${OPTARG}
            ;;
        \?)
            ACTION=help
            ;;
    esac
done
shift $((OPTIND-1))

case "${ACTION}" in
    "pick")
        do_color_pick
        ;;
    "menu")
        do_menu
        ;;
    "function")
        do_func
        ;;
    *)
        do_help
        ;;
esac
