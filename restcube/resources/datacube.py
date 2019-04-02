from flask_restful import Resource

import datacube
import re

class Datacube(Resource):

    def get(self):
        with datacube.Datacube() as dc:
            connstr = str(dc)
            print(connstr)
            matches = re.search("postgresql.+/(.+)\\)>>>", connstr)
            return {"name": matches.group(1)}, 200
