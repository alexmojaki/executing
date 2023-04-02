
'4.60.3.85 Unreleased'
_change_log = '\n    Changelog since 4.60.0 released to PyPI on 8-May-2022\n    \n    4.60.0.1\n        main_open_github_issue - prefill the "Details" using the platform module (thank you macdeport!)\n            Fills Mac, Windows and Linux with details\n    4.60.0.2\n        Fix for the "jumping window problem on Linux".  Major credit to Chr0nic for his amazing "stick with it" work on this problem!\n    4.60.0.3\n        Removed the previous fix attempt for jumping window on linux\n        Added ability for Mac users to specify file_type in Browse and popup_get_file\n            This feature must be ENABLED by the user in the Mac control panel that can be found in the PySimpleGUI Global Settings\n            The default is this feature is OFF\n    4.60.0.4\n        New location parameter option for Windows. Setting location=None tells PySimpleGUI to not set any location when window is created. It\'s up to the OS to decide.\n            The docstring for Window has been changed, but not all the other places (like popup). Want to make sure this works before making all those changes.            \n    4.60.0.5\n        Added check for None invalid values parm when creating a Listbox element\n    4.60.0.6\n        Column docstring changed to add reminder to call contents_changed if changing the contents of a scrollable column\n    4.60.0.7\n        Fixed crash when horizontal_scroll=True for Listbox element\n    4.60.0.8\n        Added readonly to Input.update\n    4.60.0.9\n        Added Window.set_resizable - can change the X and Y axis resizing after window is created\n    4.60.0.10\n        Added wrap parameter to Spin element - if True, wraps back to the first value when at the end\n        Temp test code added for a new verification feature\n    4.60.0.11\n        Fixed Spin Element docstring - readonly was not correct\n    4.60.0.12\n        Output element - addition of wrap_lines and horizontal_scroll parameters\n        Multiline element -  addition of wrap_lines parameter\n    4.60.0.13\n        Added Window.unbind\n    4.60.0.14\n        Added (None, None) to the Window docstring\n    4.60.0.15\n        Fix for continuous Graph element mouse up events when reading with a timeout=0. Big thank you to @davesmivers (THANKS DAVE!!) for finding and fixing\n    4.60.0.16\n        Added platform (Windows, Mac, Linux) and platform version information to the get_versions function\n    4.60.0.17\n        Added a fix for the file_types Mac problem that doesn\'t require the system settings to be used... let\'s give it a go!\n    4.60.0.18\n        Added ubiquitious Edit Me to the right click menu\n    4.60.0.19\n        PySimpleGUI Anniversary sale on Udemy course coupon \n    4.60.0.20\n        Fix for bind_return_key - if a button has been disabled, then the event shouldn\'t be generated for the return key being pressed\n    4.60.0.21\n        Added cols_justification for Table element - list or tuple of strings that indicates how each column should be justified\n    4.60.0.22\n        Better error handling for table element\'s new justification list. If a bad value is found, will use the default value\n    4.60.0.23\n        Additional mac filetype testing.... added more combinations that specify \n    4.60.0.24\n        Added * *.* to the Mac filetypes to check for\n    4.60.0.25\n        New logic for checking for the * case for Mac filetypes\n    4.60.0.26\n        Docstring update - TabGroup visible parameter marked as deprecated .  Use a Column element to make a TabGroup invisible\n    4.60.0.27\n        Docstring update for the pin helper function that describes the shrinking of the container that it helps provide.  \n        Also added explanation that it\'s the elements you want to make visible/invisible that are what you want to pin\n    4.60.0.28\n        Applied same Mac file_types fix to popup_get_file\n        Removed filetypes setting from Mac Feature Control Panel\n    4.60.0.29\n        Addition of enable_window_config_events to the Window object. This will cause a EVENT_WIMDOW_CONFIG event to be returned\n            if the window is moved or resized.\n    4.60.0.30\n        Made upgrade from GitHub window resizable so can screencapture the entire session\n    4.60.0.31\n        Added new constant TKINTER_CURSORS which contains a list of the standard tkinter cursor names\n    4.60.0.32\n        Added erase_all parameter to cprint (like the Debug Print already has)\n    4.60.0.33\n        Fix popup_scrolled - was only adding the Sizegrip when there was no titlebar.  It should be added to all windows\n            unless the no_sizegrip parameter is set.\n        popup_scrolled - added no_buttons option. If True then there will not be a row at the bottom where the buttons normally are.\n            User will have to close the window with the "X"\n    4.60.0.34\n        popup_scrolled - added button_justification parameter. Wanted to make scrolled popups consistent with other popups which have left justified\n            buttons.  But since they\'ve been right justified in the past, want to give users the ability to retain that look. \n            Since the Sizegrip works correctly now, it increases the changes of accidently clicking a button if it\'s right justified.\n    4.60.0.35\n        Added default_color to ColorChooser button\n    4.60.0.36\n        Added to Button element error message that images must be in PNG or GIF format\n    4.60.0.37\n        Added exapnd_x and expand_y to all of the "lazy buttons" and Chooser buttons\n    4.60.0.38\n        Column element - added horizontal_scroll_only parameter (fingers crossed on this one....)\n    4.60.0.39\n        New signature testing\n    4.60.0.40\n        Exposed the Table Element\'s ttk style using member variable TABLE.table_ttk_style_name\n    4.60.0.41\n        New signature format\n    4.60.0.42\n        Backed out the changes from 4.60.0.38 (horizontal_scroll_only parameter).  Those changes broke code in the scrollable columns.  Need to make time to work on this feature more.\n    4.60.0.43\n        Added a print if get an exception trying to set the alpha channel after a window is created (troubleshooting a Mac problem)\n    4.60.0.44\n        Updated Menubar docstring to clarify the Menubar iself cannot have colors changed, only the submenus. Use MenubarCustom if you want full control\n        Format of file-signature changed\n    4.60.0.45\n        Further refinement of Menubar docstring\n    4.60.0.46\n        Added suggestion of using the Demo Browser to the checklist item of "Look for Demo Programs similar to your problem"\n    4.60.0.47\n        Testing some importing methods\n        Delay rerouting stdout and stderr in Output and Multiline elements until window is being built instead of when element is initialized\n    4.60.0.48\n        Additional window movement capability. If Control+Mouse movement feature is enabled, then Control+Arrow key will move the window 1 pixel\n            in the indicated direction\n    4.60.0.49\n        Added Window.set_size to match the other settings that are performed through method calls. There is also the Window.size property, but\n            since PySimpleGUI rarely uses properties, it makes sense to include a method as well as a property\n    4.60.0.50\n        Fix for ColorChooser button filling in a None value when cancel from color choise dialog box.  Nothing will be filled in target if dialog cancelled\n    4.60.0.51\n        vtop, vcenter, vbottom helper functions gets background_color parameter\n        vcenter and vbottom - added USING the expand_x and expand_y parms that were already defined.  (HOPE NOTHING BREAKS!)\n    4.60.0.52\n        justification parameter added to Listbox (default is left.. can be right and center now too)\n    4.60.0.53\n        Made settings dictionary multiline in test harness write-only.  New coupon code                \n    4.60.0.54\n        alpha_channel added to set_options.  This sets the default value for the alpha_channel for all windows both user generated and PySimpleGUI generated (such as popups).\n    4.60.0.55\n        Allow Browse/Chooser buttons (that have a target) to indicate a target key that is a tuple.\n    4.60.1.55\n        While not actually correct.... 4.60.1 was released in the middle of the development above... I\'m changing the version to look as\n            if this release is based on 4.60.1.  This code DOES have the same code that\'s in 4.60.1 so it\'s more a matter of symantics.\n            Hoping this clears up confusion.  Sorry for the dot-release causing so much confusion.\n    4.60.1.56\n        Fix for Window.extend_layout.  Was not picking up the background color of the container that the rows were being added to.\n    4.60.1.57\n        Fixed Text element\'s update method docstring to indicate that value can be "Any" type not just strings\n    4.60.1.58\n        Addition of without_titlebar paramter to Window.current_location.  Defaults to False.  If True, then the location of the main portion of the window\n            will be returned (i.e. will not have the titlebar)\n    4.60.1.59\n        Fix for crash if COLOR_SYSTEM_DEFAULT specified in parameter disabled_readonly_background_color or disabled_readonly_text_color for Input Element.\n        Also applied similar fix for Tab element\'s focus color\n    4.60.1.60\n        Addition of set_option parameter hide_window_when_creating. If set to False then window will not be hidden while creating and moving\n    4.60.1.61\n        Changed the documentation location to PySimpleGUI.org (updated some comments as well as the SDK Reference Window\'s links)\n        New coupon code.  Make the Udemy button in the test harness now include the coupon code automatically\n    4.60.1.62\n        Removed the "NOT avoilable on the MAC" from file_types parameter in the docstrings\n        Use Withdraw to hide window during creation\n    4.60.1.63\n        Addition of checklist item when logging new issue to  GitHub - upgraded to latest version of PySimpleGUI on PyPI\n        Listbox justification parameter found to not be implemented on some early verions of tkinter so had to protect this situation. This new feature crached on the Pi for example\n    4.60.1.64\n        Allow set_options(window_location=None) to indicate the OS should provide the window location.  \n            This will stop the Alpha channel being set to 0 when the window is created\n    4.60.1.65\n        Addition of new Mac Control Panel option and emergency patch for MacOS version 12.3+\n            If MacOS version 12.3 or greater than option is ON by default\n            When ON, the default Alpha channel for all windows is set to 0.99. \n            This can either be turned off, or can be overridden by calling set_options in your application\n    4.60.2.65\n        Bumping version number to avoid confusion.  An emergency 4.60.2 release was posted to PyPI. This change was added to this current GitHub version of PySimpleGUI.  \n    4.60.3.66\n        Fixed bug in checking Mac OS version number that is being released as 4.60.3\n    4.60.3.67\n        Correctly check for Mac 12.3+ AND 13+ this time.\n    4.60.3.68\n        Roll in the changes being released to PyPI as 4.60.3\n    4.60.3.69\n        Test to see if the additional pack of Notebook in Tab code was causing expansion problems        \n    4.60.3.70\n        Debug Print - fix for bug caused by no_button being set with non_blocking... a lesson in thorough testing... assumption was either blocking OR no_button (or else app would\n            close without seeing the output... unless something else blocked. (DOH)\n    4.60.3.71\n        "Window closed" check added to update methods for elements. This will prevent a crash and instead show an error popup\n            Will be helpful for users that forget to check for closed window event in their event loop and try to call update after window closed. \n    4.60.3.72\n        Output element now automatically sets auto_refresh to True.   Should this not be desired, switch to using the Multiline element.  There will likely be\n            no impact to this change as it seems like the windows are alredy refreshing OK, but adding it just to be sure.\n    4.60.3.73\n        Addition of Window.key_is_good(key) method.  Returns True if key is used in the window. Saves from having to understand the window\'s key dictionary.\n            Makes for easier code completion versus writing  "if key in window.key_dict"\n    4.60.3.74\n        Combo - if readonly, then set the select colors to be "transparent" (text=text color, background=background color)\n    4.60.3.75\n        Better description of bar_color parm for the ProgressMeter element and the one_line_progress_meter function\n        Combo element - addition of select parameter to enable easier selection of the contents of clearing of the selection of the contents.\n    4.60.3.76\n        Changed the _this_elements_window_closed to use a flag "quick_check" for cheking is the window is closed.  Found that calling tkinter.update takes over 500ms sometimes!\n            For appllications that call update frequently, this caused a catestrophic slowdown for complex windows.\n    4.60.3.77\n        New Window method - get_scaling - gets the scaling value from tkinter.  Returns DEFAULT_SCALING if error.\n    4.60.3.78\n        Custom Titlebar - Support added to Window.minimize, Window.maximize, and Window.normal\n    4.60.3.79\n        Fix for Mulitline showing constant error messages after a Window is closed. \n        Fix for correctly restoring stdout, stderr after they\'ve been rerouted. THIS CODE IS NOT YET COMPLETE! Shooting for this weekend to get it done!\n        Image element - more speicific with tkinter when chaning to a new image so that pypy would stop crashing due to garbage collect not running. \n            This change didn\'t fix the pypy problem but it also didn\'t hurt the code to have it\n    4.60.3.80\n        Quick and dirty addition of Alt-shortcuts for Buttons (like exists for Menus)\n            For backward compatablity, must be enabled using set_options with use_button_shortcuts=True\n        Fixed docstring errors in set_options docstring\n    4.60.3.81\n        Completed restoration of stdout & stderr\n            If an Output Element is used or a Multline element to reroute stdout and/or stderr, then this hasn\'t worked quite right in the past\n            Hopefuly now, it does.  A LIFO list (stack) is used to keep track of the current output device and is scrubbed for closed windows and restored if one is closed\n    4.60.3.82\n        Addition of Style Names for horizaontal and vertical ttk scrollbars - hsb_style_name and vsb_style_name so that scrollbar colors can be changed in user code\n    4.60.3.83\n        Output element - now automatically rereoutes cprint to here as well. Assumption is that you want stuff to go here without\n            needing to specify each thing.  If want more control, then use the Multline directly\n    4.60.3.84\n        Output element - updated docstring\n    4.60.3.85\n        Combo Element - new parameter enable_per_char_events.  When True will get an event when individual characters are entered.\n    '
try:
    version.split(' ')
