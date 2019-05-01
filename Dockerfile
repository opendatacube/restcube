FROM opendatacube/datacube-core:latest

RUN pip3 install -U pip && rm -rf $HOME/.cache/pip

RUN pip3 uninstall -y boto3  && rm -rf $HOME/.cache/pip

RUN pip3 install flask flask-restful gunicorn boto3 requests validators gevent aiobotocore[awscli] celery[redis] furl && rm -rf $HOME/.cache/pip

RUN pip3 install 'git+https://github.com/opendatacube/dea-proto.git' && rm -rf $HOME/.cache/pip

RUN pip3 install 'git+https://github.com/opendatacube/dea-proto.git#egg=odc_apps_cloud&subdirectory=apps/cloud'


WORKDIR /opt/odc/restcube
ADD . .

CMD gunicorn -b "0.0.0.0:8000" "restcube.app:app"