from ..bootstrap import re

ILLEGAL_REGEX = re.compile(r'[<>:"/\\|?*\x00-\x1F]')
PARSE_REGEX = re.compile(r"(\d{8,10})(?:&searchtext=(.*))?")
LINK_REGEX = re.compile(r"^(?:https://steamcommunity\.com/sharedfiles/filedetails/\?id=\d{8,10}.*|\d{8,10})$")
