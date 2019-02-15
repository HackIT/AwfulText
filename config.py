#!/usr/bin/env python
# -*- coding: utf-8 -*-

progName = "AwfulText"
progVer = "0.1a"
progIcon = "icon.png"
progUrl = "https://www.glfs.tk"
progCop = "(copydrop) by [Awaxx]."
progCom = "A wondering text editor."

__DEBUG__ = True

# logging
logpath = "/tmp/my.log"
# higlight current line
highlight_current_line = True
# show gutter with line numbers
show_line_numbers = True
# indent on tabs?
indent_on_tab = True
# follow indentation automatically
auto_indent = True
# right margin *default* position 
right_margin_position = 80
# show right margin.
show_right_margin = True
# insert spaces instead of tabs.
insert_spaces_instead_of_tabs = False
# 0 = disable, 1 = only spaces, 2 = spaces and tabs
draw_spaces = 2
# An *available* system font.
font = "Ubuntu mono 12"
# Don't show these extension into filebrowser sidepan
ignore = [ ".pyc", ".o", ".a", ".so", ".rar", ".zip", ".gz", ".xz", ".bz", ".txz", ".tgz" ]
# show hidden files
hidden_files = True
# oredered sidepane, directories first
dirs_first = True
# your file browser
file_browser = "pcmanfm"
# ======================================================
# GTK Sourceview
# Syntax highlight using the nice sourceview's schemes.
highlight_syntax = True
# Match brackets/parenthesis
highlight_matching_brackets = True
# Scheme name
scheme = "monokai-extended"
# Tab width
tab_width = 4

# ======================================================
# window related
# Window Menu
window_menu = True

# Window statusbar
window_statusbar = True

# Window sidepane
window_sidepane = True

# Window console
window_console = False

# window gutter

# futur
#use theme icon into sidepane
icon_theme = False