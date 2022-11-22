<div align="center">
<img src="http://photos.prnewswire.com/prnfull/20141022/153661LOGO?p=publish"  width="300" height="120">
</div>

# Setting up pipelines

## Adding new jobs

To add new jobs, we must include them using the `include` directive in the project's root `.gitlab-ci.yml`:

```yaml
include:
  - local: microservices/.gitlab-ci.yml
```

Also, `.gitlab-ci.yml` files can reference `.gitlab-ci.yml` files that exist in a directory that has its own `.gitlab-ci.yml`.

For example, this one references a configuration exclusive to a particular service within the `microservices` folder, for whom
we included its own `.gitlab-ci.yml` in the previous snippet:
```yaml
include:
  - local: microservices/fetchers/velocloud/.gitlab-ci.yml
```

By following this approach we are able to isolate code to the appropriate place, and ultimately avoid huge files with
spaghetti code, which are harder to maintain.

## Adding new templates

Before adding a new template that other `.gitlab-ci.yml` files can inherit definitions from, we need to take a look at
the folder structure:

```
templates    -> folder holding every single template in the project
  |- gitlab  -> folder holding GitLab templates
```

To add a new template, we must add `yml` files to the `gitlab` folder, and make sure their name makes clear which kind
of templates we are going to find there.

For example, if we need a place to store templates for microservices, we should create a `microservice-ci.yml` file.
Same applies for infrastructure: we would need file named `infrastructure-ci.yml`.
```yaml
include:
  # CI templates
  - local: templates/gitlab/microservice-ci.yml
  - local: templates/gitlab/infrastructure-ci.yml
```

To ease referencing any kind of template, we should have a central `index.yml` file where all templates are included.
The folder structure would then look like this:
```
/templates
   |- /gitlab
   |- index.yml
```

`index.yml` contents should look like this:
```yaml
include:
  - local: 'gitlab/**/*.yml'
```
