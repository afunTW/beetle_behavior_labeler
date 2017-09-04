# import tkinter as tk
# from tkinter import ttk
import pandas as pd
import numpy as np
from tkinter.filedialog import asksaveasfilename
from itertools import combinations
from src.interface import Interface

class KeyHandler(object):

    def tvitem_click(self, event, item=None):
        if self.video_path is not None:
            sel_items = self.tv.selection() if item is None else item
            if sel_items:
                popup = Interface.popupEdit(self.parent, title="更改", name=sorted(self.__trajectory__.keys()), ind=(self.stop_ind, self.total_frame, None), tv=self.tv)
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
    def on_add(self, event=None, sug_name=None):
        if sug_name is not None:
            if self.k1 is not None:
                popup = Interface.popupEdit(self.parent, title="新增", name=sorted(self.__trajectory__.keys()), ind=(self.n_frame, self.total_frame, self.k1), tv=self.tv)
                self.parent.wait_window(popup.top)
                # self.k1 = None
                if self.k2 is not None:
                    popup = Interface.popupEdit(self.parent, title="新增", name=sorted(self.__trajectory__.keys()), ind=(self.n_frame, self.total_frame, self.k2), tv=self.tv)
                    self.parent.wait_window(popup.top)
                    # self.k2 = None
        else:
            popup = Interface.popupEdit(self.parent, title="新增", name=sorted(self.__trajectory__.keys()), ind=(self.n_frame, self.total_frame, None), tv=self.tv)
            self.parent.wait_window(popup.top)

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
        pair = combinations(sorted(self.__trajectory__.keys()), 2)
        for k1, k2 in pair:
            v1 = self.__trajectory__[k1]
            v2 = self.__trajectory__[k2]

            try:
                if direct == 'next':
                    ind_1 = min([v1['n_frame'].index(f) for f in v1['n_frame'] if f >= self.n_frame])
                    ind_2 = min([v2['n_frame'].index(f) for f in v2['n_frame'] if f >= self.n_frame])
                    center_1 = v1['path'][ind_1:]
                    center_2 = v2['path'][ind_2:]
                elif direct == 'prev':
                    ind_1 = max([v1['n_frame'].index(f) for f in v1['n_frame'] if f < self.n_frame])
                    ind_2 = max([v2['n_frame'].index(f) for f in v2['n_frame'] if f < self.n_frame])
                    center_1 = v1['path'][:(ind_1)]
                    center_2 = v2['path'][:(ind_2)]
                print('Index: ', ind_1, ind_2, len(v1['n_frame']), len(v2['n_frame']))
            except:
                ind_1, ind_2 = None, None

            brk = False
            if ind_1 is None or ind_2 is None:
                pass
            else:
                while True:
                    try:
                        f_1 = v1['n_frame'][ind_1]
                        f_2 = v2['n_frame'][ind_2]
                        print('Nframe: ', f_1, f_2)
                        if f_1 > f_2:
                            if direct == 'next':
                                ind_2 += 1
                            elif direct == 'prev' and ind_1 != 0:
                                ind_1 -= 1
                            elif ind_1 == 0:
                                break
                        elif f_1 < f_2:
                            if direct == 'next':
                                ind_1 += 1
                            elif direct == 'prev':
                                ind_2 -= 1
                        elif f_1 == f_2:
                            c_1 = v1['path'][ind_1]
                            c_2 = v2['path'][ind_2]
                            dist = np.linalg.norm(np.array(c_1) - np.array(c_2))
                            print(dist)
                            if dist <= 50:
                                brk = True
                                self.stop_ind = f_1                       
                                print('break from while loop')
                                break
                            else:
                                if direct == 'next':
                                    ind_1 += 1
                                    ind_2 += 1
                                elif direct == 'prev' and ind_1 != 0 and ind_2 != 0:
                                    ind_1 -= 1
                                    ind_2 -= 1
                                elif ind_1 == 0 or ind_2 == 0:
                                    break
                    except Exception as e:
                        print(e)
                        break
                if brk:
                    print('break from for loop')
                    break

        if brk:
            self.n_frame = self.stop_ind

            values = [self.tv.item(child)['values'] for child in self.tv.get_children()]
            if self.n_frame not in list(map(lambda x: x[0], values)):
                # popup label box
                self.k1 = k1
                self.k2 = k2
                self.on_add(sug_name=k1)
        else:
            self.msg('沒有埋葬蟲相鄰的 frame 了')

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


