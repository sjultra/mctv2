#!/bin/bash

# This script is created to prepare the environment for MCTv2 excution
# Tested on Ubuntu 16.04
# It does not require any parameters

set -xe

TERRAFORM_URL="https://releases.hashicorp.com/terraform/0.12.24/terraform_0.12.24_linux_amd64.zip"
PIP_URL="https://bootstrap.pypa.io/get-pip.py"

function install_dependencies {
    apt update -y
    apt install -y python3 python3-distutils wget git nano unzip curl

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

function main {
    echo "testi"
    install_dependencies

    install_terraform
    prepare_python_env
}

main $@
