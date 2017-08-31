import cv2
import numpy as np
from PIL import Image, ImageTk

class Utils(object):

    def draw(self):
        self.__frame__ = self.__orig_frame__.copy()
        if self.parent.state() == 'zoomed':
            shape = self.__frame__.shape
            r1 = (self.parent.winfo_screenwidth() / shape[1])
            r2 = (self.parent.winfo_screenheight() / shape[0])
            shrink_r = max(r1, r2)
            self._c_width = self._r_width * shrink_r
            self._c_height = self._r_height * shrink_r
            print(shrink_r)
            # newsize = (int(shape[1] * self._c_width), int(shape[0] * self._c_height))
            newsize = (int(1802 * self._r_width), int(1026 * self._r_height))
            print(newsize)
            self.__frame__ = cv2.resize(self.__frame__, newsize)
            self.update_idletasks()
            print(self.winfo_reqwidth(), self.winfo_reqheight())
            # _r_height = self.__frame__.shape[0] / self.winfo_reqheight()
            # _r_width = self.__frame__.shape[1] / self.winfo_reqwidth()
            # print(_r_height, _r_width)


        self.__frame__ = cv2.cvtColor(self.__frame__, cv2.COLOR_BGR2RGB)