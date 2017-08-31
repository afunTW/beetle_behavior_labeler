# import pywt._extensions._cwt
from scipy.linalg import _fblas
import scipy.spatial.ckdtree
# import argparse
import tkinter as tk
from src.app import Labeler

# parser = argparse.ArgumentParser(description='Some arguement for path connector')
# parser.add_argument('-m', '--max', type=int, default=300, help='maximum frame for displaying path')
# parser.add_argument('-t', '--tolerance', type=int, default=38, help='maximum tolerance of distance')
# args = vars(parser.parse_args())

if __name__ == '__main__':
	Labeler()
    # root = tk.Tk()
    # tk.Grid.rowconfigure(root, 0 , weight=1)
    # tk.Grid.columnconfigure(root, 0 , weight=1)

    # Labeler(root, bg='red').grid(sticky='news', padx=0, pady=0)
    # root.focus_force()
    # root.mainloop()
