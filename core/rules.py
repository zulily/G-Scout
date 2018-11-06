import datetime

from tinydb import TinyDB

from core import add_finding
from categories.firewalls import test_allowed
from categories.service_account_keys import key_is_old


def rules(projectId):
    db = TinyDB("project_dbs/" + projectId + ".json")

    class Rule:
        def __init__(self, rule_title, category, filter_func):
            try:
                db.table('Rule').insert({"title": rule_title, "category": category})
                for entity in list(filter(filter_func, db.table(category).all())):
                    add_finding.add_finding(db, category, entity, rule_title)
            except KeyError:
                pass

    Rule("Unused Network", "Network",
         lambda network: not network.get('members'))

    Rule("Unrestriced Internal Traffic", "Network",
         lambda network: network.get('firewallRules')
                         and [True for rule in network['firewallRules']
                              if "10.128.0.0/9" in rule['sourceRanges']
                              and [True for allow in rule['allowed']
                                   if not allow.get('ports') or "0-65535" in allow['ports']]])

    Rule("Primitive Roles in Use", "Role",
         lambda role: role['role'] in ["roles/owner", "roles/editor", "roles/viewer"])

    Rule("Role Given to User", "Role",
         lambda role: [True for member in role['members'] if member[:4] == "user"])

    Rule("allUsers Permissions in Use", "Bucket",
         lambda bucket: [True for acl in bucket['acls'] if acl['scope'] == "allUsers"])

    Rule("User Given Permissions", "Bucket",
         lambda bucket: [True for acl in bucket['acls'] if acl['scope'][:4] == "user"])

    Rule("Bucket Logging Not Enabled", "Bucket", lambda bucket: "logging" not in bucket)

    Rule("Bucket Versioning Not Enabled", "Bucket",
         lambda bucket: "versioning" not in bucket)

    Rule("Owner Role for allUsers in DefACL", "Bucket",
         lambda bucket: [True for defacl in bucket['defacls'] if
                         defacl['scope'] == "allUsers" and defacl['permission'] == "OWNER"])

    Rule("Read Role for allUsers in DefACL", "Bucket",
         lambda bucket: [True for defacl in bucket['defacls'] if
                         defacl['scope'] == "allUsers" and defacl['permission'] == "READER"])

    Rule("No Recent Backup Images", "Compute Engine",
         lambda instance: db.table('Snapshot').all()
                          and [True for snapshot in db.table('Snapshot').all()
                               if not [True for disk in instance['disks']
                                       if snapshot['sourceDisk'] in disk.values()]
                               and datetime.datetime.strptime(snapshot['creationTimestamp'][:10], "%Y-%m-%d")
                               < datetime.datetime.now() - datetime.timedelta(days=30)])

    Rule("Allows full access to all Cloud APIs", "Compute Engine", lambda instance: "https://www.googleapis.com/auth/cloud-platform" in instance['serviceAccounts'][0]['scopes'])

    Rule("Serial Port Enabled", "Compute Engine", lambda instance: instance.get("metadata").get("items")
    and [True for item in instance.get("metadata").get("items") if item['key']=="serial-port-enable" and item['value']=='true'])

    Rule("Automatic Backup Disabled", "SQL Instance",
         lambda instance: not instance.get('settings').get('backupConfiguration').get('enabled'))

    Rule("Binary Log Disabled", "SQL Instance",
         lambda instance: not instance.get('settings').get('backupConfiguration').get('binaryLogEnabled'))

    Rule("SSL Not Required", "SQL Instance",
         lambda instance: not instance.get('settings').get('ipConfiguration').get('requireSsl'))

    Rule("Unrotated Keys", "Service Account",
         lambda account: account.get('keys')
                         and [True for key in account.get('keys') if key_is_old(key)])

    Rule("allUsers Have Permissions", "Service Account",
         lambda account: account.get('iam_policies')
                         and [True for policy in account.get('iam_policies')
                              if "allUsers" in policy['scope']])

    Rule("MongoDB Port Open to All", "Firewall",
         lambda firewall: firewall.get("sourceRanges")
                          and "0.0.0.0/0" in firewall['sourceRanges']
                          and [True for rule in firewall['allowed'] if rule.get('ports')
                               and "27017" in rule['ports']])

    Rule("PostgreSQL Port Open to All", "Firewall",
         lambda firewall: firewall.get("sourceRanges")
                          and "0.0.0.0/0" in firewall['sourceRanges']
                          and [True for rule in firewall['allowed'] if rule.get('ports')
                               and "54322" in rule['ports']])

    Rule("Oracle Port Open to All", "Firewall",
         lambda firewall: firewall.get("sourceRanges")
                          and "0.0.0.0/0" in firewall['sourceRanges']
                          and [True for rule in firewall['allowed'] if rule.get('ports')
                               and "1521" in rule['ports']])

    Rule("MySQL Port Open to All", "Firewall",
         lambda firewall: firewall.get("sourceRanges")
                          and "0.0.0.0/0" in firewall['sourceRanges']
                          and test_allowed(firewall, "tcp", [3306, 1433]))

    Rule("DNS Port Open to All", "Firewall",
         lambda firewall: firewall.get("sourceRanges")
                          and "0.0.0.0/0" in firewall['sourceRanges']
                          and [True for rule in firewall['allowed'] if rule.get('ports')
                               and "53" in rule['ports']])

    Rule("FTP Port Open to All", "Firewall",
         lambda firewall: firewall.get("sourceRanges")
                          and "0.0.0.0/0" in firewall['sourceRanges']
                          and [True for rule in firewall['allowed'] if rule.get('ports')
                               and "21" in rule['ports']])

    Rule("Telnet Port Open to All", "Firewall",
         lambda firewall: firewall.get("sourceRanges")
                          and "0.0.0.0/0" in firewall['sourceRanges']
                          and [True for rule in firewall['allowed'] if rule.get('ports')
                               and "23" in rule['ports']])

    Rule("RDP Port Open to All", "Firewall",
         lambda firewall: firewall.get("sourceRanges")
                          and "0.0.0.0/0" in firewall['sourceRanges']
                          and [True for rule in firewall['allowed'] if rule.get('ports')
                               and "3389" in rule['ports']])

    Rule("SSH Port Open to All", "Firewall",
         lambda firewall: firewall.get("sourceRanges")
                          and "0.0.0.0/0" in firewall['sourceRanges']
                          and [True for rule in firewall['allowed'] if rule.get('ports')
                               and "22" in rule['ports']])

    Rule("All Ports Open to All", "Firewall",
         lambda firewall: firewall.get("sourceRanges")
                          and "0.0.0.0/0" in firewall['sourceRanges']
                          and (not firewall.get('allowed')[0].get('ports')
                               or [True for rule in firewall['allowed'] if rule.get('ports')
                                   and '0-65535' in rule.get('ports')]))

    Rule("Any Ports Open to Ingress from All", "Firewall",
         lambda firewall: firewall.get("sourceRanges")
                          and "0.0.0.0/0" in firewall['sourceRanges']
                          and "INGRESS" in firewall['direction'])

    Rule("Use of Port Ranges", "Firewall",
         lambda firewall: [allow for allow in firewall['allowed']
                           if allow.get('ports') and [port for port in allow['ports'] if "-" in port]])

    Rule("Unused Firewall Rules", "Firewall",
         lambda firewall: not firewall.get('affectedInstances'))
