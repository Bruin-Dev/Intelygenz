variable "builder_instance_type" {
  type    = string
  default = "m5.large"
}

variable "builder_launch_block_device_mappings_delete_on_termination" {
  type    = string
  default = true
}

variable "builder_launch_block_device_mappings_device_name" {
  type    = string
  default = "/dev/sda1"
}

variable "builder_launch_block_device_mappings_volume_size" {
  type    = string
  default = "30"
}

variable "builder_launch_block_device_mappings_volume_type" {
  type    = string
  default = "gp2"
}

variable "builder_region" {
  type    = string
  default = "us-west-1"
}

variable "builder_skip_create_ami" {
  type    = bool
  default = true
  # default = false
}


variable "builder_ssh_username" {
  type    = string
  default = "ubuntu"
}

variable "builder_type" {
  type    = string
  default = "amazon-ebs"
}

variable "source_ami_filter_most_recent" {
  type    = string
  default = true
}

variable "source_ami_filter_name" {
  type = string
  default = "*ubuntu-bionic-18.04-amd64-pro-serv-*"
  # default = "mettel-fips-20221028092720"
}

variable "source_ami_filter_owners" {
  type    = string
  default = "679593333241"
  # default = "374050862540"
}

variable "source_ami_filter_root_device_type" {
  type    = string
  default = "ebs"
}

variable "source_ami_filter_virtualization_type" {
  type    = string
  default = "hvm"
}

variable "username" {
  type    = string
  default = "ubuntu"
}

variable "version" {
  type    = string
  default = "1.0.0"
}

variable "ECR_REPOSITORY_NAME" {
  type    = string
  default = env("ECR_REPOSITORY_NAME")
}

variable "ECR_REPOSITORY_URL" {
  type    = string
  default = env("ECR_REPOSITORY_URL")
}

variable "ECR_REPOSITORY_TAG" {
  type    = string
  default = env("ECR_REPOSITORY_TAG")
}

variable "PACKER_DIR_MODULE" {
  type    = string
  default = env("PACKER_DIR_MODULE")
}

variable "AWS_ACCESS_KEY_ID" {
  type    = string
  default = env("AWS_ACCESS_KEY_ID")
}

variable "AWS_SECRET_ACCESS_KEY" {
  type    = string
  default = env("AWS_SECRET_ACCESS_KEY")
}

data "amazon-ami" "fedramp" {
  filters = {
    name                = "${var.source_ami_filter_name}"
    root-device-type    = "${var.source_ami_filter_root_device_type}"
    virtualization-type = "${var.source_ami_filter_virtualization_type}"
  }
  most_recent = "${var.source_ami_filter_most_recent}"
  owners      = ["${var.source_ami_filter_owners}"]
  region      = "${var.builder_region}"
}


locals { 
  timestamp = regex_replace(timestamp(), "[- TZ:]", "")
  builder_ami_name = "mettel-fips-${local.timestamp}"

}

source "amazon-ebs" "fedramp" {
  ami_name      = "${local.builder_ami_name}"
  instance_type = "${var.builder_instance_type}"
  launch_block_device_mappings {
    delete_on_termination = "${var.builder_launch_block_device_mappings_delete_on_termination}"
    device_name           = "${var.builder_launch_block_device_mappings_device_name}"
    volume_size           = "${var.builder_launch_block_device_mappings_volume_size}"
    volume_type           = "${var.builder_launch_block_device_mappings_volume_type}"
  }
  region          = "${var.builder_region}"
  skip_create_ami = "${var.builder_skip_create_ami}"
  source_ami      = "${data.amazon-ami.fedramp.id}"
  ssh_username    = "${var.username}"

  temporary_iam_instance_profile_policy_document {
      Statement {
          Action   = ["ecr:*"]
          Effect   = "Allow"
          Resource = ["*"]
      }
      Version = "2012-10-17"
  }
}

