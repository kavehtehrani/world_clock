import tkinter as tk
from tkinter import ttk
import re


class DropDown(ttk.OptionMenu):
    """
    Small class to embed the variable within
    """
    def __init__(self, parent, options, initial_value=None):
        self.var = tk.StringVar(parent)

        self.option_menu = ttk.OptionMenu.__init__(self, parent, self.var, *options)

        self.var.set(initial_value if initial_value else options[0])
        self.callback = None

    def get(self):
        return self.var.get()

    def set(self, value: str):
        self.var.set(value)

    def add_callback(self, callback: callable):
        def internal_callback(*args):
            callback()

        self.var.trace("w", internal_callback)


class AutocompleteEntry(ttk.Entry):
    """
    Entry box with autocomplete features (mostly pieced on github)
    """
    def __init__(self, autocomplete_list, *args, **kwargs):
        # Listbox length
        if 'listboxLength' in kwargs:
            self.list_box_length = kwargs['listboxLength']
            del kwargs['listboxLength']
        else:
            self.list_box_length = 8

        # Custom matches function
        if 'matchesFunction' in kwargs:
            self.matchesFunction = kwargs['matchesFunction']
            del kwargs['matchesFunction']
        else:
            def matches(fieldValue, acListEntry):
                pattern = re.compile('.*' + re.escape(fieldValue) + '.*', re.IGNORECASE)
                return re.match(pattern, acListEntry)

            self.matchesFunction = matches

        ttk.Entry.__init__(self, *args, **kwargs)
        self.focus()

        self.autocomplete_list = autocomplete_list

        self.var = self["textvariable"]
        if self.var == '':
            self.var = self["textvariable"] = tk.StringVar()

        self.var.trace('w', self.changed)
        self.bind("<Right>", self.selection)
        self.bind("<Up>", self.move_up)
        self.bind("<Down>", self.move_down)

        self.b_listbox_up = False

    def changed(self, name, index, mode):
        if self.var.get() == '':
            if self.b_listbox_up:
                self.listbox.destroy()
                self.b_listbox_up = False
        else:
            words = self.comparison()
            if words:
                if not self.b_listbox_up:
                    self.listbox = tk.Listbox(width=self["width"], height=self.list_box_length)
                    self.listbox.bind("<Button-1>", self.selection)
                    self.listbox.bind("<Right>", self.selection)
                    self.listbox.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
                    self.b_listbox_up = True

                self.listbox.delete(0, tk.END)
                for w in words:
                    self.listbox.insert(tk.END, w)
            else:
                if self.b_listbox_up:
                    self.listbox.destroy()
                    self.b_listbox_up = False

    def selection(self, event):
        if self.b_listbox_up:
            self.var.set(self.listbox.get(tk.ACTIVE))
            self.listbox.destroy()
            self.b_listbox_up = False
            self.icursor(tk.END)

    def move_up(self, event):
        if self.b_listbox_up:
            if self.listbox.curselection() == ():
                index = '0'
            else:
                index = self.listbox.curselection()[0]

            if index != '0':
                self.listbox.selection_clear(first=index)
                index = str(int(index) - 1)

                self.listbox.see(index)  # Scroll!
                self.listbox.selection_set(first=index)
                self.listbox.activate(index)

    def move_down(self, event):
        if self.b_listbox_up:
            if self.listbox.curselection() == ():
                index = '0'
            else:
                index = self.listbox.curselection()[0]

            if index != tk.END:
                self.listbox.selection_clear(first=index)
                index = str(int(index) + 1)

                self.listbox.see(index)  # Scroll!
                self.listbox.selection_set(first=index)
                self.listbox.activate(index)

    def comparison(self):
        return [w for w in self.autocomplete_list if self.matchesFunction(self.var.get(), w)]


def matches(field_value, ac_list_entry):
    """
    Func for the autocomplete dropdown boxes
    """
    pattern = re.compile(re.escape(field_value) + '.*', re.IGNORECASE)
    return re.search(pattern, ac_list_entry)
