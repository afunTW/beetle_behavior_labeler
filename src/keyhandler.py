# import tkinter as tk
# from tkinter import ttk
from src.interface import Interface

class KeyHandler(object):

    def tvitem_click(self, event, item=None):
        if self.video_path is not None:
            sel_items = self.tv.selection() if item is None else item
            if sel_items:
                popup = Interface.popupEdit(self.parent, title="更改", name=sorted(self.__trajectory__.keys()), ind=(self.stop_ind, self.total_frame), tv=self.tv)
                self.parent.wait_window(popup.top)
                sel_item = sel_items[0]
                try:
                    print(popup.value)
                except:
                    pass

    def set_n_frame(self, s):
        v = int(float(s))
        self.n_frame = v

    # move to previous frame
    def on_left(self, event=None):
        if self.video_path is not None:
            if self.n_frame > 1:
                self.n_frame -= 1
            else:
                self.msg('Already the first frame!')
    
    # move to next frame
    def on_right(self, event=None):
        if self.video_path is not None:
            if self.n_frame == self.total_frame:
                self.msg('Already the last frame!')
            else:
                self.n_frame += 1

    # return to label frame index
    def on_return(self, event=None):
        self.n_frame = self.stop_ind

    # add behavior record
    def on_add(self, event=None):
        popup = Interface.popupEdit(self.parent, title="新增", name=sorted(self.__trajectory__.keys()), ind=(self.stop_ind, self.total_frame), tv=self.tv)
        
        print('add!')

    # delete behavior record
    def on_delete(self, event=None):
        for v in self.tv.selection():
            self.tv.delete(v)

    # move to next stop frame index
    def on_next(self, event=None):
        self.get_stop_ind(direct='next')
    
    # move to previous stop frame index
    def on_prev(self, event=None):
        self.get_stop_ind(direct='prev')

    def get_stop_ind(self, direct='next'):
        if direct == 'next' and (self.stop_ind + 20) <= self.total_frame:
            self.stop_ind  += 20
        elif direct == 'prev' and (self.stop_ind - 20) >= 1:
            self.stop_ind -= 20
        self.n_frame = self.stop_ind
        pass
