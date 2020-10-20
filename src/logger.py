import os
from pathlib import Path
import shutil

class Logger:
    enable_debug = False
    logs_dir = None

    def __init__(self):
        pass
        
    def setup(self, log_path, enable_debug):
        self.log_file = open(log_path, 'w+')
        self.enable_debug = enable_debug

    def info(self, string):
        output = "[INFO] {}".format(string)
        print(output)
        self.log_file.write(output + "\n")

    def warn(self, string):
        output = "[WARNING] {}".format(string)
        print(output)
        self.log_file.write(output + "\n")

    def error(self, string):
        output = "[ERROR] {}".format(string)
        print(output)
        self.log_file.write(output + "\n")

    def debug(self, string):
        if not self.enable_debug:
            return
        output = "[DEBUG] {}".format(string)
        print(output)
        self.log_file.writelines(output + "\n")


LOGS_DIR = "/tmp/log/mct"
log = Logger()


def setup_logs(logs_dir, deployment_id, enable_debug):
    global LOGS_DIR
    global log

    if logs_dir:
        LOGS_DIR = logs_dir
    if deployment_id:
        LOGS_DIR = os.path.join(LOGS_DIR, deployment_id)

    if os.path.isdir(LOGS_DIR):
        shutil.rmtree(LOGS_DIR)
    os.makedirs(LOGS_DIR, exist_ok=True)

    print("Log Directory: {}".format(LOGS_DIR))
    log.logs_dir = LOGS_DIR
    log.setup(os.path.join(LOGS_DIR, "main.log"), enable_debug)