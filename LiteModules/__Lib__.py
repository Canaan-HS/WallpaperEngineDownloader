import os
import sys
import shutil
import atexit
import platform
import traceback
import threading
import subprocess
import tkinter as tk

import re
import json
import time
import base64
import locale
import ctypes
import logging

from pathlib import Path
from operator import itemgetter
from urllib.parse import unquote
from types import SimpleNamespace
from collections import defaultdict
from tkinter import ttk, scrolledtext, filedialog, messagebox

import psutil
import pyperclip

SysPlat = platform.system()


def Elapsed_Time(stime=None, lable=""):
    """
    stime = Elapsed_Time()
    run code ...
    Elapsed_Time(stime, "code name")
    """
    if stime is None:
        return time.perf_counter()
    print(f"{lable} Elapsed: {time.perf_counter() - stime} s".strip())
