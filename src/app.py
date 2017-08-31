import tkinter as tk
from tkinter import ttk
import cv2
import time, os, json, copy
import numpy as np
from PIL import Image, ImageTk

from src.keyhandler import KeyHandler
from src.interface import Interface
from src.utils import Utils

class Labeler(tk.Frame, KeyHandler, Interface, Utils):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        # basic variables
        self.video_path = None
        self.trajectory_path = None
        self.__video__ = None
        self.__trajectory__ = None
        self.width = 1280
        self.height = 720
        self.fps = None
        self.resolution = None
        self.total_frame = None

        self.stop_ind = 1
        self.__frame__ = None
        self.__orig_frame__ = None
        self.__image__ = None

        # UI
        self.parent = parent
        self.parent.title('Burying Beetle Behavior Labeler')
        self.parent.iconbitmap('icons/title.ico')
        self.parent.protocol('WM_DELETE_WINDOW', self.on_close)
        self.parent.option_add('*tearOff', False)
        tk.Grid.rowconfigure(self, 0 , weight=1)
        tk.Grid.columnconfigure(self, 0 , weight=1)
        tk.Grid.rowconfigure(self, 1 , weight=1)
        # tk.Grid.columnconfigure(self, 1 , weight=1)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Georgia', 14))
        style.configure("Treeview", font=('Georgia', 12))
        # style.configure("TButton.text.", font=('Georgia', 12))
        # style.configure(".", font=('Helvetica', 15))

        self.create_ui()
        self.update_display()

        # display label ratio relative to whole window
        self.update_idletasks()
        print(self.winfo_reqheight(), self.winfo_reqwidth())
        print(self.winfo_height(), self.winfo_width())
        print(self.parent.winfo_reqheight(), self.parent.winfo_reqwidth())
        self._r_height = self.__frame__.shape[0] / self.winfo_reqheight()
        self._r_width = self.__frame__.shape[1] / self.winfo_reqwidth()
        print(self._r_height, self._r_width)
        
        # maximize the window
        self.parent.state('zoomed')

    def update_display(self):
        if self.video_path is not None:
            self.update_frame()
        self.draw()
        self.__image__ = ImageTk.PhotoImage(Image.fromarray(self.__frame__))            
        self.disply_l.configure(image=self.__image__)

        self.disply_l.after(20, self.update_display)

    def update_frame(self):
        self.__video__.set(cv2.CAP_PROP_POS_FRAMES, self.stop_ind - 1)
        ok, self.__frame__ = self.__video__.read()
        self.__orig_frame__ = self.__frame__.copy()

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
        file.add_command(label='儲存操作', command=lambda: print('save'))
        menu.add_cascade(label='File', menu=file)

        help = tk.Menu(menu)
        help.add_command(label='設定', command=lambda: print('settings'))
        menu.add_cascade(label='Help', menu=help)

    def create_button(self):
        b1 = ttk.Button(self.button_frame, text='next (will change to icon)', command=lambda: print('button 1 was pressed'))
        b1.grid(row=0, column=0, sticky='news', padx=5, pady=5)
        b2 = ttk.Button(self.button_frame, text='next (will change to icon)', command=lambda: print('button 2 was pressed'))
        b2.grid(row=0, column=1, sticky='news', padx=5, pady=5)

    def create_treeview(self):
        self.tv = ttk.Treeview(self, height=20)
        self.tv['columns'] = ('f', 'n', 'b')
        self.tv.heading('#0', text='', anchor='center')
        self.tv.column('#0', anchor='w', width=0)
        self.tv.heading('f', text='幀數')
        self.tv.column('f', anchor='center', width=70)
        self.tv.heading('n', text='名稱')
        self.tv.column('n', anchor='center', width=90)
        self.tv.heading('b', text='行為')
        self.tv.column('b', anchor='center', width=120)
        self.tv.grid(row=0, column=1, rowspan=2, sticky='wsne', padx=10, pady=10)
        
        for i, v in enumerate([('1', 'A', 'chase'), ('2', 'B', 'escape'), ('100', 'C', 'attack')]):
            self.tv.insert('', 'end', i, values=v)

        self.tv.bind('<Double-Button-1>', self.tvitem_click)

    def create_ui(self):
        
        self.create_menu()

        # display label
        self.__frame__ = np.zeros((720, 1280, 3), dtype='uint8')
        cv2.putText(self.__frame__, 'Load Video', (300, 360), 7, 5, (255, 255, 255), 2)
        self.__orig_frame__ = self.__frame__.copy()
        self.__image__ = ImageTk.PhotoImage(Image.fromarray(self.__frame__))
        self.display_frame = tk.Frame(self)
        self.display_frame.grid(sticky='news', padx=10, pady=10)
        self.display_frame.grid_rowconfigure(0, weight=1)
        self.display_frame.grid_columnconfigure(0, weight=1)
        self.disply_l = ttk.Label(self.display_frame, image=self.__image__)
        self.disply_l.grid(row=0, column=0, sticky='news', padx=10, pady=10)

        # frame operation frame
        self.button_frame = ttk.LabelFrame(self)
        self.button_frame.grid(row=1, column=0, sticky='news', padx=10, pady=10)
        self.button_frame.grid_rowconfigure(0, weight=1)
        self.button_frame.grid_rowconfigure(1, weight=1)
        self.create_button()

        # record operation frame
        self.create_treeview()

        self.parent.bind('<Escape>', self.on_close)
