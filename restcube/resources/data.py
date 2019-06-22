from flask_restful import Resource, request, Api
from flask import current_app
from webargs import fields
from webargs.flaskparser import parser

from restcube.tasks.data import get_data
from restcube.resources.tasks import Task


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
    """
    Data Resource refers to raster data that can be retrieved from the associated datacube.
    """
    def get(self):
        """
        GETs data from the datacube.
        Will create a new data retrieval task
        """
        args = parser.parse(datasets_args, request)
        data_task = get_data.apply_async(kwargs=args)
        api = Api
        return "{}", 202, {"Location": api.url_for(api(current_app), Task, task_id=data_task.id)}