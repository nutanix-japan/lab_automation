class Tasks:

  def __init__(self, *_):
    ...

  def get_task_status(self, task_uuid):
    error_dict = {}
    try:
      response_dict = self.get_v08('/tasks/{}'.format(task_uuid), error_dict)
      return_dict = {
        'uuid': response_dict['uuid'],
        'method': response_dict['metaRequest']['methodName'],
        'percent': response_dict.get('percentageComplete', 0),
        'status': response_dict['progressStatus'],
      }
      return (True, return_dict)

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)


  def get_tasks_status(self):
    error_dict = {}
    try:
      response_dict = self.get_v08('/tasks/?includeCompleted=false', error_dict)
      task_list = []
      for entity in response_dict['entities']:
        entity_dict = {
          'uuid': entity['uuid'],
          'method': entity['metaRequest']['methodName'],
          'percent': entity.get('percentageComplete', 0),
          'status': entity['progressStatus'],
        }
        task_list.append(entity_dict)
      return (True, task_list)

    except Exception as exception:
      self.handle_error(exception, error_dict)
      return (False, error_dict)
