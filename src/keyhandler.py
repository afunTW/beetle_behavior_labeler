# import tkinter as tk
# from tkinter import ttk
import pandas as pd
import numpy as np
from tkinter.filedialog import asksaveasfilename
from itertools import combinations
from src.interface import Interface
import tkinter as tk

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
        except:
            pass

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
        print('on_add')
        value = (self.init_f.get(), self.end_f.get(), self.obj_a.get(), self.actions.get(), self.obj_b.get())
        self.tv.insert('', 'end', len(self.tv.get_children()), values=value)

        

        # if self.video_path is not None and (len(self.tv.selection()) != len(self.tv.get_children()) or len(self.tv.get_children()) == 0):
        #     if sug_name is not None:
        #         if self.k1 is not None:
        #             popup = Interface.popupEdit(self.parent, title="新增", name=sorted(self.__trajectory__.keys()), ind=(self.n_frame, self.total_frame, self.k1), tv=self.tv)
        #             self.parent.wait_window(popup.top)
        #             # self.k1 = None
        #             if self.k2 is not None:
        #                 popup = Interface.popupEdit(self.parent, title="新增", name=sorted(self.__trajectory__.keys()), ind=(self.n_frame, self.total_frame, self.k2), tv=self.tv)
        #                 self.parent.wait_window(popup.top)
        #                 # self.k2 = None
        #         elif self.k2 is not None:
        #             popup = Interface.popupEdit(self.parent, title="新增", name=sorted(self.__trajectory__.keys()), ind=(self.n_frame, self.total_frame, self.k2), tv=self.tv)
        #             self.parent.wait_window(popup.top)
        #             if self.k1 is not None:
        #                 popup = Interface.popupEdit(self.parent, title="新增", name=sorted(self.__trajectory__.keys()), ind=(self.n_frame, self.total_frame, self.k1), tv=self.tv)
        #                 self.parent.wait_window(popup.top)

        #     else:
        #         popup = Interface.popupEdit(self.parent, title="新增", name=sorted(self.__trajectory__.keys()), ind=(self.n_frame, self.total_frame, None), tv=self.tv)
        #         self.parent.wait_window(popup.top)

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
                # print('Index: ', ind_1, ind_2, len(v1['n_frame']), len(v2['n_frame']))
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
                        # print('Nframe: ', f_1, f_2)
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
                                # print(dist)
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
                            elif measure == 'iou':
                                pass
                                
                    except Exception as e:
                        print(e)
                        break
                if brk:
                    print('break from for loop')
                    break

        if brk:
            # print('come', '\n'*10)

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
                        print(e)
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
                    print('flag2', "\n"*10)
                    self.get_stop_ind(direct=direct, n=self.stop_ind)

                # update new init frame
                self.init_f.delete(0, tk.END)
                self.init_f.insert(0, self.n_frame)
            except Exception as e:
                print(e)
                pass
        else:
            self.msg('%s沒有埋葬蟲相鄰的 frame 了。' % ('往前' if direct=='prev' else '往後'))

    def on_select_all(self, event=None):
        if self.video_path is not None:
            for x in self.tv.get_children():
                self.tv.selection_add(x)

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
            print(e)
