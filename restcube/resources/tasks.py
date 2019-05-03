from flask_restful import Resource
from restcube.tasks import get_task, delete_task, get_all_tasks

class Task(Resource):

    def get(self, task_id):
        return get_task(task_id), 200

    def delete(self, task_id):
        delete_task(task_id)


class Tasks(Resource):

    def get(self):
        return get_all_tasks(), 200