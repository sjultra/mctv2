from python_terraform import Terraform, IsFlagged
from backend import get_backend_provider
from logger import log, artifact
from utils import stage
import json


class TerraformProvider():
    def __init__(self, configuration, terraform_workspace):
        log.info("Preparing terraform deployment")
        log.debug("Using workspace: {}".format(terraform_workspace))

        self._backend_provider = get_backend_provider(configuration, terraform_workspace)
        self._controller = Terraform(working_dir=terraform_workspace, 
                                     variables=configuration["terraform"]["parameters"])

        self._controller.init(capture_output=False, force_copy=IsFlagged)

    @stage("Terraform deploy")
    def deploy(self):
        log.info("Deploying terraform infrastructure")
        
        self._backend_provider.init_remote_backend()
        self._controller.apply(capture_output=False, skip_plan=True)
        output = self._controller.output()
        artifact.create("terraform_output", content=json.dumps(output))


    def destroy(self):
        log.info("Destroying terraform infrastructure")

        self._controller.destroy(capture_output=False)
        self._backend_provider.remove_remote_backend()


