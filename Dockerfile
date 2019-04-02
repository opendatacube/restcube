FROM opendatacube/datacube-core:latest

RUN pip3 install flask flask-restful gunicorn && rm -rf $HOME/.cache/pip

WORKDIR /opt/odc/windsweeper
ADD . .

CMD gunicorn -b "0.0.0.0:8000" "windsweeper.app:app"