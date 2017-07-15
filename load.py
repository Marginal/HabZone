#
# System display and EDSM lookup
#

import sys

import Tkinter as tk
import myNotebook as nb

if __debug__:
    from traceback import print_exc

from config import config

VERSION = '1.00'

WORLDS = [
    # Type     Black-body temp range
    ('Metal-Rich',   0,  1103.0),
    ('Earth-Like', 278.0, 227.0),
    ('Water',      307.0, 156.0),
    ('Ammonia',    193.0, 117.0),
]

LS = 300000000.0	# 1 ls in m (approx)

this = sys.modules[__name__]	# For holding module globals


def plugin_start():
    return 'HabZone'

def plugin_app(parent):
    frame = tk.Frame(parent)
    frame.columnconfigure(3, weight=1)
    this.worlds = []
    for (name, high, low) in WORLDS:
        this.worlds.append((tk.Label(frame, text = name + ':'),
                            tk.Label(frame),
                            tk.Label(frame),
                            tk.Label(frame),
                            tk.Label(frame),
                            ))
    update_visibility()
    return frame

def plugin_prefs(parent):
    frame = nb.Frame(parent)
    nb.Label(frame, text = 'Display:').grid(row = 0, padx = 10, pady = (10,0), sticky=tk.W)

    setting = config.getint('habzone') or 2
    this.settings = []
    row = 1
    for (name, high, low) in WORLDS:
        var = tk.IntVar(value = (setting & row) and 1)
        nb.Checkbutton(frame, text = name, variable = var).grid(row = row, padx = 10, pady = 2, sticky=tk.W)
        this.settings.append(var)
        row *= 2

    nb.Label(frame, text = 'Version %s' % VERSION).grid(padx = 10, pady = 10, sticky=tk.W)

    return frame

def prefs_changed():
    row = 1
    setting = 0
    for var in this.settings:
        setting += var.get() * row
        row *= 2

    config.set('habzone', setting)
    this.settings = None
    update_visibility()


def journal_entry(cmdr, system, station, entry, state):

    if entry['event'] == 'Scan':
        try:
            if not float(entry['DistanceFromArrivalLS']):	# Only calculate for arrival star
                r = float(entry['Radius'])
                t = float(entry['SurfaceTemperature'])
                for i in range(len(WORLDS)):
                    (name, high, low) = WORLDS[i]
                    (label, near, dash, far, ls) = this.worlds[i]
                    if not high:
                        near['text'] = str(int(0.5 + r / LS))
                    else:
                        near['text'] = str(int(0.5 + dfort(r, t, high)))
                    dash['text'] = '-'
                    far['text'] = str(int(0.5 + dfort(r, t, low)))
                    ls['text'] = 'ls'
        except:
            for (label, near, dash, far, ls) in this.worlds:
                near['text'] = ''
                dash['text'] = ''
                far['text'] = ''
                ls['text'] = '?'

    elif entry['event'] == 'FSDJump':
        for (label, near, dash, far, ls) in this.worlds:
            near['text'] = ''
            dash['text'] = ''
            far['text'] = ''
            ls['text'] = ''


# Distance for target black-body temperature
def dfort(r, t, target):
    return (((r ** 2) * (t ** 4) / (4 * (target ** 4))) ** 0.5) / LS


def update_visibility():
    setting = config.getint('habzone') or 2
    row = 1
    for (label, near, dash, far, ls) in this.worlds:
        if setting & row:
            label.grid(row = row, column = 0, sticky=tk.W)
            near.grid(row = row, column = 1, sticky=tk.E)
            dash.grid(row = row, column = 2, sticky=tk.E)
            far.grid(row = row, column = 3, sticky=tk.E)
            ls.grid(row = row, column = 4, sticky=tk.W)
        else:
            label.grid_remove()
            near.grid_remove()
            dash.grid_remove()
            far.grid_remove()
            ls.grid_remove()
        row *= 2