except:
    ver = ''
port = 'PySimpleGUI'
import tkinter as tk
from tkinter import filedialog
from tkinter.colorchooser import askcolor
from tkinter import ttk
import tkinter.font
from uuid import uuid4
tkinter.Tcl().eval('info patchlevel')
framework_version = tclversion_detailed
import time
import pickle
import calendar
import datetime
import textwrap
from hashlib import sha256 as hh
import inspect
import traceback
import difflib
import copy
import pprint
try:
    from typing import List, Any, Union, Tuple, Dict, SupportsAbs, Optional
except:
    print('*** Skipping import of Typing module. "pip3 install typing" to remove this warning ***')
import random
from math import floor
from math import fabs
from functools import wraps
try:
    import subprocess
except Exception as e:
    '** Import error {} **'.format
import threading
import itertools
import json
import configparser
import queue
try:
    import webbrowser
    webbrowser_available = True
except:
    webbrowser_available = False
import urllib.request
import urllib.error
import urllib.parse
import pydoc
from urllib import request
import os
import sys
import re
warnings.simplefilter('always', UserWarning)

def timer_start():
    pass

def timer_stop():
    pass

def _timeit():
    pass
MAX_TIMEIT_COUNT = 1000

def _timeit_summary():
    pass

def running_linux():
    pass

