from flask_restful import Resource
from windsweeper.factory import make_celery
from celery.result import AsyncResult

class Tasks(Resource):

    def get(self, task_id):
        task = AsyncResult(task_id, app=make_celery())
        if not task:
            return '{"error": "Error finding task"}', 500
        if task.state == "PENDING":
            response = {
                "state": task.state,
                "processed": 0,
            }
        elif task.state != "FAILURE":
            response = {
                "state": task.state,
                "processed": task.info.get("count"),
                "last_processed": task.info.get("last_processed")
            }
        else:
            response = {
                "state": task.state,
                # "processed": task.info.get("count"),
                # "last_processed": task.info.get("last_processed"),
                "error": str(task.info)
            }
        return response, 200


    def delete(self, task_id):
        make_celery().control.revoke(task_id, terminate=True)