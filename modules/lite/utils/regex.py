from ..bootstrap import re

illegal_regex = re.compile(r'[<>:"/\\|?*\x00-\x1F]')
parse_regex = re.compile(r"(\d{8,10})(?:&searchtext=(.*))?")
link_regex = re.compile(r"^https://steamcommunity\.com/sharedfiles/filedetails/\?id=\d+.*$")
