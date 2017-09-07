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
            # self.label_n_frame_right['text'] = self.total_frame
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
            # top.resizable(False, False)
            self.tv = tv
            self.title = title
            bev = ['Attack', 'Wrestle', 'Chase', 'Escape']

            top.title(title)
            tk.Grid.rowconfigure(top, 0, weight=1)
            tk.Grid.columnconfigure(top, 0, weight=1)
            top.transient(master)
            top.grab_set()
            top.focus_force()
            infoframe = ttk.Frame(top)
            infoframe.grid(row=0, column=0, padx=10)
            tk.Label(infoframe, text='幀數:', font=("Georgia", 12)).grid(row=0, column=0, padx=10, sticky='w')
            tk.Label(infoframe, text='名稱:', font=("Georgia", 12)).grid(row=0, column=2, padx=10, sticky='w')
            # tk.Label(top, text='行為:', font=("Georgia", 12)).grid(row=1, column=0, padx=10)

            f_ind = ind[0] if title == '新增' else self.tv.item(self.tv.selection()[0])['values'][0]
            if title == '新增' and ind[2] is not None:
                n_ind = name.index(ind[2])
            elif ind[2] is None:
                n_ind = 0
            else:
                n_ind = name.index(self.tv.item(self.tv.selection()[0])['values'][2])
            b_ind = 0 if title == '新增' else bev.index(self.tv.item(self.tv.selection()[0])['values'][2])
            
            # self.f = ttk.Combobox(top, values=list(range(1, ind[1])))
            # self.f.current(f_ind - 1)
            # e = tk.Entry(r,width=60)
            self.f = ttk.Entry(infoframe, width=8)
            self.f.insert(0, ind[0])
            self.f.configure(state='readonly')
            self.f.grid(row=0, column=1, padx=10, sticky='w')
            # self.f.bind('<Return>', lambda event: self.cleanup())
            self.n = ttk.Combobox(infoframe, values=name, width=8)
            self.n.current(n_ind)
            # self.n.configure(state='readonly')
            self.n.grid(row=0, column=3, padx=10, sticky='w')
            # self.n.bind('<Return>', lambda event: self.cleanup())

            button_frame = ttk.LabelFrame(top, text='行為')
            button_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=10)
            for i, b in enumerate(bev):
                butt = ttk.Button(button_frame, text="%s (%s)" % (b, i+1), command=lambda behav=b: self.cleanup(behav=behav))
                butt.grid(row=2, column=i, sticky='news', padx=5, pady=5)
                top.bind('%s' % (i+1), lambda event, behav=b: self.cleanup(behav=behav))

            width = top.winfo_reqwidth() + 10
            height = top.winfo_reqheight() + 10
            x = (top.winfo_screenwidth() // 2.25) - (width // 2)
            y = (top.winfo_screenheight() // 2) - (height // 2)
            top.geometry('+%d+%d' % (x, y))
            # top.geometry('240x180')

            top.bind('<Escape>', lambda event: top.destroy())

        def cleanup(self, event=None, behav=None):
            self.value = (self.f.get(), self.n.get(), behav)
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