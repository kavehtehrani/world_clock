"""
Wrote this since Win10 only allows two native clocks and the world clock app is too massive

Kaveh Tehrani
"""

import datetime
import pytz
import tkinter as tk
import yaml
from tkinter import ttk
from ttkthemes import ThemedTk
from ttk_extensions import AutocompleteEntry, DropDown, matches
import platform
import os


class WorldClock:
    def __init__(self, master, l_tz=None, num_max_clocks=20):
        self.master = master
        self.master.title('Clock')

        # load last preset, otherwise load defaults
        self.load_config()
        if not self.wc_config:
            if not l_tz:
                self.l_tz = ['US/Eastern', 'Europe/London', 'Asia/Tehran']
                self.b_show_seconds = tk.BooleanVar(value=True)

        self.num_max_clocks = num_max_clocks
        self.num_clocks = len(self.l_tz)

        self.frame = ttk.Frame()
        self.frame.pack()
        self.create_clocks()

    def create_clocks(self):
        """
        Create the GUI
        """
        self.l_entries = []
        self.l_dd = []
        for i in range(self.num_clocks):
            self.l_dd.append(AutocompleteEntry(pytz.all_timezones, self.frame, listboxLength=4, width=20, matchesFunction=matches))
            self.l_dd[i].var.set(pytz.all_timezones[0])
            if i < len(self.l_tz):
                self.l_dd[i].delete(0, tk.END)
                self.l_dd[i].insert(0, self.l_tz[i])
            self.l_dd[i].listbox.destroy()

            self.l_dd[i].grid(row=i, column=0, columnspan=2)

            self.l_entries.append(ttk.Entry(self.frame))
            self.l_entries[i].grid(row=i, column=2, columnspan=1)
            self.l_entries[i].bind("<Key>", lambda e: "break")

        self.bt_update = ttk.Button(self.frame, text="Update", command=self.redesign_clocks)
        self.bt_update.grid(row=i + 1, column=0, columnspan=1)
        self.dd_num_clocks = DropDown(self.frame, range(1, self.num_max_clocks + 1), self.num_clocks)
        self.dd_num_clocks.grid(row=i + 1, column=1, columnspan=1)

        self.ck_seconds = ttk.Checkbutton(self.frame, text="Show Seconds", variable=self.b_show_seconds)
        self.ck_seconds.grid(row=i + 1, column=2, columnspan=1)

    def redesign_clocks(self):
        """
        Have to create a new GUI since the number of clocks changed
        """
        for w in self.frame.winfo_children():
            w.destroy()

        self.num_clocks = int(app.dd_num_clocks.get())
        self.create_clocks()

    def load_config(self):
        """
        Load previous known state if exists
        """
        try:
            self.wc_config = yaml.safe_load(open(r'world_clock.yaml'))
            self.l_tz = self.wc_config['l_tz']
            self.b_show_seconds = tk.BooleanVar(value=self.wc_config['b_seconds'])
        except FileNotFoundError:
            self.wc_config = {}

    def save_config(self):
        """
        Save current state
        """
        wc_config = {'l_tz': self.l_tz, 'b_seconds': self.b_show_seconds.get()}

        with open(r'world_clock.yaml', 'w') as config_file:
            yaml.dump(wc_config, config_file)


def change_text(app):
    """
    Takes our GUI and updates it for the time zones
    """
    b_seconds = app.b_show_seconds.get()
    app.l_tz = [x.var.get() for x in app.l_dd]
    for i, str_tz in enumerate(app.l_tz):
        try:
            cur_zone = pytz.timezone(str_tz)
            cur_time = datetime.datetime.now(cur_zone).strftime(f"%I:%M{':%S' if b_seconds else ''} %p")
            app.l_entries[i].delete(0, tk.END)
            app.l_entries[i].insert(0, cur_time)
        except pytz.UnknownTimeZoneError:
            pass

    app.save_config()

    # update clocks every second if showing seconds, every 10 seconds otherwise to reduce cpu load
    root.after(1000 if b_seconds else 10000, change_text, app)


if __name__ == '__main__':
    root = ThemedTk(themebg=True)
    app = WorldClock(master=root)
    root.set_theme('equilux')
    if platform.system() == "Windows":
        root.iconbitmap(r'clock_mini_icon.ico')
    else:
        iconPath = os.path.realpath('clock_mini_icon.png')
        img = tk.Image("photo", file=iconPath)
        root.tk.call('wm', 'iconphoto', root._w, img)

    change_text(app)
    root.mainloop()
