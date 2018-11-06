from googleapiclient import discovery
import google.auth

from tinydb import TinyDB

credentials, projectId = google.auth.default()


def insert_entity(projectId, product, categories, table_name, version="v1", prefix="", items="items"):
    db = TinyDB("project_dbs/" + projectId + ".json")
    service = discovery.build(product, version, credentials=credentials)
    while categories:
        api_entity = getattr(service, categories.pop(0))()
        service = api_entity
    request = api_entity.list(project=prefix + projectId)
    try:
        while request is not None:
            response = request.execute()
            for item in response[items]:
                db.table(table_name).insert(item)
            try:
                request = api_entity.list_next(previous_request=request, previous_response=response)
            except AttributeError:
                request = None
    except KeyError:
        pass
