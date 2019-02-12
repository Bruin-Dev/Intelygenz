# Getting started
- Install python 3
- Install pip for python 3
- Install virtualenv for python 3

Then create and activate the virtualenv like this:
````
python3 -m venv env
source ./env/bin/activate
pip install -r requirements.txt
````

# Adding new libraries to the project

With virtualenv activated

````
pip install some-package
pip freeze | grep -v "pkg-resources" > requirements.txt #The grep -v is needed only if you use Ubuntu due a harmless bug
````
Remember to commit the new requirements.txt file


# Fast development in local environment

- Go to project root
- Type the following ``docker-compose up nats-streaming``
- [JUST ONCE] Go to /etc/hosts and add ``127.0.0.1	nats-streaming``

Now you can execute your python code related to NATS connections, using nats-streaming as host name