build {
  sources = ["source.amazon-ebs.fedramp"]

  provisioner "shell" {
    environment_vars = ["DEBIAN_FRONTEND=noninteractive"]
    inline = [
      "echo '** Create fips-enabled packages directory **'",
      "sudo mkdir -p /app/ubuntu18-fips/packages",
      "sudo chmod -R 777 /app"
    ]
    inline_shebang = "/bin/bash -xe"
  }

  provisioner "file" {
    destination = "/app/"
    sources      = [
      "${var.PACKER_DIR_MODULE}"
    ]
  }

  provisioner "shell" {
    environment_vars = ["DEBIAN_FRONTEND=noninteractive"]
    inline = [
      "echo '** Enable Ubuntu Pro services **'",
      "sudo killall apt-get",
      "ls -al /app",
      "sudo apt-get update && sudo apt-get upgrade -yq",
      "echo '** Enabling UA services already enabled will cause the pipeline to fail **'",
      "sudo pro enable cc-eal cis fips --assume-yes",
    ]
    inline_shebang = "/bin/bash -xe"
  }

  provisioner "shell" {
    environment_vars = ["DEBIAN_FRONTEND=noninteractive"]
    inline = [
      "echo '** Rebooting VM so the patched kernel aws-fips runs **'",
      "sudo reboot",
    ]
    inline_shebang    = "/bin/bash -xe"
    expect_disconnect = true
  }

  provisioner "shell" {
    environment_vars = ["DEBIAN_FRONTEND=noninteractive"]
    inline = [
      "echo '** Reinstall fips-enabled packages and install new ones **'",
      "echo '** List of additional packages **'",
      "echo '** libssl-dev **'",
      "sudo apt-get clean",
      <<-EOF
      sudo apt-get install -yq --reinstall --download-only \
        openssh-client openssh-client-hmac openssh-server \
        openssh-server-hmac strongswan strongswan-hmac \
        openssh-sftp-server libssl-dev libstrongswan libstrongswan-standard-plugins \
        strongswan-starter strongswan-libcharon strongswan-charon \
        openssl libssl1.1 libssl1.1-hmac kcapi-tools libkcapi1
      EOF
    ]
    inline_shebang = "/bin/bash -xe"
  }

  provisioner "shell" {
    environment_vars = ["DEBIAN_FRONTEND=noninteractive"]
    inline = [
      "echo '** Copy those deb packages to your build directory **'",
      "sudo cp /var/cache/apt/archives/*.deb /app/ubuntu18-fips/packages/",
    ]
    inline_shebang = "/bin/bash -xe"
  }


  provisioner "shell" {
    environment_vars = ["DEBIAN_FRONTEND=noninteractive"]
    inline = [
      "echo '** Rebooting VM to ensure dpkg is unlocked **'",
      "sudo reboot",
    ]
    inline_shebang    = "/bin/bash -xe"
    expect_disconnect = true
  }

  provisioner "shell" {
    environment_vars = ["DEBIAN_FRONTEND=noninteractive"]
    inline = [
      "echo '** Install mandatory packages **'",
      "sudo apt-get install -yq git golang build-essential curl libssl-dev libffi-dev python3-dev python3-pip unzip",
      "sudo -H python3 -m pip install --user --upgrade pip",
      "sudo -H python3 -m pip install setuptools wheel cryptography",
      "sudo -H python3 -m pip install ansible==4.10.0",
      "curl -s 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o 'awscliv2.zip'",
      "unzip -qq awscliv2.zip",
      "sudo ./aws/install",
      "export AWS_ACCESS_KEY_ID=${var.AWS_ACCESS_KEY_ID}",
      "export AWS_SECRET_ACCESS_KEY=${var.AWS_SECRET_ACCESS_KEY}",
      "git clone --depth 1 --branch ${var.ECR_REPOSITORY_TAG} https://github.com/kubernetes/ingress-nginx.git",
      "cd ingress-nginx",
      "make build",
      "cd ..",
    ]
    inline_shebang = "/bin/bash -xe"
  }

  provisioner "ansible-local" {
    extra_arguments = [
      "--extra-vars", "ecr_repository_uri=${var.ECR_REPOSITORY_URL}",
      "--extra-vars", "ecr_repository_name=${var.ECR_REPOSITORY_NAME}",
      "--extra-vars", "ecr_repository_tag=${var.ECR_REPOSITORY_TAG}",
    ]
    command = "ANSIBLE_ROLES_PATH=/app/ansible/roles ansible-playbook"
    galaxy_collections_path = "/app/ansible/ansible_collections"
    galaxy_command = "ansible-galaxy"
    galaxy_file = "./ansible/ansible_galaxy/requirements.yaml"
    role_paths = ["./ansible/roles"]
    playbook_file = "./ansible/playbook.yaml"
  }
}