def running_mac():
    pass

def running_windows():
    pass

def running_trinket():
    pass

def running_replit():
    pass
DEFAULT_BASE64_ICON = b'R0lGODlhIQAgAPcAAAAAADBpmDBqmTFqmjJrmzJsnDNtnTRrmTZtmzZumzRtnTdunDRunTRunjVvnzdwnzhwnjlxnzVwoDZxoTdyojhzozl0ozh0pDp1pjp2pjp2pzx0oj12pD52pTt3qD54pjt4qDx4qDx5qTx5qj16qj57qz57rD58rT98rkB4pkJ7q0J9rEB9rkF+rkB+r0d9qkZ/rEl7o0h8p0x9pk5/p0l+qUB+sEyBrE2Crk2Er0KAsUKAskSCtEeEtUWEtkaGuEiHuEiHukiIu0qKu0mJvEmKvEqLvk2Nv1GErVGFr1SFrVGHslaHsFCItFSIs1COvlaPvFiJsVyRuWCNsWSPsWeQs2SQtGaRtW+Wt2qVuGmZv3GYuHSdv3ievXyfvV2XxGWZwmScx2mfyXafwHikyP7TPP/UO//UPP/UPf/UPv7UP//VQP/WQP/WQf/WQv/XQ//WRP7XSf/XSv/YRf/YRv/YR//YSP/YSf/YSv/ZS//aSv/aS/7YTv/aTP/aTf/bTv/bT//cT/7aUf/cUP/cUf/cUv/cU//dVP/dVf7dVv/eVv/eV//eWP/eWf/fWv/fW/7cX/7cYf7cZP7eZf7dav7eb//gW//gXP/gXf/gXv/gX//gYP/hYf/hYv/iYf/iYv7iZP7iZf/iZv/kZv7iaP/kaP/ka//ma//lbP/lbv/mbP/mbv7hdP7lcP/ncP/nc//ndv7gef7gev7iff7ke/7kfv7lf//ocf/ocv/odP/odv/peP/pe//ofIClw4Ory4GszoSszIqqxI+vyoSv0JGvx5OxyZSxyZSzzJi0y5m2zpC10pi715++16C6z6a/05/A2qHC3aXB2K3I3bLH2brP4P7jgv7jh/7mgf7lhP7mhf7liv/qgP7qh/7qiP7rjf7sjP7nkv7nlv7nmP7pkP7qkP7rkv7rlv7slP7sl/7qmv7rnv7snv7sn/7un/7sqv7vq/7vrf7wpv7wqf7wrv7wsv7wtv7ytv7zvP7zv8LU48LV5c3a5f70wP7z0AAAACH5BAEAAP8ALAAAAAAhACAAAAj/AP8JHEiwoMGDCA1uoYIF4bhK1vwlPOjlQICLApwVpFTGzBk1siYSrCLgoskFyQZKMsOypRyR/GKYnBkgQbF/s8603KnmWkIaNIMaw6lzZ8tYB2cIWMo0KIJj/7YV9XgGDRo14gpOIUBggNevXpkKGCDsXySradSoZcMmDsFnDxpEKEC3bl2uXCFQ+7emjV83bt7AgTNroJINAq0wWBxBgYHHdgt0+cdnMJw5c+jQqYNnoARkAx04kPEvS4PTqBswuPIPUp06duzcuYMHT55wAjkwEahsQgqBNSQIHy582D9BePTs2dOnjx8/f1gJ9GXhRpTqApFQoDChu3cOAps///9D/g+gQvYGjrlw4cU/fUnYX6hAn34HgZMABQo0iJB/Qoe8UxAXOQiEg3wIXvCBQLUU4mAhh0R4SCLqJOSEBhhqkAEGHIYgUDaGICIiIoossogj6yBUTQ4htNgiCCB4oIJAtJTIyI2MOOLIIxMtQQIJIwQZpAgwCKRNI43o6Igll1ySSTsI7dOECSaUYOWVKwhkiyVMYuJlJpp0IpA6oJRTkBQopHnCmmu2IBA2mmQi5yZ0fgJKPP+0IwoooZwzkDQ2uCCoCywUyoIW/5DDyaKefOLoJ6LU8w87pJgDTzqmDNSMDpzqYMOnn/7yTyiglBqKKKOMUopA7JgCy0DdeMEjUDM71GqrrcH8QwqqqpbiayqToqJKLwN5g45A0/TAw7LL2krGP634aoopp5yiiiqrZLuKK+jg444uBIHhw7g+MMsDFP/k4wq22rririu4xItLLriAUxAQ5ObrwzL/0PPKu7fIK3C8uxz0w8EIIwzMP/cM7HC88hxEzBBCBGGxxT8AwQzDujws7zcJQVMEEUKUbPITAt1D78OSivSFEUXEXATKA+HTscC80CPSQNGEccQRYhjUDzfxcjPPzkgnLVBAADs='
DEFAULT_BASE64_ICON_16_BY_16 = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAKCSURBVDhPVZNbSFRRFIb35YwXItBIGtDsiqENEUTRjJlZkJggPSUYBD0UhULElE6hBY6ID/ZSpD1IDxaCEPhUaFLRQyWRNxIJe8syMxCjMCbB07fOsaMt+GftvWf//7/2Whyt1sTei/fCpDqQBTrGOi9Myrk7URwhnQUfQLeOvErJuUQgADlK6gObvAOl5sHx0doHljwARFRiCpxG5J1sjPxALiYNgn9kiQ3gafdYUYzseCd+FICX7sShw7LR++q6cl3XHaXQHFdOJLxFsJtvKHnbUr1nqp01hhStpXAzo7TZZXOjJ+9orT9pY74aY3ZobZZYW8D/GpjM19Ob088fmJxW2tkC4AJt17Oeg2MLrHX6jXWes16w1sbBkrFWBTB2nTLpv5VJg7wGNhRDwCS0tR1cbECkidwMQohAdoScqiz8/FCZUKlPCgSWlQ71elOI1fcco9hCXp1kS7dX3u+qVOm2L4nW8qE4Neetvl8v83NOb++9703BcUI/cU3imuWV7JedKtv5LdFaMRzHLW+N+zJoVDZzRLj6SFNfPlMYwy5bDiRcCojmz15tKx+6hKPv7LvjrG/Q2RoOwjSyzNDlahyzA2dAJeNtFcMHA2cfLn24STNr6P4I728jJ7hvf/lEGuaXLnkRAp0PyFK+hlyLSJGyGWnKyeBi2oJU0IPIjNd15uuL2f2PJgueQBKhVRETCgNeYU+xaeEpnWaw8cQPRM7g/McT8eF0De9u7P+49TqXF7no98BDEEkdvvXem8LAtfJniFRB/A5XeiAiG2+/icgHVQUW5d5KyAhl3M2y+U+ysv1FDukyKGQW3Y+vHJWvU7mz8RJSPZgDd3H2RqiUUn8BSQuaBvGjGpsAAAAASUVORK5CYII='
DEFAULT_BASE64_LOADING_GIF = b'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'
PSG_DEBUGGER_LOGO = b'iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAALiIAAC4iAari3ZIAAA2CSURBVHhe7VtplBXFGe03qBiN+RGJJjEGFGZYXWMETDhhZFEGDaA4KCbnmOTo0UQx7AwgMIDs+4ggGlAjI/BERxY3loggHpGdgRkGJlFQzxFzNCd6NC6hc28tXVXd/XrevBnyI/HC7ar6vuru735V1a9f9xvvG/yfI6XKBuO+QYN/hKIT+H1h8Lz3wG1lC+Z+KJu5obDrtc1QtAVPB98Ha/7y6uaTKBsFDUoARHP/m8BhYEcwfLyvwTQ4Gol4W1iyBIRfhmIa2ANsQpvCR+Cz4EIkYq+wNAA5JwDiL0TxJNhVGJLxMdgPSdgim8mA+GIUPHZTYYiHDz4PjkAijghLDsgpARDfC8VT4HeFITt8DvZBEjbIZjyU+OXgacJQN/4FcqZMRSK+FJZ6oF4JUFN+JDgZtKdltkhMQg7ibewH70AS9shmdsg6ARDPoJaAvxGG3BGbhAaK1/gCHAry+iAMdSGrBED8t1CsBG8UhobDSQLE34KiHGyIeBvLwLuzWRJ5qswIJf45sLHEEzzm8zg2r/AEE/JvWW0UcJauQWJ5nkQkzgAEeAaKNeB1wtD4CGYCgr0B9WfApCt/ffEy2A8zgeeJRcYZMOj+IUwOp9KpEk8EMwFBrkO9P8h13Fi4zvP9ZV1/UZhxoDMmIJVKTc3LyxsIeiTaiWwAGj8Jvo//ip43ABXeqMUiNvLBQ4YPRMHP+RQPkoQkfz33rf9ykAJj4R7b/xIdr9qydcsBZQgQScDQYSPbo3gTBzhbWuLRiMJtiCTMnzebSeiL+mowL0loRp86h/H5O2DqvHXba873COdmZviIUbjopV7ElP5xeIprEnF2MslHZuE/HWX/Tp2veXnFiuWbWzRvcT5sP6UjcxJglf9DMEZVXIBj1Bw7fsyZBc4MGDFy9AQU42XLHFIl04JriPpd5DAj3gE77HprBz+FjoGYjegj/0eh9nd90c44Tw2K9tu2b+OXNIHgIjiqZGwLXOxGmhHhhU8yeiE0Ptufl5dyqPvH+c2xbH/A5uDvt7z26kcIegUTRI1iDoh6PLGx/LK/08fzClD+UkkWCBKAQCj+TB0E6v8Ex4BFYAn4sfaFCZ9ifGLi/GZ/k5RQYu5gXAj4JUcEiI0lFAwLtWn5sGF5vxCsIJbAmLHjebXlg4tz2EYnXih+PuXBiW+wTZSMfoDfz99EYMGVWRzUAto+/MGyCvttJPkIdaxzt299rRl6cupKhM9pbXWhEfgsO1OAzcVvvPmGeD4hZgAyfyV4jjUS22zxxNQpk/ZhxNbQT42kGUUxysdRdkS5O86vmeQjLT+K1PeQhw9EzIInKUDVJbHhf8fm+kBrH1RTqBUpWToBeRfKk+vp2eRT4Q0BfU7ETV/EC/GpQiTtLdgX2z7TJ2vhtu2rk77f1IjJXqjxIfCIzb9KKlIJwIneDgnrOqF08gWih8KE0km8PvRWfkUR5HHsWzh5UmntuPETb4H9Ye2Tfp3U4NgOo8ID+2dov4tgL7ICF6X4p+uKgdAYn6Bj974jValrAMTy85dr4odsK1SCvwV3gi3Ah7BzMHUk/OM4WGHphAdqkSDnKy3sIbiGJL/0+RWTJk7o17lj5z+iMZcWA8oRRQjSED02AaP8TzyxY+cOcZEVM2DC+LFfIQHjQqPQAdwBfgFfLVhk/GbkKb504oPFqJeDp4VHHP0UzWyw/epcqq+m6D+r09WdIMa/1YycITYQ49qkWfniKDIg6sGzyeBjEEEsxYmf1sFYAZ2OesoEyuDkmh8/bkztpMlTi+FfjvZpbh9Jfawwtd+IdvwLJpaOex2BFiLijiJ0R0zWQqP0/PfgXKFkm1vhzZs3ed2691iHoK5AMAUmQHGNCAgch6XwgbEltQ9OmY6R95bDjpHXftNXMrx/nT4+6b3z808+PQsl63wvgJjFfwuqFbETxmcKseUdYN+du3cdZYPgWR1MnTaTn/OrEU9vaZFA8rgVa350yYha9CtGO3iGJ/02XIPrj/dhhCqwHbC2gg+g+Ow/hRhM34zncIpQJzSVheIH7tqzi+8pAkQSQEyfMUskQQYggeAw8l7hqJHDauEPHmAmCa9PUnB8jLZfXLGaXwC9VWAfViRUR7cA7APYRcQuxe/d7YgnYhNAzJg5W82EVG+KR7CFI0cMrZ0xc44S7zsPMKNibbjOcF8tfvWqVQyImz7cxXSzdlDViM/pYjUo3vcG7t63JyKeyJgAYuasuU2xFPDx500bPmxw7azZ85xpT7hinEZMUuL8FO8Vp59+mtGYkVddzR4RA6pWg4j6xMjv2bc3VjyRmAAbc+bOd57bN1w4SznyK8t5WL5DTOGbmnbKQsMR61QjHRV8KX7/voziiawSMG9+WVZrnkjy2z4tvvzPfAXorcL1X4x8DkKtLSArQvzeA8niiTpfby0oW4iPupQQrz+u4shcujZYVD3sA55HUbz8iSdYD13wQmKThSpYPl+K31e5P31p+0vO+ODDE4nvGxITUPbQonp/ztskoraUEP/k0qV0p3E4Z81LWCnIJJSIVpT4AxDfQXx9P++88ypPfHjir8IbAxllDBY+vDhhzROuwfVn8vkVmPoDlj32KBuY9l4f41KlgGxEfaaTqJkmINf8/oOV6Uvataf4jZCHmyj/c/Trc6DqYOwL2dgELFq8JMc1n9mn1/yfHlnMJqa9XPPcJ+gWrQhkOoeoySbE+wMPHDqY7tBWiocwPkgBxFYkobL6UCQJkQQ8suSxK1FsR8DBk58w6pcUtv212PZf8vBCtFLxNzmAqAXNuu0Cas1jhNMd2rSTI5+yb5+D/iIJBw9XOUlwEvDoY0ubINhdqPJAEcCnavGI88PG++4rFpWV8U3tKqx/Oe2Dru4+5hChY6FpLEFNiK+sOpRu36atmvZKvIbYL+j/GU7Q5VDN4d2qbb4NErhI9cU3scusb2WC+gIWtmvW4R96z913fYowpoB9RJJA8Y9liNioOquWjyLstu9/DQrx7Vq3uRz1jWAz5XOIja6fhaK8bX4Bf3Al4CQAwd5ufz0NC3N9UX+Y8PE5wlpclNrh5IN1QKQJqk6hhsqHQog/WF2VblfQ+nLYOK2b0Wf1/zu4Afwbd6FP+D2/NWx8/ygQJGDZ408i1lQX+zu9ESJpxMX7DWViwOfuuvN3OJ+PjZeH0g4wG6FxPiH+0OHqdNv81hh5bwO6qZGHEG58vxxsXlVzuCesreAbFewv+3WXqq0EQMjZYDMtSgrTIxxmdn7wLR4bJ+3Cs7pBgMlCRYmNbZfia6rTbfILLocF4iPT/h8o7q46UvMZz119pOZk9dGa6bBtoh8d2KclfUSQAAhpGhUWCHGY5Nc+Rf5YkrhAnjxroRaxt2kvwKimW7fK55rfAIM77cWxvGoI/kSe1gD+rbofWsHdoT0DPkLAfP4XEaWphWXra9KkCc9mBZe1UEm1D4kNy3tbt8wfjgrE62kfPubJlgUXt+Q7RQe0y66iH989CgQJ+NXtt/FNzF4pJsz6CbcoHq3jhMdMgMLgBh0Vauj6IMyfgVrkao+NrHseX6ZMzb/o4kBbqxYXdYGtmF7Vf7tymQQQCHiNFBOmFKTF2jS+MIVfvNrGCbeIE1tiIhQ+0VeIISN9bFr9NZUBHm8I2jshfCa4Eu1NCKOp8GEqgC8wLsK5EVqxMs33AvzoOlNa5AmSUIefN0EFpWPHtESvKtTlgxSxi9kvqIXshDG5dkKao3Yiwbem9p23gztRZwbcOuCW9zGai+zR1iMcZpb+VmBR9dEjRxHMAiYrjthEbJrYQIxrc30s4n0ZMEuVAk4CCAQ8Hnw3ThSphMX6yBj/nFXp1d9GUCUIar0IMEYQNo0tNA4c/a2qLhD5MkSsfraCr8DWUYu01H0eEUxmVIDFJcOGMuF87MsHrbRHIKz1E5Ut+PujS5GA4J0AEZkBxM039X0Bo7jMvqiFRzhMM+KsS1r+vmD5tNlzeAG6GVxPiUxCmNjIIBofk8PiidgEEBAzCEFXhoUboS61PyFp/cHymfPmiyRA6Hp1qv8GXgdnyKqL2CWgsWbt+nwU/Mx0v2IqiBFLQAY/l8BtQwfdFywHGk8hPgB/gtHXd6UOEhNArF33wjUo+NO54J16jsIDwP8Mjjdw8L1/ONVJ4C1xN4gX30nikHEJaNx4Q9F2rOdemMX80ZSYzmbqm/Vur3njd2n5uRweR2D8SezN4KlYDvxLkuIk8USdCSB6F/XajjXdFUGrj0ctWgtz17ydFNISLoj61yA/GbxTlAT+jVIPHPsl2cyMOpeAjRdfeuV8BM6Hpd2kxUVdUx892Ec8xirqdb3z0qJl8xbqhWyDlwN/CXoTxEeu+HGoVwKIl1/ZyFkzBJyIZIg/SMj2mqDF97q+Z+wbmwYmgT/tKwNLID7j3weEUe8EaGzYuLkAxSLwWmEIIZwULf66nt0TX1flmAQ+5BwE4fy4qxdyTgCxcRP/MCnF9YvbZ+8S2qKTgdNe/Pb31z26X+vchmaCSgLfmw0Qhsw4BPJP5sohPqc/uWlQAjQ2bX6Vx/kZktAPYq9G/VyQqTiCAvf/3lPduxVmPS0JJIFFT/AekMf8AciPNa7tbSBnyVYIT15//ytAQlKkan6DxoHn/QdmVLZzVZokoAAAAABJRU5ErkJggg=='
UDEMY_ICON = b'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'
BLANK_BASE64 = b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAANSURBVBhXY2BgYGAAAAAFAAGKM+MAAAAAAElFTkSuQmCC'
BLANK_BASE64 = b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='
DEFAULT_ELEMENT_SIZE = (45,)
DEFAULT_BUTTON_ELEMENT_SIZE = (1,)
DEFAULT_MARGINS = (10,)
DEFAULT_ELEMENT_PADDING = (5,)
DEFAULT_FONT = ('Helvetica',)
DEFAULT_TEXT_JUSTIFICATION = 'left'
DEFAULT_DEBUG_WINDOW_SIZE = (80,)
DEFAULT_WINDOW_LOCATION = (None,)
MAX_SCROLLED_TEXT_BOX_HEIGHT = 50
DEFAULT_TOOLTIP_TIME = 400
DEFAULT_TOOLTIP_OFFSET = (0,)
DEFAULT_ALPHA_CHANNEL = 1.0
TOOLTIP_BACKGROUND_COLOR = '#ffffe0'
BLUES = ('#082567',)
PURPLES = ('#480656',)
GREENS = ('#40A860',)
YELLOWS = ('#F3FB62',)
TANS = ('#FFF9D5',)
NICE_BUTTON_COLORS = ((GREENS[3],), ('#000000', '#FFFFFF'), ('#FFFFFF', '#000000'), (PURPLES[1],), (BLUES[2],))
COLOR_SYSTEM_DEFAULT = '1234567890'
DEFAULT_BUTTON_COLOR = ('white',)
OFFICIAL_PYSIMPLEGUI_THEME = CURRENT_LOOK_AND_FEEL = 'Dark Blue 3'
DEFAULT_ERROR_BUTTON_COLOR = ('#FF0000',)
RELIEF_RAISED = 'raised'
RELIEF_SUNKEN = 'sunken'
RELIEF_FLAT = 'flat'
RELIEF_RIDGE = 'ridge'
RELIEF_GROOVE = 'groove'
RELIEF_SOLID = 'solid'
THEME_DEFAULT = 'default'
THEME_WINNATIVE = 'winnative'
THEME_CLAM = 'clam'
THEME_ALT = 'alt'
THEME_CLASSIC = 'classic'
THEME_VISTA = 'vista'
THEME_XPNATIVE = 'xpnative'
DEFAULT_PROGRESS_BAR_COLOR = ('#01826B',)
DEFAULT_PROGRESS_BAR_COMPUTE = ('#000000',)
DEFAULT_PROGRESS_BAR_SIZE = (20,)
DEFAULT_METER_ORIENTATION = 'Horizontal'
DEFAULT_SLIDER_ORIENTATION = 'vertical'
LISTBOX_SELECT_MODE_MULTIPLE = 'multiple'
LISTBOX_SELECT_MODE_BROWSE = 'browse'
LISTBOX_SELECT_MODE_EXTENDED = 'extended'
LISTBOX_SELECT_MODE_SINGLE = 'single'
TABLE_CLICKED_INDICATOR = '+CLICKED+'
TAB_LOCATION_TOP = 'top'
TAB_LOCATION_TOP_LEFT = 'topleft'
TAB_LOCATION_TOP_RIGHT = 'topright'
TAB_LOCATION_LEFT_TOP = 'lefttop'
TAB_LOCATION_LEFT_BOTTOM = 'leftbottom'
TAB_LOCATION_RIGHT = 'right'
TAB_LOCATION_RIGHT_TOP = 'righttop'
TAB_LOCATION_RIGHT_BOTTOM = 'rightbottom'
TAB_LOCATION_BOTTOM = 'bottom'
TAB_LOCATION_BOTTOM_LEFT = 'bottomleft'
TAB_LOCATION_BOTTOM_RIGHT = 'bottomright'
ThisRow = 555666777
MESSAGE_BOX_LINE_WIDTH = 60
EVENT_TIMEOUT = TIMEOUT_EVENT = TIMEOUT_KEY = '__TIMEOUT__'
WINDOW_CLOSE_ATTEMPTED_EVENT = WIN_X_EVENT = WIN_CLOSE_ATTEMPTED_EVENT = '-WINDOW CLOSE ATTEMPTED-'
WINDOW_CONFIG_EVENT = '__WINDOW CONFIG__'
TITLEBAR_MINIMIZE_KEY = '__TITLEBAR MINIMIZE__'
TITLEBAR_MAXIMIZE_KEY = '__TITLEBAR MAXIMIZE__'
TITLEBAR_CLOSE_KEY = '__TITLEBAR CLOSE__'
TITLEBAR_IMAGE_KEY = '__TITLEBAR IMAGE__'
TITLEBAR_DO_NOT_USE_AN_ICON = '__TITLEBAR_NO_ICON__'
WRITE_ONLY_KEY = '__WRITE ONLY__'
MENU_DISABLED_CHARACTER = '!'
MENU_SHORTCUT_CHARACTER = '&'
MENU_KEY_SEPARATOR = '::'
MENU_SEPARATOR_LINE = '---'
MENU_RIGHT_CLICK_EDITME_VER_LOC_EXIT = [['Edit Me', 'Version', 'File Location', 'Exit']]
MENU_RIGHT_CLICK_EDITME_VER_SETTINGS_EXIT = [['Settings']]
_MENU_RIGHT_CLICK_TABGROUP_DEFAULT = ['TABGROUP DEFAULT']
TITLEBAR_METADATA_MARKER = 'This window has a titlebar'
CUSTOM_MENUBAR_METADATA_MARKER = 'This is a custom menubar'
OLD_TABLE_TREE_SELECTED_ROW_COLORS = ('#FFFFFF',)
ALTERNATE_TABLE_AND_TREE_SELECTED_ROW_COLORS = ('SystemHighlightText',)
SYMBOL_SQUARE = '█'
SYMBOL_CIRCLE = '⚫'
SYMBOL_CIRCLE_OUTLINE = '◯'
SYMBOL_UP = '▲'
SYMBOL_RIGHT = '►'
SYMBOL_LEFT = '◄'
SYMBOL_DOWN = '▼'
SYMBOL_X = '❎'
SYMBOL_CHECK = '✅'
SYMBOL_CHECK_SMALL = '✓'
SYMBOL_X_SMALL = '✗'
SYMBOL_BALLOT_X = '☒'
SYMBOL_BALLOT_CHECK = '☑'
SYMBOL_LEFT_DOUBLE = '«'
SYMBOL_RIGHT_DOUBLE = '»'
SYMBOL_LEFT_ARROWHEAD = '⮜'
SYMBOL_RIGHT_ARROWHEAD = '⮞'
SYMBOL_UP_ARROWHEAD = '⮝'
SYMBOL_DOWN_ARROWHEAD = '⮟'
if (sum([int for i in '.']) > 19):
    SYMBOL_TITLEBAR_MAXIMIZE = '◻'
    SYMBOL_TITLEBAR_CLOSE = 'Ｘ'
