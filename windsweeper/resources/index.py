from flask_restful import Api, reqparse, abort, Resource
from flask import current_app
from windsweeper.tasks.indexing import send_s3_urls_to_sqs
from windsweeper.resources.tasks import Tasks
import os

postargparser = reqparse.RequestParser()
postargparser.add_argument('pattern', type=str, required=True, help="S3 Pattern to search")
postargparser.add_argument('dc_product', type=str, required=False, help="DC Product to match against")

sqs_url = os.getenv("SQS_QUEUE_URL", "")

class Index(Resource):

    def post(self):
        args = postargparser.parse_args()
        s3_pattern = args['pattern']
        dc_product = args['dc_product']
        if s3_pattern is None:
            abort(400, message="no s3 pattern defined")
        index_task = send_s3_urls_to_sqs.apply_async(args=[s3_pattern, dc_product, sqs_url])
        api = Api
        return "{}", 202, {"Location": api.url_for(api(current_app), Tasks, task_id=index_task.id)}