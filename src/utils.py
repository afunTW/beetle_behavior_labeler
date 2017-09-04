import cv2
import numpy as np
from PIL import Image, ImageTk

COLOR = [(50, 205, 50), (255, 191, 0), (0, 255, 255), (0, 165, 255), (211, 85, 186), (255, 102, 255), (255, 255, 0), (0, 0, 0), (100, 10, 255), (255, 255, 255)]
class Utils(object):

    def draw(self):
        self.__frame__ = self.__orig_frame__.copy()
        if self.video_path is not None:
            for i, (k, v) in enumerate(self.__trajectory__.items()):
                nframe = v['n_frame']
                traj = v['path']
                wh = v['wh']
                c = COLOR[i]
                try:
                    ind = nframe.index(self.n_frame)
                    x_c, y_c = tuple(traj[ind])
                    w, h = tuple(wh[ind])
                    xmin, xmax = int(x_c - w/2.0), int(x_c + w/2.0)
                    ymin, ymax = int(y_c - h/2.0), int(y_c + h/2.0)
                    cv2.rectangle(self.__frame__, (xmin, ymin), (xmax, ymax), c, 1)

                    if ymin < 50:
                        y_t = ymax + 20
                    else:
                        y_t = ymin - 10

                    if xmin < 50:
                        x_t = xmax + 20
                    else:
                        x_t = xmin - 10

                    cv2.putText(self.__frame__, k, (x_t, y_t), cv2.FONT_HERSHEY_TRIPLEX, 0.8, (255, 255, 255), 3)
                    cv2.putText(self.__frame__, k, (x_t, y_t), cv2.FONT_HERSHEY_TRIPLEX, 0.8, c, 1)
                except Exception as e:
                    pass

        if self.parent.state() == 'zoomed':
            shape = self.__frame__.shape
            r1 = (shape[1] / self.parent.winfo_screenwidth())
            r2 = (shape[0] / self.parent.winfo_screenheight())
            shrink_r = max(r1, r2)
            self._c_width = self._r_width / shrink_r
            self._c_height = self._r_height / shrink_r
            nw = int(shape[1] * self._c_width)
            nh = int(shape[0] * nw / shape[1])
            newsize = (nw, nh)
            self.__frame__ = cv2.resize(self.__frame__, newsize)

        self.__frame__ = cv2.cvtColor(self.__frame__, cv2.COLOR_BGR2RGB)