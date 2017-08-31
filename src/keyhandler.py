# import tkinter as tk
# from tkinter import ttk
from src.interface import Interface

class KeyHandler(object):

    def tvitem_click(self, event, item=None):
        if self.video_path is not None:
            sel_items = self.tv.selection() if item is None else item
            if sel_items:
                popup = Interface.popupEdit(self.parent, title="更改", name=sorted(self.__trajectory__.keys()), ind=(self.stop_ind, self.total_frame))
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

    # move to previous frame
    def on_left(self, event):
        if self.stop_ind > 1:
            self.stop_ind -= 1
            self.var_n_frame.set(self.stop_ind)
        else:
            self.msg('Already the first frame!')
    
    # move to next frame
    def on_right(self, event):
        if self.stop_ind == self.total_frame:
            self.msg('Already the last frame!')
        else:
            self.stop_ind += 1
            self.var_n_frame.set(self.stop_ind)
