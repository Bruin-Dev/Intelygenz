# Welcome Pack

## Team Composition

- Julia - Manager
- Dani - Tech Lead
- Ángel - Devops
- Brandon - Developer
- David - Developer
- Sergio - Developer
- Javier - Developer

## First steps

Please request access to all the things listed below:

- Project repository <https://gitlab.intelygenz.com/mettel/automation-engine/>,
docker repository <https://gitlab.intelygenz.com/mettel/docker_images/-/tree/master> and One password to itcrowd@intelygenz.com through their ticketing system <https://docs.google.com/document/d/1YLYdI9Dyq8tNlNy2iJ29InquKDz8r_Dw4XBsxI7pPiM/edit> and CC your manager to allow the request

- Configure vpn <https://docs.google.com/document/d/16_LFpkiBWN0mbfjAoqR4BaEB5kPNsuNHrUS7PtrWnEA/edit#heading=h.to49i8wu1vn3>

- AWS account creation to our devops

- Jira board to our manager

- Mettel's Slack channels to our tech lead

## Project overview

### Resources

- Check docs folder inside the mettel gitlab project and read carefully the readme for installing all the required programs and configure the project.
- After RRHH's on-boarding our team lead will give an overview of the project <https://docs.google.com/presentation/d/1Y18vXn6lsSp-6pJVsB5swWg7UcTDWYrIYtXq8_brRMk/edit#slide=id.g6183830b53_0_5>

### Project guidelines

- This project uses Black and isort. You just need to install `pip install pre-commit` and then just run `pre-commit run --all-files` on the root folder.
Please check `pre-commit-config.yaml` for more info about it.
- Another option (after adding the project poetry env as interpreter in pycharm) would be running `poetry run black .` and `poetry run isort .` on the root folder, the config options will be taken automatically from `pyproject.toml`. For adding this as autosave option please refer to https://black.readthedocs.io/en/stable/integrations/editors.html
- When updating a git branch please use rebase instead of merge.

### Tools

- k9s <https://k9scli.io/>
- bash-completion
