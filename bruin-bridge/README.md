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