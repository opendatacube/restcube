# This Dockerfile should follow the Travis configuration process
# available here: https://github.com/opendatacube/datacube-core/blob/develop/.travis.yml

FROM opendatacube/datacube-core:latest

RUN pip3 install -U pip && rm -rf $HOME/.cache/pip

RUN pip3 uninstall -y boto3  && rm -rf $HOME/.cache/pip

RUN pip3 install flask flask-restful gunicorn boto3 requests validators \
  gevent aiobotocore[awscli] celery[redis] furl webargs && rm -rf $HOME/.cache/pip

RUN pip3 install --extra-index-url="https://packages.dea.gadevs.ga" odc-apps-cloud


WORKDIR /opt/odc/restcube
ADD . .

EXPOSE 8000
CMD gunicorn -b "0.0.0.0:8000" "restcube.app:app" 
