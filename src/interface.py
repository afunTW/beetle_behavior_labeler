import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askokcancel, showinfo, showerror, showwarning
from tkinter.filedialog import askopenfilename
import os
import cv2
import json

class Interface(object):

    # show message
    def msg(self, string, type='info'):
        root = tk.Tk()
        root.withdraw()
        if type == 'info':
            showinfo('Info', string)
        elif type == 'error':
            showerror('Error', string)
        elif type == 'warning':
            showwarning('Warning', string)
        else:
            print('Unknown type %s' % type)

    # confirm quiting
    def on_close(self, event=None):
        if askokcancel('離開', '你確定要關閉程式嗎？'):
            self.parent.destroy()

    def on_load(self):
        ok = self.get_path()
        if ok:
            self.init_video()
            with open(self.trajectory_path, 'r') as f:
                self.__trajectory__ = json.load(f)
            self.scale_n_frame.state(['!disabled'])
            self.scale_n_frame['to_'] = self.total_frame
            self.label_n_frame_right['text'] = self.total_frame
            # self.stop_ind = 1
            self.get_stop_ind()

    def get_path(self):
        path = askopenfilename(title='請選擇影像路徑', filetypes=[('video file (*.avi;)', '*.avi;')])

        if path in [None, ""]:
            self.msg('請載入影像檔案。')
        else:
            jsonfile = path.split('.avi')[0] + '.json'
            res = os.path.isfile(jsonfile)
            if not res:
                self.msg('影像檔案路徑底下沒有對應的 json 檔。')
            else:
                self.video_path = path
                self.trajectory_path = jsonfile
                return True

        return False

    class popupEdit(object):

        def __init__(self, master, title, name, ind, tv):
            top=self.top= tk.Toplevel(master)
            self.tv = tv
            self.title = title
            top.title(title)
            tk.Grid.rowconfigure(top, 0, weight=1)
            tk.Grid.columnconfigure(top, 0, weight=1)
            top.transient(master)
            top.grab_set()

            tk.Label(top, text='幀數', font=("Georgia", 12)).grid(row=0, column=0, padx=10, pady=10)
            tk.Label(top, text='名稱', font=("Georgia", 12)).grid(row=1, column=0, padx=10, pady=10)
            tk.Label(top, text='行為', font=("Georgia", 12)).grid(row=2, column=0, padx=10, pady=10)
            
            self.f = ttk.Combobox(top, values=list(range(1, ind[1])))
            self.f.current(ind[0] - 1)
            self.f.focus_force()
            self.f.grid(row=0, column=1, padx=10, pady=10, sticky='news')
            self.f.bind('<Return>', lambda event: self.cleanup())
            self.n = ttk.Combobox(top, values=name)
            self.n.current(0)
            self.n.grid(row=1, column=1, padx=10, pady=10, sticky='news')
            self.n.bind('<Return>', lambda event: self.cleanup())
            self.b = ttk.Combobox(top, values=['Attack', 'Wrestle', 'Chase', 'Escape'])
            self.b.current(0)
            self.b.grid(row=2, column=1, padx=10, pady=10, sticky='news')
            self.b.bind('<Return>', lambda event: self.cleanup())
            
            bt = ttk.Button(top,text='Ok',command=self.cleanup, width=5)
            bt.grid(row=4, column=0, columnspan=2, sticky='news', padx=10, pady=10)

            top.update_idletasks()
            width = top.winfo_reqwidth() + 10
            height = top.winfo_reqheight() + 10
            x = (top.winfo_screenwidth() // 2) - (width // 2)
            y = (top.winfo_screenheight() // 2) - (height // 2)
            top.geometry('+%d+%d' % (x, y))
            top.geometry('240x180')

            top.bind('<Escape>', lambda event: top.destroy())

        def cleanup(self):
            self.value = (self.f.get(), self.n.get(), self.b.get())
            if self.title == '新增':
                self.tv.insert('', 'end', len(self.tv.get_children()), values=self.value)
            elif self.title == '更改':
                pass
            self.top.destroy()
        
    class popupEntry(object):

        def __init__(self, master, title, string, validnum=False):
            top=self.top= tk.Toplevel(master)
            top.title(title)
            tk.Grid.rowconfigure(top, 0, weight=1)
            tk.Grid.columnconfigure(top, 0, weight=1)
            top.transient(master)
            top.grab_set()

            self.l=tk.Label(top,text=string, font=("Verdana", 12))
            self.l.pack(expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)
            if validnum:
                vcmd = (master.register(self.validate), 
                    '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
                self.e =ttk.Entry(top, validate='key', validatecommand=vcmd)
            else:
                self.e = ttk.Entry(top)
            self.e.config(width=9)
            self.e.pack(expand=tk.YES, padx=5, pady=5)
            self.e.focus_force()
            self.e.bind('<Return>', lambda event: self.cleanup())
            self.b = ttk.Button(top,text='Ok',command=self.cleanup, width=5)
            self.b.pack(expand=tk.YES, padx=5, pady=5)

            top.update_idletasks()
            width = top.winfo_reqwidth() + 10
            height = top.winfo_reqheight() + 10
            x = (top.winfo_screenwidth() // 2.25) - (width // 2)
            y = (top.winfo_screenheight() // 2) - (height // 2)
            top.geometry('+%d+%d' % (x, y))
            top.geometry('260x120')

            top.bind('<Escape>', lambda event: top.destroy())

            # pending; bind return, a decent name judge
        def cleanup(self):
            self.value=self.e.get()
            self.top.destroy()
        
        def validate(self, action, index, value_if_allowed,
                           prior_value, text, validation_type, trigger_type, widget_name):
            if text in '0123456789':
                try:
                    float(value_if_allowed)
                    return True
                except ValueError:
                    return False
            else:
                return False