from flask_restful import Resource, request

from webargs import fields
from webargs.flaskparser import parser

from restcube.tasks.data import get_data


datasets_args = {
    "product": fields.String(required=False),
    "url": fields.String(required=False),
    "time": fields.DelimitedList(fields.String(), required=False),
    "x": fields.DelimitedList(fields.Float(), required=False),
    "y": fields.DelimitedList(fields.Float(), required=False),
    "crs": fields.String(required=False),
    "measurements": fields.DelimitedList(fields.String(), required=False),
    "output_crs": fields.String(required=False),
    "resolution": fields.DelimitedList(fields.Float(), required=False),
    "align": fields.DelimitedList(fields.Float(), required=False)
}
class Data(Resource):
    def get(self):
        args = parser.parse(datasets_args, request)
        data_task = get_data.apply_async(kwargs=args)

        return data_task.id, 200