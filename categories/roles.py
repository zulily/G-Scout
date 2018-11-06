import json

from googleapiclient import discovery, errors
import google.auth

credentials, projectId = google.auth.default()

service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)


def insert_roles(projectId, db):
    try:
        content = service.projects().getIamPolicy(body={},resource=projectId).execute()
    except errors.HttpError as httperr:
        print("Error fetching roles: %s", str(httperr))
        content = None
    for role in content['bindings']:
        db.table('Role').insert(role)
