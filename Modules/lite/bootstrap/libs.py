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
import inspect
import logging
import functools

from pathlib import Path
from operator import itemgetter
from urllib.parse import unquote
from types import SimpleNamespace
from collections import deque, defaultdict
from tkinter import ttk, scrolledtext, filedialog, messagebox

import psutil
import pyperclip
