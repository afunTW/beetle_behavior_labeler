# import tkinter as tk
# from tkinter import ttk
from src.interface import Interface

class KeyHandler(object):

    def tvitem_click(self, event, item=None):
        sel_items = self.tv.selection() if item is None else item
        if sel_items:
            popup = Interface.popupEntry(self.parent, title="更改 object 名稱", string="請輸入新的名稱。")
            self.parent.wait_window(popup.top)
            sel_item = sel_items[0]

            print(popup.value)