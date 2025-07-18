from ..bootstrap import base64

account_dict = {
    key: {key: base64.b64decode(value).decode("utf-8")}
    for key, value in {
        "ruiiixx": "UzY3R0JUQjgzRDNZ",
        "premexilmenledgconis": "M3BYYkhaSmxEYg==",
        "vAbuDy": "Qm9vbHE4dmlw",
        "adgjl1182": "UUVUVU85OTk5OQ==",
        "gobjj16182": "enVvYmlhbzgyMjI=",
        "787109690": "SHVjVXhZTVFpZzE1",
    }.items()
}

account_list = list(account_dict.keys())
