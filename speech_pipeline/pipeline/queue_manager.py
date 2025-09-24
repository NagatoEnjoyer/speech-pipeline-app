import threading
import uuid
import logging

tasks = {}

def run_task(task_id, func, *args, **kwargs):
    try:
        tasks[task_id]["status"] = "processing"
        result = func(*args, **kwargs)
        tasks[task_id]["status"] = "done"
        tasks[task_id]["result"] = result
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["result"] = str(e)

def add_task(func, *args, **kwargs):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "queued", "result": None}

    thread = threading.Thread(target=run_task, args=(task_id, func, *args), kwargs=kwargs)
    thread.start()

    return task_id

def get_task_status(task_id):

    return tasks.get(task_id)
