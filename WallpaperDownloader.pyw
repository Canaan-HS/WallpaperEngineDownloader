from Modules import *

class Controller(DLL, tk.Tk, Backend, GUI):
    def __init__(self, current_dir):
        DLL.__init__(self, current_dir)
        tk.Tk.__init__(self)
        Backend.__init__(self)
        GUI.__init__(self)

        self.protocol("WM_DELETE_WINDOW", self.Closure)
        self.mainloop()

if __name__ == "__main__":
    Controller(
        Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
    )