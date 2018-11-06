import json
from google.auth import default
from google.auth.transport.requests import AuthorizedSession

credentials, projectId = default()
scope_creds = credentials.with_scopes(['https://www.googleapis.com/auth/iam'])
auth_session = AuthorizedSession(scope_creds)



def insert_sa_policies(projectId, db):
    headers = {"Content-Length": 0}
    service_accounts = db.table("Service Account").all()
    for account in service_accounts:
        resp = auth_session.post("https://iam.googleapis.com/v1/projects/" + projectId + "/serviceAccounts/" + account['uniqueId'] + ":getIamPolicy", data={})
        try:
            for policy in resp.json()['bindings']:
                db.table('Service Account').update(
                    add_policy({
                        "permission": policy['role'],
                        "scope": policy['members']
                    }),
                    eids=[account.eid])
        except KeyError:
            pass


# Function to pass Tinydb for the update query
def add_policy(policy):
    def transform(element):
        try:
            element['iam_policies'].append(policy)
        except KeyError:
            element['iam_policies'] = [policy]

    return transform
