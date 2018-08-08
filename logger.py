class Logger():
    """
    Simple logger that print informations in console
    """
    def __init__(self, parent, enable=True):
        """
        Param: parent: The component's name that is currently using the logger
        Param: enable: Enabled the logger, False will not print on console
        """
        self.parent = parent
        self.enable = enable

    def log(self, msg):
        "Param: msg: Can be either str or list"
        if self.enable:
            if isinstance(msg, str):
                print("[" + self.parent + "]>>>>>", msg, "<<<<<")
            else:
                print("[" + self.parent + "]>>>>>")
                for m in msg:
                    print(m)
                print("<<<<<")

    def span(self):
        "Separate logs"
        print("========================= END =========================")
