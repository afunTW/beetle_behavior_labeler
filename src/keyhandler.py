# import tkinter as tk
# from tkinter import ttk
import pandas as pd
from tkinter.filedialog import asksaveasfilename

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
                    self.tv.item(sel_item, values=popup.value)
                    # print(popup.value)
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

    # logic to get stop frame index
    def get_stop_ind(self, direct='next'):
        for i, (k, v) in enumerate(self.__trajectory__.items()):
            nframe = v['n_frame']
            traj = v['path']
            wh = v['wh']

        if direct == 'next' and (self.stop_ind + 20) <= self.total_frame:
            self.stop_ind  += 20
        elif direct == 'prev' and (self.stop_ind - 20) >= 1:
            self.stop_ind -= 20

        self.n_frame = self.stop_ind
        # popup label box
        self.on_add()

    def on_save(self, event=None):
        {'frame_index': [], 'name': [], 'behavior': []}
        values = [self.tv.item(child)['values'] for child in self.tv.get_children()]
        self.__results_dict__['frame_index'] = list(map(lambda x: x[0], values))
        self.__results_dict__['name'] = list(map(lambda x: x[1], values))
        self.__results_dict__['behavior'] = list(map(lambda x: x[2], values))

        df = pd.DataFrame(self.__results_dict__)
        df = df.reindex_axis(['frame_index', 'name', 'behavior'], axis=1)
        root = '/'.join(self.video_path.split('/')[:-1])
        filename = self.video_path.split('/')[-1].split('.avi')[0] + '_behavior_record'
        filename = asksaveasfilename(initialdir='%s' % (root), 
                                     defaultextension=".csv", 
                                     filetypes=(("CSV (逗號分隔)", "*.csv"),("All Files", "*.*")), 
                                     initialfile=filename, 
                                     title='存檔')
        df.to_csv(filename, index=False)


