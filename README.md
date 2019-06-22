restcube
===========

restcube is a pre-alpha REST API over the OpenDataCube for use with cloud deployments of an OpenDataCube. The API is currently highly unstable and under active development.

## Getting Started
* Requires a running [redis](https://redis.io/) instance. Running a local redis server on `localhost` is sufficient for development and testing.
* Clone the repo `git clone https://github.com/opendatacube/restcube.git`
* Ensure you have a usable datacube configuration file
* Start restcube using flask: `export FLASK_APP=restcube/app.py flask run`
* To use Data Download or Indexing tasks: `celery -A restcube.tasks.indexing.celery worker` and `celery -A restcube.tasks.data.celery worker`
