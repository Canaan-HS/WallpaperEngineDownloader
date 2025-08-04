from ..bootstrap import messagebox
from ..core import shared


class UI_Operat:
    """
    後端與 UI 的交互操作, 由 ui_main 分離出來
    """

    def __init__(self):
        # 目前只用於顯示 請求速度
        shared.msg.connect(
            lambda speed="": self.title(
                f"{self.win_title} （{speed}）" if speed.strip() else self.win_title
            ),
            "title_change",
        )

        shared.msg.connect(
            lambda title, message: messagebox.showerror(title, message, parent=self),
            "showerror",
        )

        shared.msg.connect(self.ui_close)
        shared.msg.connect(self.input_operat)
        shared.msg.connect(self.console_insert)
        shared.msg.connect(self.button_state_change)

    def ui_close(self, account, application, tasks):
        shared.save_config(
            {
                "Language": shared.set_lang,
                "Account": account,
                "Application": application,
                "Extract_Pkg": shared.enable_extract_pkg,
                "window_x": self.winfo_x(),
                "window_y": self.winfo_y(),
                "window_width": self.winfo_width(),
                "window_height": self.winfo_height(),
                "Tasks": tasks,
            }
        )

        self.destroy()

    def console_insert(self, message: str, *args):
        self.console.config(state="normal")
        self.console.insert("end", message, *args)
        self.console.yview("end")
        self.console.config(state="disabled")

    def button_state_change(self, state, cursor):
        self.merge_button.config(state=state, cursor=cursor)
        self.run_button.config(state=state, cursor=cursor)

    def input_operat(self, operat: str, *args):
        if operat == "insert":
            self.input_text.insert("end", *args)
            self.input_text.yview("end")
            self.input_text.xview_moveto(1.0)
            self.input_text.update_idletasks()
        elif operat == "delete":
            self.input_text.delete(*args)
        elif operat == "get":
            return self.input_text.get(*args).splitlines()

    def search_operat(self):
        # 文本緩存, 用於當取消焦點狀態 且 serverid 內容為空時, 重新填充
        self.text_cache = ""

        def on_input(event):
            widget = event.widget
            suffix = widget.get().lower()  # 忽略大小寫
            widget.configure(values=self.search_list(suffix))

        def on_click(event):
            if self.searcher is None:
                self.after(100, self.build_searcher)

            x = event.x
            widget = event.widget
            text = self.serverid_var.get()

            if x < widget.winfo_width() - 20 and "->" in text:
                text = self.clean_text(text)
                self.serverid_var.set(text)
                widget.unbind("<Button-1>")

            self.text_cache = text

        def on_select(event):
            self.text_cache = self.serverid_var.get()
            event.widget.configure(values=self.app_list)

        def of_select(_):
            if self.serverid_var.get().strip() == "":
                self.serverid_var.set(self.text_cache)

        self.serverid_menu.bind("<KeyRelease>", on_input)
        self.serverid_menu.bind("<Button-1>", on_click)
        self.serverid_menu.bind("<FocusOut>", of_select)
        self.serverid_menu.bind("<<ComboboxSelected>>", on_select)
