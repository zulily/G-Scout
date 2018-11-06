import json
from google.auth import default
from google.auth.transport.requests import AuthorizedSession

credentials, projectId = default()
scope_creds = credentials.with_scopes(['https://www.googleapis.com/auth/iam'])
auth_session = AuthorizedSession(scope_creds)


def insert_service_accounts(projectId, db):
    resp = auth_session.get("https://iam.googleapis.com/v1/projects/" + projectId + "/serviceAccounts/")
    content = resp.json()
    if 'error' in content:
        print("Error calling service account api: %s",
              content['error']['message'])
    else:
        for account in content['accounts']:
            db.table("Service Account").insert(account)


def add_role(role):
    def transform(element):
        try:
            element['roles'].append(role)
        except KeyError:
            element['roles'] = [role]

    return transform


def insert_sa_roles(projectId, db):
    for role in db.table('Role').all():
        for sa in db.table('Service Account').all():
            if "serviceAccount:" + str.split(str(sa['name']), '/')[-1] in role['members']:
                db.table("Service Account").update(
                    add_role(role['role']),
                    eids=[sa.eid])
