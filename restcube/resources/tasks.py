from flask_restful import Resource
from restcube.tasks import get_task, delete_task, get_all_tasks

class Task(Resource):
    """
    The Task Resource is for management of tasks created by the restcube
    """
    def get(self, task_id):
        """
        GETs information about a task given its id
        """
        return get_task(task_id), 200

    def delete(self, task_id):
        """
        Attempts to stop and deleted a task given its id
        """
        delete_task(task_id)


class Tasks(Resource):

    def get(self):
        """
        Retrieves all tasks which are visible to the restcube
        """
        return get_all_tasks(), 200