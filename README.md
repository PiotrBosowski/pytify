# PyTify

## Setup:


### Bare-metal run:
* make sure to use Python 3

- `python -m venv .venv`
- `source .venv/bin/activate`
- `pip install -r requirements.txt`

* install requirements: `pip install -r requirements.txt` 

* (optionally) modify `settings.py` file
  
* run `python webserver.py`

### Dockerize run:

- `docker build -t "pytify:latest" .`
- `docker run -d -p 5001:5001 --mount type=bind,src=/home/peter/opt/pytify/data,target=/home/.data pytify`

### Ptui!
