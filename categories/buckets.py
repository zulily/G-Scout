from googleapiclient import discovery, errors
import google.auth

credentials, projectId = google.auth.default()
service = discovery.build('storage', 'v1', credentials=credentials)


def insert_acls(db):
    for bucket in db.table('Bucket').all():
        request = service.bucketAccessControls().list(bucket=bucket['name'])
        try:
            response = request.execute()
            for acl in response['items']:
                db.table('Bucket').update(
                    add_acl({"permission": acl['role'], "scope": acl['entity']}),
                    eids=[bucket.eid])
        except errors.HttpError as err:
            print("Error fetching bucket: %s :", bucket['name'])
            print("%s", str(err))


def insert_defacls(db):
    for bucket in db.table('Bucket').all():
        request = service.defaultObjectAccessControls().list(bucket=bucket['name'])
        try:
            response = request.execute()
            for defacl in response['items']:
                db.table('Bucket').update(
                    add_defacl({"permission": defacl['role'], "scope": defacl['entity']}),
                    eids=[bucket.eid])
        except errors.HttpError as err:
            print("Error fetching bucket ACL: %s :", bucket['name'])
            print("%s", str(err))


# Function to pass Tinydb for the update query
def add_acl(acl):
    def transform(element):
        try:
            element['acls'].append(acl)
        except KeyError:
            element['acls'] = [acl]

    return transform


def add_defacl(defacl):
    def transform(element):
        try:
            element['defacls'].append(defacl)
        except KeyError:
            element['defacls'] = [defacl]

    return transform
