#!/bin/bash

# This script is created to prepare the environment for MCTv2 excution
# Tested on Ubuntu 16.04
# It does not require any parameters

set -xe

TERRAFORM_URL="https://releases.hashicorp.com/terraform/0.12.24/terraform_0.12.24_linux_amd64.zip"
PIP_URL="https://bootstrap.pypa.io/get-pip.py"

function install_dependencies {
    apt update -y
    apt install -y python3 python3-distutils wget git nano unzip curl apt-transport-https ca-certificates gnupg

    wget "$PIP_URL" -O /tmp/get-pip.py
    python3 /tmp/get-pip.py

    curl -sL https://aka.ms/InstallAzureCLIDeb | bash
}

function install_terraform {
    wget $TERRAFORM_URL -O /tmp/terraform.zip
    unzip /tmp/terraform.zip -d /tmp/terraform_bin

    mv /tmp/terraform_bin/terraform /usr/bin
}

function prepare_python_env {
    pip install python-terraform azure.identity azure-keyvault-secrets
}

function prepare_inspec_env {
    # Install Inspec
    curl https://omnitruck.chef.io/install.sh | bash -s -- -P inspec

    # Install GCP sdk
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
    apt-get update && apt-get install google-cloud-sdk
}

function main {
    install_dependencies

    install_terraform
    prepare_python_env
    prepare_inspec_env
}

main $@
