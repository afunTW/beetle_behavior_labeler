import tkinter as tk
from tkinter import ttk
import cv2
import time, os, json, copy
import numpy as np
import pandas as pd
from itertools import combinations
from PIL import Image, ImageTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from src.keyhandler import KeyHandler
from src.interface import Interface
from src.utils import Utils

N_MAX_PLOT = 800000

class BehaviorLabeler(KeyHandler, Interface, Utils):

    def __init__(self, *args, **kwargs):
        # basic variables
        self.video_path = None
        self.trajectory_path = None
        self.__video__ = None
        self.__trajectory__ = None
        self.__obj_name__ = None
        self.__results_dict__ = dict()
        self.width = 1280
        self.height = 720
        self.fps = None
        self.resolution = None
        self.total_frame = None
        self.dist_df = None

        self.stop_ind = 1
        self.n_frame = 1
        self.__frame__ = None
        self.__orig_frame__ = None
        self.__image__ = None
        self.var_n_frame = None
        self.scale_n_frame = None
        self.label_n_frame = None
        self.label_n_frame_right = None
        self.k1 = None
        self.k2 = None
        self.lines = [] # for matplotlib distance plot

        self.init_f_focus_id = None
        self.end_f_focus_id = None

        # UI
        self.parent = tk.Tk()
        self.parent.title('Burying Beetle Behavior Labeler')
        self.parent.iconbitmap('icons/title.ico')
        self.parent.protocol('WM_DELETE_WINDOW', self.on_close)
        self.parent.option_add('*tearOff', False)
        tk.Grid.rowconfigure(self.parent, 0 , weight=1)
        tk.Grid.columnconfigure(self.parent, 0 , weight=1)
        tk.Grid.rowconfigure(self.parent, 1 , weight=1)
        tk.Grid.columnconfigure(self.parent, 1 , weight=1)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Georgia', 14))
        style.configure("Treeview", font=('Georgia', 12))

        self.create_ui()

        # update
        self.update_display()
        self.update_label()
        self.update_distance()

        # display label ratio relative to whole window
        self.parent.update_idletasks()
        self._r_height = self.__frame__.shape[0] / self.parent.winfo_reqheight()
        self._r_width = self.__frame__.shape[1] / self.parent.winfo_reqwidth()
        
        # maximize the window
        self.parent.state('zoomed')

        self.parent.mainloop()

    def calc_dist(self):
        obj_name = self.__obj_name__
        traj = self.__trajectory__

        df = pd.DataFrame()
        for k in sorted(obj_name.keys(), key=lambda x: obj_name[x]['display_name']):
            path = traj[k]['path']
            f_ind = traj[k]['n_frame']
            tmp_df = pd.DataFrame({'n_frame': f_ind, obj_name[k]['display_name']: path})
            if df.shape[0] == 0:
                df = tmp_df
            else:
                df = pd.merge(df, tmp_df, how='outer', on='n_frame')

        column_nm = sorted([obj_name[k]['display_name'] for k in obj_name.keys()])
        dist_df = pd.DataFrame()
        for k1, k2 in combinations(column_nm, 2):
            tmp_df = df[["n_frame", k1, k2]].dropna()
            tmp_dist = np.linalg.norm(np.array(tmp_df[k1].tolist()) - np.array(tmp_df[k2].tolist()), axis=1)
            tmp_dist_df = pd.DataFrame({"n_frame": tmp_df.n_frame, "%s - %s" % (k1, k2): tmp_dist})
            if dist_df.shape[0] == 0:
                dist_df = tmp_dist_df
            else:
                dist_df = pd.merge(dist_df, tmp_dist_df, how='outer', on='n_frame')

        dist_df.set_index("n_frame", inplace=True)
        dist_df.sort_index(inplace=True)

        self.dist_df = dist_df

    def update_distance(self):

        if self.dist_df is not None:
            # self.start_f = 0
            # self.end_f = min(500, max(self.dist_df.index))

            if len(self.lines) != 0:
                for i in range(self.dist_df.shape[1]):
                    x = self.dist_df.index[self.n_frame:min(self.n_frame+N_MAX_PLOT, self.dist_df.shape[0]-1)]
                    y = self.dist_df.iloc[self.n_frame:min(self.n_frame+N_MAX_PLOT, self.dist_df.shape[0]-1), i-1]
                    self.lines[i].set_data(x, y)
                    ax = self.canvas.figure.axes[i]
                    ax.set_xlim(x.min(), x.max())
                    ax.set_ylim(0, y.max())
                ax.set_xlabel("frame index", fontsize='large')
            elif len(self.lines) == 0:
                
                for i in range(1, self.dist_df.shape[1]+1):
                    ax = self.fig.add_subplot(7, 1, i)
                    x = self.dist_df.index[self.n_frame:min(self.n_frame+N_MAX_PLOT, self.dist_df.shape[0]-1)]
                    y = self.dist_df.iloc[self.n_frame:min(self.n_frame+N_MAX_PLOT, self.dist_df.shape[0]-1), i-1]
                    X, = ax.plot(x, y, color='#008000', label=self.dist_df.columns[i-1], lw=1.5)
                    ax.legend(loc="upper right", fontsize='small')
                    if i < self.dist_df.shape[1]:
                        plt.setp(ax.get_xticklabels(), visible=False)
                    self.lines.append(X)
                self.fig.text(0.04, 0.55, 'Distance', ha='center', fontsize='large')
            self.canvas.draw()
        self.parent.after(100, self.update_distance)

    def update_display(self):
        if self.video_path is not None:
            self.update_frame()
        try:
            self.draw()
            self.__image__ = ImageTk.PhotoImage(Image.fromarray(self.__frame__))            
            self.disply_l.configure(image=self.__image__)
        except:
            pass

        self.disply_l.after(20, self.update_display)

    def update_frame(self):
        self.__video__.set(cv2.CAP_PROP_POS_FRAMES, self.n_frame - 1)
        ok, self.__frame__ = self.__video__.read()
        self.__orig_frame__ = self.__frame__.copy()

    def update_label(self):
        # if int(float(self.var_n_frame.get())) != self.n_frame:
        # if str(self.label_n_frame.focus_get().__class__) != "<class 'tkinter.ttk.Entry'>":
        if self.video_path is not None:
            try:
                self.var_n_frame.set(self.n_frame)
                self.scale_n_frame.set(self.n_frame)
                self.label_n_frame.config(text='%s/%s' % (self.n_frame, self.total_frame))

                text_video_name = self.video_path.split('/')[-1]
                sec = round(self.n_frame / self.fps, 2)
                m, s = divmod(sec, 60)
                h, m = divmod(m, 60)
                text_time = "%d:%02d:%02d" % (h, m, s)
                
                self.label_video_name.configure(text=text_video_name)
                self.label_time.configure(text=text_time)
            except:
                pass

        self.disply_l.after(10, self.update_label)

    def get_focus_entry(self, event=None):
        if self.init_f_focus_id is None:
            self.init_f_focus_id = self.init_f.focus_get()

    def get_focus_entry2(self, event=None):
        if self.end_f_focus_id is None:
            self.end_f_focus_id = self.end_f.focus_get()

    def init_video(self):
        self.__video__ = cv2.VideoCapture(self.video_path)
        self.width = int(self.__video__.get(3))
        self.height = int(self.__video__.get(4))
        self.fps = int(self.__video__.get(5))
        self.resolution = (self.width, self.height)
        self.total_frame = int(self.__video__.get(cv2.CAP_PROP_FRAME_COUNT))

    def create_menu(self):

        menu = tk.Menu(self.parent)
        self.parent.config(menu=menu)

        file = tk.Menu(menu)
        file.add_command(label='載入新影像', command=self.on_load)
        file.add_command(label='儲存操作', command=self.on_save)
        menu.add_cascade(label='File', menu=file)

        # help = tk.Menu(menu)
        # help.add_command(label='設定', command=lambda: print('settings'))
        # menu.add_cascade(label='Help', menu=help)

    def create_op(self):
        input_frame = tk.Frame(self.op_frame)
        input_frame.grid(row=0, column=0)
        tk.Grid.rowconfigure(input_frame, 0, weight=1)
        tk.Grid.columnconfigure(input_frame, 0, weight=1)

        tk.Label(input_frame, text='起始幀數:', font=("Georgia", 14)).grid(row=0, column=0, padx=10, sticky='w')
        tk.Label(input_frame, text='結束幀數:', font=("Georgia", 14)).grid(row=0, column=2, padx=10, sticky='w')
        tk.Label(input_frame, text='Object 1:', font=("Georgia", 14)).grid(row=0, column=4, padx=10, sticky='w')
        tk.Label(input_frame, text='行為:', font=("Georgia", 14)).grid(row=0, column=6, padx=10, sticky='w')
        tk.Label(input_frame, text='Object 2:', font=("Georgia", 14)).grid(row=0, column=8, padx=10, sticky='w')

        self.init_f = ttk.Entry(input_frame, width=8)
        self.init_f.insert(0, 0)
        # self.init_f.configure(state='readonly')
        self.init_f.grid(row=0, column=1, padx=10, sticky='w')

        self.end_f = ttk.Entry(input_frame, width=8)
        self.end_f.insert(0, 0)
        # self.end_f.configure(state='readonly')
        self.end_f.grid(row=0, column=3, padx=10, sticky='w')

        name = sorted(["x", "A", "o", "="])
        self.obj_a = ttk.Combobox(input_frame, values=name, width=5, state="readonly")
        self.obj_a.current(0)
        # self.n.configure(state='readonly')
        self.obj_a.grid(row=0, column=5, padx=10, sticky='w')

        bev = ['Attack', 'Wrestle', 'Chase']
        self.actions = ttk.Combobox(input_frame, values=bev, width=5, state="readonly")
        self.actions.current(0)
        # self.n.configure(state='readonly')
        self.actions.grid(row=0, column=7, padx=10, sticky='w')

        self.obj_b = ttk.Combobox(input_frame, values=name, width=5, state="readonly")
        self.obj_b.current(1)
        # self.n.configure(state='readonly')
        self.obj_b.grid(row=0, column=9, padx=10, sticky='w')

        # create button to click
        buttons = []
        button_frame = tk.Frame(self.op_frame)
        button_frame.grid(row=1, column=0)
        return_img = ImageTk.PhotoImage(file='icons/return.png')
        next_img = ImageTk.PhotoImage(file='icons/next.png')
        next2_img = ImageTk.PhotoImage(file='icons/down.png')
        prev_img = ImageTk.PhotoImage(file='icons/prev.png')
        prev2_img = ImageTk.PhotoImage(file='icons/up.png')
        add_img = ImageTk.PhotoImage(file='icons/add.png')
        delete_img = ImageTk.PhotoImage(file='icons/delete.png')

        b_prev2 = ttk.Button(button_frame, image=prev2_img, command=self.on_prev)
        b_prev2.image = prev2_img
        buttons.append(b_prev2)
        b_prev = ttk.Button(button_frame, image=prev_img, command=self.on_left)
        b_prev.image = prev_img
        buttons.append(b_prev)
        b_return = ttk.Button(button_frame, image=return_img, command=self.on_return)
        b_return.image = return_img
        buttons.append(b_return)
        b_next = ttk.Button(button_frame, image=next_img, command=self.on_right)
        b_next.image = next_img
        buttons.append(b_next)
        b_next2 = ttk.Button(button_frame, image=next2_img, command=self.on_next)
        b_next2.image = next2_img
        buttons.append(b_next2)
        b_add = ttk.Button(button_frame, image=add_img, command=self.on_add)
        b_add.image = add_img
        buttons.append(b_add)
        b_delete = ttk.Button(button_frame, image=delete_img, command=self.on_delete)
        b_delete.image = delete_img
        buttons.append(b_delete)

        for i, b in enumerate(buttons):
            b.grid(row=0, column=i, sticky='news', padx=10, pady=10)
            b.config(cursor='hand2')

        vcmd = (self.parent.register(self.validate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        # scale bar for n frame
        self.var_n_frame = tk.IntVar()

        scale_frame = tk.Frame(self.op_frame)
        scale_frame.grid(row=2, column=0, sticky='news')

        scale_frame.grid_rowconfigure(0, weight=1)
        for i in range(3):
            scale_frame.grid_columnconfigure(i, weight=1)

        # self.label_n_frame = ttk.Entry(scale_frame, textvariable=self.var_n_frame, width=10, justify='right', vcmd=vcmd, validate='key')
        # self.label_n_frame.bind('<Return>', self.set_n_frame_2)
        # self.label_n_frame = ttk.Label(scale_frame, textvariable=self.var_n_frame)
        self.label_n_frame = ttk.Label(scale_frame, text='%s/%s' % (self.n_frame, self.total_frame))
        self.label_n_frame.grid(row=0, column=0, pady=5)
        self.scale_n_frame = ttk.Scale(scale_frame, from_=1, to_=self.total_frame, length=1250, command=self.set_n_frame)
        self.scale_n_frame.set(self.n_frame)
        self.scale_n_frame.state(['disabled'])
        self.scale_n_frame.grid(row=1, column=0, padx=10)
        # self.label_n_frame_right = ttk.Label(scale_frame, text=str(self.total_frame))
        # self.label_n_frame_right.grid(row=0, column=2)

    def create_info(self):
        text_video_name = '-----'
        text_time = '--:--:--'

        info_label_frame = ttk.LabelFrame(self.info_frame, text='影像信息')
        info_label_frame.grid(row=0, column=0, columnspan=2, sticky='news')

        label_video_name = ttk.Label(info_label_frame, text='影像檔名: ')
        label_video_name.grid(row=0, column=0, sticky='w')
        self.label_video_name = ttk.Label(info_label_frame, text=text_video_name)
        self.label_video_name.grid(row=0, column=1, sticky='w')
        label_time = ttk.Label(info_label_frame, text='影像時間: ')
        label_time.grid(row=1, column=0, sticky='w')
        self.label_time = ttk.Label(info_label_frame, text=text_time)
        self.label_time.grid(row=1, column=1, sticky='w')

    def create_potential_treeview(self):
        self.pot_tv = ttk.Treeview(self.info_frame, height=3)
        self.pot_tv['columns'] = ('sf', 'ef')
        self.pot_tv.heading('#0', text='', anchor='center')
        self.pot_tv.column('#0', anchor='w', width=0)
        self.pot_tv.heading('sf', text="start_f")
        self.pot_tv.column('sf', anchor='center', width=160)
        self.pot_tv.heading('ef', text='end_f')
        self.pot_tv.column('ef', anchor='center', width=160)
        self.pot_tv.grid(row=1, column=0, sticky='news', pady=10)

        vsb = ttk.Scrollbar(self.info_frame, orient="vertical", command=self.pot_tv.yview)
        vsb.grid(row=1, column=1, sticky='news', pady=10)
        
        self.pot_tv.configure(yscrollcommand=vsb.set)

    def create_res_treeview(self):
        self.tv = ttk.Treeview(self.info_frame, height=30)
        self.tv['columns'] = ('sf', 'ef', 'obja', 'bev', 'objb')
        self.tv.heading('#0', text='', anchor='center')
        self.tv.column('#0', anchor='w', width=0)
        self.tv.heading('sf', text="start_f")
        self.tv.column('sf', anchor='center', width=70)
        self.tv.heading('ef', text='end_f')
        self.tv.column('ef', anchor='center', width=70)
        self.tv.heading('obja', text='obj_1')
        self.tv.column('obja', anchor='center', width=80)
        self.tv.heading('bev', text='behav')
        self.tv.column('bev', anchor='center', width=80)
        self.tv.heading('objb', text='obj_2')
        self.tv.column('objb', anchor='center', width=80)

        self.tv.grid(row=1, column=0, rowspan=1, sticky='news', pady=10)
        
        vsb = ttk.Scrollbar(self.info_frame, orient="vertical", command=self.tv.yview)
        vsb.grid(row=1, column=1, rowspan=1, sticky='news', pady=10)
        
        self.tv.configure(yscrollcommand=vsb.set)
        self.tv.bind('<Double-Button-1>', self.tvitem_click)

    def create_ui(self):
        
        self.create_menu()

        # display label
        self.__frame__ = np.zeros((720, 1280, 3), dtype='uint8')
        cv2.putText(self.__frame__, 'Load Video', (300, 360), 7, 5, (255, 255, 255), 2)
        self.__orig_frame__ = self.__frame__.copy()
        self.__image__ = ImageTk.PhotoImage(Image.fromarray(self.__frame__))
        

        self.display_frame = tk.Frame(self.parent)
        self.display_frame.grid(row=0, column=0, padx=10, pady=10)
        self.display_frame.grid_rowconfigure(0, weight=1)
        self.display_frame.grid_rowconfigure(1, weight=1)
        self.display_frame.grid_columnconfigure(0, weight=1)
        self.display_frame.grid_rowconfigure(2, weight=1)
        
        self.fig = Figure(figsize=(10, 12))
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.display_frame)
        self.canvas.show()

        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='news')

        self.disply_l = ttk.Label(self.display_frame, image=self.__image__)
        self.disply_l.grid(row=1, column=0, sticky='news', padx=10, pady=10)

        # frame operation frame
        self.op_frame = tk.Frame(self.display_frame)
        self.op_frame.grid(row=2, column=0, sticky='news', padx=10, pady=10)
        self.op_frame.grid_rowconfigure(0, weight=1)
        self.op_frame.grid_rowconfigure(1, weight=1)
        self.op_frame.grid_columnconfigure(0, weight=1)
        self.create_op()

        self.info_frame = tk.Frame(self.parent)
        self.info_frame.grid(row=0, column=1, rowspan=3, sticky='news', pady=10)
        self.info_frame.grid_columnconfigure(0, weight=1)
        self.info_frame.grid_rowconfigure(1, weight=1)
        self.info_frame.grid_columnconfigure(1, weight=1)

        # display info
        self.create_info()
        # self.create_potential_treeview()
        # record operation frame
        self.create_res_treeview()

        self.parent.bind('<Escape>', self.on_close)
        self.parent.bind('<Control-Left>', lambda event: self.on_left(event, n=1))
        self.parent.bind('<Control-Right>', lambda event: self.on_right(event, n=1))
        self.parent.bind('<Left>', lambda event: self.on_left(event))
        self.parent.bind('<Right>', lambda event: self.on_right(event))
        self.parent.bind('<Return>', self.on_return)
        self.parent.bind('<Down>', self.on_next)
        self.parent.bind('<Up>', self.on_prev)
        self.parent.bind('<space>', self.on_add)
        self.parent.bind('<Delete>', self.on_delete)
        self.tv.bind('<Control-a>', self.on_select_all)
        self.parent.bind('<d>', self.on_delete)
        self.parent.bind('<j>', self.jump_frame)
        self.init_f.bind('<FocusIn>', self.get_focus_entry)
        self.end_f.bind('<FocusIn>', self.get_focus_entry2)

        # key bind for input
        for k in ['q', 'w', 'e', 'r', 'a', 's', 'd', 'f']:
            self.parent.bind(k.join('<>'), self.on_key)
        for k in ['1', '2', '3']:
            self.parent.bind(k, self.on_key)
        
