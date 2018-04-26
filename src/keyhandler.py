import logging
import tkinter as tk
from itertools import combinations
from tkinter.filedialog import asksaveasfilename

import numpy as np
import pandas as pd

from src.interface import Interface

LOGGER = logging.getLogger(__name__)


class KeyHandler(object):

    def tvitem_click(self, event, item=None):
        if self.video_path is not None:
            sel_items = self.tv.selection() if item is None else item
            if sel_items:
                self.n_frame = self.tv.item(self.tv.selection()[0])['values'][0]

    def set_n_frame(self, s):
        v = int(float(s))
        self.n_frame = v
        self.update_entry()

    def update_entry(self):
        try:
            # update entry
            current_id = self.init_f.focus_get()
            if current_id is not None:
                if current_id == self.init_f_focus_id:
                    self.init_f.delete(0, tk.END)
                    self.init_f.insert(0, self.n_frame)
                else:
                    if self.n_frame >= int(self.init_f.get()):
                        self.end_f.delete(0, tk.END)
                        self.end_f.insert(0, self.n_frame)
        except Exception as e:
            LOGGER.exception(e)

    def set_n_frame_2(self, event):
        self.n_frame = int(float(self.var_n_frame.get()))

    # move to previous frame
    def on_left(self, event=None, n=10):
        if self.video_path is not None:
            if self.n_frame > 1:
                self.n_frame = max(1, self.n_frame-n)
            else:
                self.msg('Already the first frame!')

    # move to next frame
    def on_right(self, event=None, n=10):
        if self.video_path is not None:
            if self.n_frame == self.total_frame:
                self.msg('Already the last frame!')
            else:
                self.n_frame = min(self.total_frame, self.n_frame+n)

    # return to label frame index
    def on_return(self, event=None):
        self.n_frame = self.stop_ind
        self.update_entry()

    # add behavior record
    def on_add(self, event=None, sug_name=None):
        if self.init_f.get() != self.end_f.get():
            value = (self.init_f.get(), self.end_f.get(), self.obj_a.get(), self.actions.get(), self.obj_b.get())
            self.tv.insert('', 'end', len(self.tv.get_children()), values=value)

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
    def get_stop_ind(self, direct='next', n=None, measure='distance'):
        pair = combinations(sorted(self.__trajectory__.keys()), 2)
        n = self.n_frame if n is None else n
        for k1, k2 in pair:
            v1 = self.__trajectory__[k1]
            v2 = self.__trajectory__[k2]

            try:
                if direct == 'next':
                    ind_1 = min([v1['n_frame'].index(f) for f in v1['n_frame'] if f > n])
                    ind_2 = min([v2['n_frame'].index(f) for f in v2['n_frame'] if f > n])
                    center_1 = v1['path'][ind_1:]
                    center_2 = v2['path'][ind_2:]
                    wh_1 = v1['wh'][ind_1:]
                    wh_2 = v2['wh'][ind_2:]
                elif direct == 'prev':
                    ind_1 = max([v1['n_frame'].index(f) for f in v1['n_frame'] if f < n])
                    ind_2 = max([v2['n_frame'].index(f) for f in v2['n_frame'] if f < n])
                    center_1 = v1['path'][:(ind_1)]
                    center_2 = v2['path'][:(ind_2)]
                    wh_1 = v1['wh'][:(ind_1)]
                    wh_2 = v2['wh'][:(ind_2)]
            except Exception as e:
                ind_1, ind_2 = None, None
                LOGGER.exception(e)

            brk = False
            if ind_1 and ind_2:
                while True:
                    try:
                        f_1 = v1['n_frame'][ind_1]
                        f_2 = v2['n_frame'][ind_2]
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

                            if measure == 'distance':
                                dist = np.linalg.norm(np.array(c_1) - np.array(c_2))
                                if dist <= 50:
                                    brk = True
                                    self.stop_ind = f_1
                                    LOGGER.info('break from while loop')
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
                            elif measure == 'iou':
                                pass

                    except Exception as e:
                        LOGGER.exception(e)
                        break
                if brk:
                    LOGGER.info('break from for loop')
                    break

        if brk:
            values = [self.tv.item(child)['values'] for child in self.tv.get_children()]
            try:
                nframes = list(map(lambda x: x[0], values))
                flag = nframes.count(self.stop_ind)
                if flag == 0:
                    self.k1 = k1
                    self.k2 = k2
                    self.n_frame = self.stop_ind
                    # self.on_add(sug_name=k1)
                elif flag == 1:
                    ind = nframes.index(self.stop_ind)
                    try:
                        name = list(map(lambda x: x[1], values))[ind]
                    except Exception as e:
                        LOGGER.exception(e)
                    if k1 == name:
                        self.k2 = k2
                        self.k1 = None
                        self.n_frame = self.stop_ind
                        # self.on_add(sug_name=k2)
                    elif k2 == name:
                        self.k1 = k1
                        self.k2 = None
                        self.n_frame = self.stop_ind
                        # self.on_add(sug_name=k1)
                elif flag >= 2:
                    LOGGER.info('flag2')
                    self.get_stop_ind(direct=direct, n=self.stop_ind)

                # update new init frame
                self.init_f.delete(0, tk.END)
                self.init_f.insert(0, self.n_frame)
            except Exception as e:
                LOGGER.exception(e)
                pass
        else:
            self.msg('%s沒有埋葬蟲相鄰的 frame 了。' % ('往前' if direct=='prev' else '往後'))

    def on_select_all(self, event=None):
        if self.video_path is not None:
            for x in self.tv.get_children():
                self.tv.selection_add(x)

    def on_save(self, event=None):
        self.__results_dict__ = {'start_frame': [], 'end_frame': [], 'object_1': [], 'object_2': [], 'behav': []}
        values = [self.tv.item(child)['values'] for child in self.tv.get_children()]
        self.__results_dict__['start_frame'] = list(map(lambda x: x[0], values))
        self.__results_dict__['end_frame'] = list(map(lambda x: x[1], values))
        self.__results_dict__['object_1'] = list(map(lambda x: x[2], values))
        self.__results_dict__['behav'] = list(map(lambda x: x[3], values))
        self.__results_dict__['object_2'] = list(map(lambda x: x[4], values))

        df = pd.DataFrame(self.__results_dict__)
        df = df.reindex_axis(['start_frame', 'end_frame', 'object_1', 'behav', 'object_2'], axis=1)
        root = '/'.join(self.video_path.split('/')[:-1])
        filename = self.video_path.split('/')[-1].split('.avi')[0] + '_behavior_record'
        filename = asksaveasfilename(initialdir='%s' % (root),
                                     defaultextension=".csv",
                                     filetypes=(("CSV (逗號分隔)", "*.csv"),("All Files", "*.*")),
                                     initialfile=filename,
                                     title='存檔')
        df.to_csv(filename, index=False)

        self.msg("行為標註已存檔於 %s" % filename)

    def jump_frame(self, event):
        popup = Interface.popupEntry(self.parent, title="移動幀數", string="請輸入介於 %s ~ %s 的數字。" % (1, self.total_frame), validnum=True)
        self.parent.wait_window(popup.top)
        try:
            n = int(popup.value)
            if n >= 1 and n <= self.total_frame:
                self.n_frame = n
            else:
                self.msg("請輸入介於 %s ~ %s 的數字。" % (1, self.total_frame))
                self.jump_frame()
        except Exception as e:
            LOGGER.exception(e)

    def on_key(self, event):
        sym = event.keysym
        if sym == '1':
            self.actions.current(0)
        elif sym == '2':
            self.actions.current(1)
        elif sym == '3':
            self.actions.current(2)
        elif sym == 'q':
            self.obj_a.current(0)
        elif sym == 'w':
            self.obj_a.current(1)
        elif sym == 'e':
            self.obj_a.current(2)
        elif sym == 'r':
            self.obj_a.current(3)
        elif sym == 'a':
            self.obj_b.current(0)
        elif sym == 's':
            self.obj_b.current(1)
        elif sym == 'd':
            self.obj_b.current(2)
        elif sym == 'f':
            self.obj_b.current(3)
