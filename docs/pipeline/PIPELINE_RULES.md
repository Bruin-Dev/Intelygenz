<div align="center">
<img src="http://photos.prnewswire.com/prnfull/20141022/153661LOGO?p=publish"  width="300" height="120">
</div>

# PIPELINES RULES
## Add new section
To add new section of jobs in the pipeline, we must include the section adding an included in the general .gitlab-ci.yml:
```yaml
include:
  - local: microservices/.gitlab-ci.yml
```
Could be possible that an included .gitlab-ci.yml of another section include more sub-sections(Example microservices):
```yaml
include:
  - local: microservices/fetchers/velocloud/.gitlab-ci.yml
```
We should follow this organization technique to isolate code to their respective area and avoid big files with
spaghetti code.

## Add new template
To add a new template we should take a look in the folder structure:
```yaml
# templates (folder where project templating is going to be saved)
  ## gitlab (section of the templating)
```
Inside gitlab folder we should create template YAML files that fits with a section, for example, for microservices
we created a microservice-ci.yml to store the templates of that section. Same in infrastructure. Also, we should include 
new templates in the index.yml in templates/index.yml
```yaml
include:
  # CI templates
  - local: templates/gitlab/microservice-ci.yml
  - local: templates/gitlab/infrastructure-ci.yml
```
