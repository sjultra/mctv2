import subprocess
import os


class ScriptExecutor():
    def __init__(self, config):
        self._config = config
        self._check_script()

    def _check_script(self):
        if not self._config["path"]:
            raise Exception("script path is empty")
        self._config["path"] = os.path.abspath(self._config["path"])

        if not os.path.isfile(self._config["path"]):
            raise Exception("File {} does not exist".format(self._config["path"]))

    def exec(self):
        command = "bash {0} {1}".format(self._config["path"], self._config["parameters"])
        print("Executing command: {0}".format(command))

        try:
            subprocess.check_call(command, shell=True)
        except subprocess.CalledProcessError as error:
            print("Warning: command exited with error code: {0}".format(error.returncode))
            return error.returncode
        finally:
            return 0
