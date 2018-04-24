import logging
import sys
import tkinter as tk

import scipy.spatial.ckdtree
from scipy.linalg import _fblas

from src.app import BehaviorLabeler

LOGGER = logging.getLogger(__name__)


def log_handler(*loggers):
    formatter = logging.Formatter(
        '%(asctime)s %(filename)12s:L%(lineno)3s [%(levelname)8s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    # stream handler
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)

    for logger in loggers:
        logger.addHandler(sh)
        logger.setLevel(logging.DEBUG)


if __name__ == '__main__':
    log_handler(LOGGER)
    BehaviorLabeler()
