from ..bootstrap import base64

# ! 為了簡化語法, 將格式改為 {key: {key: value}}
account_dict = {
    key: {key: base64.b64decode(value).decode("utf-8")}
    for key, value in {
        "adgjl1182": "UUVUVU85OTk5OQ==",
    }.items()
}

# 判斷觸發 QR 登錄, 與登入後標記
QR_KEY = "QRCodeLogin"
LOGIN_KEY = "-remember-password"

account_dict = {QR_KEY: {QR_KEY: ""}, **account_dict}
account_list = list(account_dict.keys())


def add_login_account(account):
    account_dict.update({account: {account: LOGIN_KEY}})
    account_list.clear()
    account_list.extend(account_dict.keys())
