import tkinter as tk
from tkinter import ttk

import Controller


class GUI:

    def populate_effects_list(self):
        for i in self.tree_view.get_children():
            self.tree_view.delete(i)
        selected_ingredients = set()
        for checkbox in self.checkbox_dict:
            if self.checkbox_dict[checkbox].get() == 1:
                selected_ingredients.add(checkbox)
        possible_effects = Controller.get_possible_effects_combinations(selected_ingredients)
        for i in sorted(possible_effects.keys()):
            self.tree_view.insert("", 'end', i, text=i)
            for pair in possible_effects[i]:
                self.tree_view.insert(i, 'end', text=pair[0] + " + " + pair[1])

    def filter_check_box(self, *args):
        c = 0
        r = 0
        for widget in self.checkbox_frame.winfo_children():
            if self.ingredients_entry_value.get().lower() in widget.cget("text").lower():
                widget.grid(column=c, row=r, sticky=tk.W)
                r = r + 1
                if r == 32:
                    c = c + 1
                    r = 0
            else:
                widget.grid_forget()

    def __init__(self, data_source):
        self.data_source = data_source
        self.window = tk.Tk()
        self.window.title("Alchemia w Skyrim")
        #self.window.iconbitmap(default="empty_logo.ico")
        self.window.resizable(True, False)

        self.entry_checkbox_frame = tk.Frame(master=self.window)
        self.entry_checkbox_frame.pack(side=tk.LEFT)

        self.ingredients_entry_value = tk.StringVar()
        self.ingredients_entry = tk.Entry(master=self.entry_checkbox_frame, textvariable=self.ingredients_entry_value)
        self.ingredients_entry.pack(fill=tk.BOTH, padx=3, pady=3)
        self.ingredients_entry_value.trace("w", self.filter_check_box)
        self.ingredients_entry.grid_propagate(0)

        self.checkbox_frame = tk.Frame(master=self.entry_checkbox_frame)
        self.checkbox_frame.pack(fill=tk.X)

        self.checkbox_dict = dict()
        c = 0
        r = 0
        for ingredient in sorted(list(self.data_source.ingredients_set)):
            self.checkbox_dict[ingredient] = tk.IntVar()
            tk.Checkbutton(self.checkbox_frame, text=ingredient, variable=self.checkbox_dict[ingredient],
                           command=self.populate_effects_list).grid(column=c, row=r, sticky=tk.W)
            r = r+1
            if r == 32:
                c = c+1
                r = 0
        self.checkbox_frame.update_idletasks()
        self.checkbox_frame.pack_propagate(0)
        self.entry_checkbox_frame.pack_propagate(0)
        self.tree_view_frame = tk.Frame(master=self.window)
        self.tree_view_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.TRUE)

        self.tree_view = ttk.Treeview(self.tree_view_frame)
        self.tree_view.pack(fill=tk.BOTH, expand=tk.TRUE, padx=3, pady=3)
        self.window.mainloop()
