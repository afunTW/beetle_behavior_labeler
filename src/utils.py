import cv2
import numpy as np
from PIL import Image, ImageTk

class Utils(object):

    def draw(self):
        self.__frame__ = self.__orig_frame__.copy()
        if self.video_path is not None:
            for k, v in self.__trajectory__.items():
                nframe = v['n_frame']
                traj = v['path']

                try:
                    ind = nframe.index(self.stop_ind)
                    p = tuple(traj[ind])
                    cv2.circle(self.__frame__, p, 10, (255, 255, 0), 1)
                except Exception as e:
                    print(e)
                    pass

        if self.parent.state() == 'zoomed':
            shape = self.__frame__.shape
            r1 = (shape[1] / self.parent.winfo_screenwidth())
            r2 = (shape[0] / self.parent.winfo_screenheight())
            shrink_r = max(r1, r2)
            self._c_width = self._r_width / shrink_r
            self._c_height = self._r_height / shrink_r
            newsize = (int(shape[1] * self._c_width * 0.95), int(shape[0] * self._c_height * 0.95))
            self.__frame__ = cv2.resize(self.__frame__, newsize)

        self.__frame__ = cv2.cvtColor(self.__frame__, cv2.COLOR_BGR2RGB)