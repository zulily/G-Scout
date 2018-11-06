import datetime
import json

from google.auth import default
from google.auth.transport.requests import AuthorizedSession

credentials, projectId = default()
scope_creds = credentials.with_scopes(['https://www.googleapis.com/auth/iam'])
auth_session = AuthorizedSession(scope_creds)


def insert_service_account_keys(projectId, db):
    service_accounts = db.table("Service Account").all()
    for sa in service_accounts:
        sa_keys = list_service_account_keys(sa, projectId)
        for sa_key in sa_keys:
            db.table('Service Account').update(
                add_key({
                    "keyAlgorithm": sa_key['keyAlgorithm'],
                    "validBeforeTime": sa_key['validBeforeTime'],
                    "validAfterTime": sa_key['validAfterTime']
                }),
                eids=[sa.eid])


def list_service_account_keys(sa, projectId):
    resp = auth_session.get("https://iam.googleapis.com/v1/projects/" + projectId + "/serviceAccounts/" + sa['uniqueId'] + "/keys")
    return resp.json()['keys']


# Function to pass Tinydb for the update query
def add_key(key):
    def transform(element):
        try:
            element['keys'].append(key)
        except KeyError:
            element['keys'] = [key]

    return transform


def key_is_old(key):
    creation_date = datetime.datetime.strptime(key['validAfterTime'][:10], "%Y-%m-%d")
    if creation_date < datetime.datetime.now() - datetime.timedelta(days=90):
        return True
    return False