else:
    SYMBOL_TITLEBAR_MINIMIZE = '_'
    SYMBOL_TITLEBAR_MAXIMIZE = 'O'
    SYMBOL_TITLEBAR_CLOSE = 'X'
DEFAULT_USER_SETTINGS_WIN_PATH = '~\\AppData\\Local\\PySimpleGUI\\settings'
DEFAULT_USER_SETTINGS_LINUX_PATH = '~/.config/PySimpleGUI/settings'
DEFAULT_USER_SETTINGS_MAC_PATH = '~/Library/Application Support/PySimpleGUI/settings'
DEFAULT_USER_SETTINGS_PYSIMPLEGUI_FILENAME = '_PySimpleGUI_settings_global_.json'

def rgb():
    pass
BUTTON_TYPE_BROWSE_FILES = 21
BUTTON_TYPE_CLOSES_WIN = 5
BUTTON_TYPE_CLOSES_WIN_ONLY = 6
BUTTON_TYPE_READ_FORM = 7
BUTTON_TYPE_REALTIME = 9
BUTTON_TYPE_CALENDAR_CHOOSER = 30
BUTTON_TYPE_COLOR_CHOOSER = 40
BROWSE_FILES_DELIMITER = ';'
FILE_TYPES_ALL_FILES = ()
BUTTON_DISABLED_MEANS_IGNORE = 'ignore'
ELEM_TYPE_TEXT = 'text'
ELEM_TYPE_INPUT_TEXT = 'input'
ELEM_TYPE_INPUT_COMBO = 'combo'
ELEM_TYPE_INPUT_OPTION_MENU = 'option menu'
ELEM_TYPE_INPUT_RADIO = 'radio'
ELEM_TYPE_INPUT_MULTILINE = 'multiline'
ELEM_TYPE_INPUT_CHECKBOX = 'checkbox'
ELEM_TYPE_INPUT_SPIN = 'spind'
ELEM_TYPE_BUTTON = 'button'
ELEM_TYPE_IMAGE = 'image'
ELEM_TYPE_CANVAS = 'canvas'
ELEM_TYPE_FRAME = 'frame'
ELEM_TYPE_GRAPH = 'graph'
ELEM_TYPE_TAB = 'tab'
ELEM_TYPE_TAB_GROUP = 'tabgroup'
ELEM_TYPE_INPUT_SLIDER = 'slider'
ELEM_TYPE_INPUT_LISTBOX = 'listbox'
ELEM_TYPE_OUTPUT = 'output'
ELEM_TYPE_COLUMN = 'column'
ELEM_TYPE_MENUBAR = 'menubar'
ELEM_TYPE_PROGRESS_BAR = 'progressbar'
ELEM_TYPE_BLANK = 'blank'
ELEM_TYPE_TABLE = 'table'
ELEM_TYPE_TREE = 'tree'
ELEM_TYPE_ERROR = 'error'
ELEM_TYPE_SEPARATOR = 'separator'
ELEM_TYPE_STATUSBAR = 'statusbar'
ELEM_TYPE_PANE = 'pane'
ELEM_TYPE_BUTTONMENU = 'buttonmenu'
ELEM_TYPE_TITLEBAR = 'titlebar'
ELEM_TYPE_SIZEGRIP = 'sizegrip'
POPUP_BUTTONS_OK_CANCEL = 4
PSG_THEME_PART_BUTTON_TEXT = 'Button Text Color'
PSG_THEME_PART_BUTTON_BACKGROUND = 'Button Background Color'
PSG_THEME_PART_BACKGROUND = 'Background Color'
PSG_THEME_PART_INPUT_BACKGROUND = 'Input Element Background Color'
PSG_THEME_PART_INPUT_TEXT = 'Input Element Text Color'
PSG_THEME_PART_TEXT = 'Text Color'
PSG_THEME_PART_SLIDER = 'Slider Color'
TTK_SCROLLBAR_PART_TROUGH_COLOR = 'Trough Color'
TTK_SCROLLBAR_PART_ARROW_BUTTON_ARROW_COLOR = 'Arrow Button Arrow Color'
TTK_SCROLLBAR_PART_FRAME_COLOR = 'Frame Color'
TTK_SCROLLBAR_PART_SCROLL_WIDTH = 'Frame Width'
TTK_SCROLLBAR_PART_ARROW_WIDTH = 'Arrow Width'
TTK_SCROLLBAR_PART_RELIEF = 'Relief'
DEFAULT_TTK_PART_MAPPING_DICT = {TTK_SCROLLBAR_PART_TROUGH_COLOR: PSG_THEME_PART_SLIDER, TTK_SCROLLBAR_PART_BACKGROUND_COLOR: PSG_THEME_PART_BUTTON_BACKGROUND, TTK_SCROLLBAR_PART_ARROW_BUTTON_ARROW_COLOR: PSG_THEME_PART_BUTTON_TEXT, TTK_SCROLLBAR_PART_FRAME_COLOR: PSG_THEME_PART_BACKGROUND, TTK_SCROLLBAR_PART_SCROLL_WIDTH: 12, TTK_SCROLLBAR_PART_ARROW_WIDTH: 12, TTK_SCROLLBAR_PART_RELIEF: RELIEF_RAISED}

