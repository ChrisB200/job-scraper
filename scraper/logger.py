class Logger:
    def __init__(self, mode):
        self.mode = mode

    def info(self, message):
        if self.mode == "info":
            print(f"INFO: {message}")

    def debug(self, message):
        if self.mode == "debug":
            print(f"DEBUG: {message}")

    def warning(self, message):
        if self.mode == "warning":
            print(f"WARNING: {message}")

    def exception(self, message):    
        print(f"EXCEPTION RAISED: {message}")

    def change_mode(self, mode):
        self.mode = mode