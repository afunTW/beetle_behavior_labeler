# import tkinter as tk
# from tkinter import ttk
from src.interface import Interface

class KeyHandler(object):

    def tvitem_click(self, event, item=None):
        sel_items = self.tv.selection() if item is None else item
        if sel_items:
            popup = Interface.popupEntry(self.parent, title="更改", string="Please enter new entry")
            self.parent.wait_window(popup.top)
            sel_item = sel_items[0]
            try:
                print(popup.value)
            except:
                pass

    def set_n_frame(self, s):
        v = int(float(s))
        self.var_n_frame.set(v)
        self.stop_ind = v