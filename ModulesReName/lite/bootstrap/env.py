from .libs import sys, logging, platform

SysPlat = platform.system()
IsFrozen = getattr(sys, "frozen", False)

LogConfig = {
    "level": logging.DEBUG,
    "format": "%(asctime)s - %(levelname)s: %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S",
    "force": True,
}
