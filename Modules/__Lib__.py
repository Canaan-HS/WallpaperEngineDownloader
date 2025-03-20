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

from pathlib import Path
from urllib.parse import unquote
from types import SimpleNamespace
from collections import defaultdict
from tkinter import ttk, scrolledtext, filedialog, messagebox

import psutil
import pyperclip

SysPlat = platform.system()