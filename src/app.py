import tkinter as tk
from tkinter import ttk
import cv2
import time, os, json, copy
import numpy as np
from PIL import Image, ImageTk

from src.keyhandler import KeyHandler
from src.interface import Interface
from src.utils import Utils

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

        self.stop_ind = 1
        self.n_frame = 1
        self.__frame__ = None
        self.__orig_frame__ = None
        self.__image__ = None
        self.var_n_frame = None
        self.scale_n_frame = None
        self.label_n_frame_left = None
        self.label_n_frame_right = None
        self.k1 = None
        self.k2 = None

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

        # display label ratio relative to whole window
        self.parent.update_idletasks()
        self._r_height = self.__frame__.shape[0] / self.parent.winfo_reqheight()
        self._r_width = self.__frame__.shape[1] / self.parent.winfo_reqwidth()
        
        # maximize the window
        self.parent.state('zoomed')

        self.parent.mainloop()

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
        # if str(self.label_n_frame_left.focus_get().__class__) != "<class 'tkinter.ttk.Entry'>":
        if self.video_path is not None:
            try:
                self.var_n_frame.set(self.n_frame)
                self.scale_n_frame.set(self.n_frame)
                self.label_n_frame_left.config(text='%s/%s' % (self.n_frame, self.total_frame))

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

    def create_button(self):
        buttons = []
        # button to click
        button_frame = tk.Frame(self.op_frame)
        button_frame.grid(row=0, column=0)
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
        scale_frame.grid(row=1, column=0, sticky='news')

        scale_frame.grid_rowconfigure(0, weight=1)
        for i in range(3):
            scale_frame.grid_columnconfigure(i, weight=1)

        # self.label_n_frame_left = ttk.Entry(scale_frame, textvariable=self.var_n_frame, width=10, justify='right', vcmd=vcmd, validate='key')
        # self.label_n_frame_left.bind('<Return>', self.set_n_frame_2)
        # self.label_n_frame_left = ttk.Label(scale_frame, textvariable=self.var_n_frame)
        self.label_n_frame_left = ttk.Label(scale_frame, text='%s/%s' % (self.n_frame, self.total_frame))
        self.label_n_frame_left.grid(row=0, column=0, pady=5)
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
        info_label_frame.grid(row=0, column=0, sticky='news')

        label_video_name = ttk.Label(info_label_frame, text='影像檔名: ')
        label_video_name.grid(row=0, column=0, sticky='w')
        self.label_video_name = ttk.Label(info_label_frame, text=text_video_name)
        self.label_video_name.grid(row=0, column=1, sticky='w')
        label_time = ttk.Label(info_label_frame, text='影像時間: ')
        label_time.grid(row=1, column=0, sticky='w')
        self.label_time = ttk.Label(info_label_frame, text=text_time)
        self.label_time.grid(row=1, column=1, sticky='w')

    def create_treeview(self):
        self.tv = ttk.Treeview(self.info_frame, height=20)
        self.tv['columns'] = ('f', 'n', 'b')
        self.tv.heading('#0', text='', anchor='center')
        self.tv.column('#0', anchor='w', width=0)
        self.tv.heading('f', text='幀數')
        self.tv.column('f', anchor='center', width=90)
        self.tv.heading('n', text='名稱')
        self.tv.column('n', anchor='center', width=120)
        self.tv.heading('b', text='行為')
        self.tv.column('b', anchor='center', width=150)
        self.tv.grid(row=1, column=0, rowspan=2, sticky='news', pady=10)
        
        vsb = ttk.Scrollbar(self.info_frame, orient="vertical", command=self.tv.yview)
        vsb.grid(row=1, column=1, rowspan=2, sticky='news', pady=10)
        
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
        self.display_frame.grid_columnconfigure(0, weight=1)
        self.display_frame.grid_rowconfigure(1, weight=1)
        self.disply_l = ttk.Label(self.display_frame, image=self.__image__)
        self.disply_l.grid(row=0, column=0, sticky='news', padx=10, pady=10)

        # frame operation frame
        # self.button_frame = ttk.LabelFrame(self.display_frame)
        self.op_frame = tk.Frame(self.display_frame)
        self.op_frame.grid(row=1, column=0, sticky='news', padx=10, pady=10)
        self.op_frame.grid_rowconfigure(0, weight=1)
        self.op_frame.grid_rowconfigure(1, weight=1)
        self.op_frame.grid_columnconfigure(0, weight=1)
        self.create_button()

        self.info_frame = tk.Frame(self.parent)
        self.info_frame.grid(row=0, column=1, rowspan=2, sticky='news', pady=10)
        self.info_frame.grid_columnconfigure(0, weight=1)
        self.info_frame.grid_rowconfigure(1, weight=1)
        self.info_frame.grid_columnconfigure(1, weight=1)

        # display info
        self.create_info()

        # record operation frame
        self.create_treeview()

        self.parent.bind('<Escape>', self.on_close)
        self.parent.bind('<Left>', self.on_left)
        self.parent.bind('<Right>', self.on_right)
        self.parent.bind('<Return>', self.on_return)
        self.parent.bind('<Down>', self.on_next)
        self.parent.bind('<Up>', self.on_prev)
        self.tv.bind('<Control-a>', self.on_select_all)
        self.parent.bind('<a>', self.on_add)
        self.parent.bind('<d>', self.on_delete)
