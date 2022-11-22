  provisioner "shell" {
    environment_vars = ["DEBIAN_FRONTEND=noninteractive"]
    inline = [
      "echo '** Install Ansible requirements **'",
      "ansible-galaxy role install -r /app/ansible/requirements.yaml",
      "ansible-galaxy collection install -r /app/ansible/requirements.yaml"
    ]
    inline_shebang = "/bin/bash -xe"
  }

  provisioner "ansible-local" {
    extra_arguments = [
      "--extra-vars", "ecr_repository_uri=${var.ECR_REPOSITORY_URI}",
      "--extra-vars", "ecr_repository_name=${var.ECR_REPOSITORY_NAME}",
      "--extra-vars", "ecr_repository_tag=${var.ECR_REPOSITORY_TAG}",
    ]
    galaxy_file = "./ansible/requirements.yaml"
    playbook_file = "./ansible/playbook.yaml"
  }