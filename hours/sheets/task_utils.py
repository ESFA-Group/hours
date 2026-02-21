import json
import os
from django.conf import settings

STATUS_DIR = os.path.join(settings.MEDIA_ROOT, 'task_status')

def ensure_status_dir():
    if not os.path.exists(STATUS_DIR):
        os.makedirs(STATUS_DIR)

def get_task_status_path(task_id):
    ensure_status_dir()
    return os.path.join(STATUS_DIR, f"{task_id}.json")

def set_task_status(task_id, status, message="", data=None):
    path = get_task_status_path(task_id)
    with open(path, 'w') as f:
        json.dump({
            'status': status,
            'message': message,
            'data': data or {}
        }, f)

def get_task_status(task_id):
    path = get_task_status_path(task_id)
    if not os.path.exists(path):
        return {'status': 'not_found', 'message': 'Task not found'}
    with open(path, 'r') as f:
        return json.load(f)

def is_any_task_running():
    ensure_status_dir()
    for filename in os.listdir(STATUS_DIR):
        if filename.endswith('.json'):
            path = os.path.join(STATUS_DIR, filename)
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    if data.get('status') == 'running':
                        return True
            except:
                continue
    return False

def clear_old_tasks():
    # Simple cleanup can be added here if needed
    pass
