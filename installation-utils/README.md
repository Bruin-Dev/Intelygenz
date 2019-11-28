# installation-utils

This folder contains some scripts used as tools for the installation process.

**Table of content:**

+ [Environment files generator](#env_generation)
    - [Description](#env_generation_description)
    - [Usage](#env_generation_usage)

## Environment files generator<a name="env_generation"></a>

### Description <a name="env_generation_description"></a>

The Python [script](./environment_files_generator.py) is used to generate all environment files that are needed to run this project. The script will create each file in its folder, overwriting any existing `env` file.

### Usage <a name="env_generation_usage"></a>

In order to use this [script](./environment_files_generator.py) it is necessary to ask for a private token. Once this is done, run:

```
$ cd installation-utils
$ python3 -m pip install -r requirements.txt
$ python3 environment_files_generator.py <private_token>
```