def __init__():
    pass
TKINTER_CURSORS = ['X_cursor', 'arrow', 'based_arrow_down', 'based_arrow_up', 'boat', 'bogosity', 'bottom_left_corner', 'bottom_right_corner', 'bottom_side', 'bottom_tee', 'box_spiral', 'center_ptr', 'circle', 'clock', 'coffee_mug', 'cross', 'cross_reverse', 'crosshair', 'diamond_cross', 'dot', 'dotbox', 'double_arrow', 'draft_large', 'draft_small', 'draped_box', 'exchange', 'fleur', 'gobbler', 'gumby', 'hand1', 'hand2', 'heart', 'icon', 'iron_cross', 'left_ptr', 'left_side', 'left_tee', 'leftbutton', 'll_angle', 'lr_angle', 'man', 'middlebutton', 'mouse', 'pencil', 'pirate', 'plus', 'question_arrow', 'right_ptr', 'right_side', 'right_tee', 'rightbutton', 'rtl_logo', 'sailboat', 'sb_down_arrow', 'sb_h_double_arrow', 'sb_left_arrow', 'sb_right_arrow', 'sb_up_arrow', 'sb_v_double_arrow', 'shuttle', 'sizing', 'spider', 'spraycan', 'star', 'target', 'tcross', 'top_left_arrow', 'top_left_corner', 'top_right_corner', 'top_side', 'top_tee', 'trek', 'ul_angle', 'umbrella', 'ur_angle', 'watch', 'xterm']

def popup_get_date(start_mon=None, start_day=None, start_year=None, begin_at_sunday_plus=0, no_titlebar=True, title='Choose Date'):
    pass
