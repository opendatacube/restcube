from celery.result import AsyncResult
from celery import current_app
from restcube.factory import make_celery

celery = make_celery()

def get_all_tasks():
    all_tasks = celery.tasks
    return all_tasks

def get_task(task_id):
    task = AsyncResult(task_id, app=celery)
    if not task:
        return '{"error": "Error finding task"}', 500
    print(task)
    if task.state == "PENDING":
        response = {
            "state": task.state,
            "task_data": task.info
        }
    elif task.state != "FAILURE":
        response = {
            "state": task.state,
            "task_data": task.info
        }
    else:
        response = {
            "state": task.state,
            # "processed": task.info.get("count"),
            # "last_processed": task.info.get("last_processed"),
            "error": str(task.info)
        }
    return response

def delete_task(task_id):
    celery.control.revoke(task_id, terminate=True)