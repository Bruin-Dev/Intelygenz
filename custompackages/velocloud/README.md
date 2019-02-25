# Description
Velocloud SDK provided by VMWare. It wraps all the API calls that we need to 
make to the Velocloud clusters, and the authentication for that.

## Changelog (Latest changes on top)
- Increase the velocloud.rest.RESTClientObject http client pool size in order to make multiple concurrent calls. Current value: 10000 

## Run the example script 
- `cd custompackages/velocloud`[If not already here]
- `python3.6 -m venv velocloud-example-env`
- `source velocloud-example-env/bin/activate`
- `pip install -r requirements.txt`
- Copy env.example
- Rename it to env
- Fill env file with credentials you are provided with.
- `source ./env`
- `python example.py`
