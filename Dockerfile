FROM opendatacube/datacube-core:latest

RUN pip3 install -U pip && rm -rf $HOME/.cache/pip

RUN pip3 uninstall -y boto3  && rm -rf $HOME/.cache/pip

RUN pip3 install flask flask-restful gunicorn boto3 requests validators gevent aiobotocore[awscli] celery[redis] && rm -rf $HOME/.cache/pip

RUN pip3 install 'git+https://github.com/opendatacube/dea-proto.git' && rm -rf $HOME/.cache/pip

RUN pip3 install 'git+https://github.com/opendatacube/dea-proto.git#egg=odc_apps_cloud&subdirectory=apps/cloud'


WORKDIR /opt/odc/windsweeper
ADD . .

CMD gunicorn -b "0.0.0.0:8000" "windsweeper.app:app"