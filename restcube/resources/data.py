from flask_restful import Resource, request

from webargs import fields
from webargs.flaskparser import parser

from restcube.tasks.data import get_data


datasets_args = {
    "product": fields.Str(required=False),
    "url": fields.Str(required=False),
    "time": fields.DelimitedList(fields.Str(), required=False),
    "x": fields.DelimitedList(fields.Float(), required=False),
    "y": fields.DelimitedList(fields.Float(), required=False),
    "crs": fields.Str(required=False),
    "measurements": fields.DelimitedList(fields.Str(), required=False)
}
class Data(Resource):
    def get(self):
        args = parser.parse(datasets_args, request)
        data_task = get_data.apply_async(kwargs=args)

        return data_task.id, 200