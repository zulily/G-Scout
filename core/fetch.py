import logging

logging.basicConfig(filename="log.txt")


def fetch(projectId, db):

    from insert_entity import insert_entity
    from categories.firewalls import add_affected_instances, add_network_rules
    from categories.roles import insert_roles
    import categories.compute_engine
    from categories.service_account_keys import insert_service_account_keys
    import categories.service_accounts
    import categories.service_account_IAM_policy
    import categories.buckets

    print "Collecting Data."
    print "Collecting compute networks."
    try:
        insert_entity(projectId, "compute", ["networks"], "Network")
    except Exception as err:
        print "Failed to fetch networks."
        logging.exception("network exception: %s", str(err))

    print "Collecting compute firewalls."
    try:
        insert_entity(projectId, "compute", ["firewalls"], "Firewall")
    except Exception as err:
        print "Failed to fetch firewalls."
        logging.exception("firewall exception: %s", str(err))

    print "Collecting roles."
    try:
        insert_roles(projectId, db)
    except Exception as err:
        print "Failed to fetch roles."
        logging.exception("role exception: %s", str(err))

    print "Collecting sa and sa roles."
    try:
        categories.service_accounts.insert_service_accounts(projectId, db)
        categories.service_accounts.insert_sa_roles(projectId, db)
    except Exception as err:
        print "Failed to fetch service accounts."
        logging.exception("service account exception: %s", str(err))

    print "Collecting sa keys."
    try:
        insert_service_account_keys(projectId, db)
    except Exception as err:
        print "Failed to fetch service account keys."
        logging.exception("service account key exception: %s", str(err))

    print "Collecting sa iam policy."
    try:
        categories.service_account_IAM_policy.insert_sa_policies(projectId, db)
    except Exception as err:
        print "Failed to fetch service account IAM policies."
        logging.exception("service account IAM policie exception: %s", str(err))

    print "Collecting buckets."
    try:
        insert_entity(projectId, "storage", ["buckets"], "Bucket")
    except Exception as err:
        print "Failed to fetch buckets."
        logging.exception("bucket exception: %s", str(err))

    print "Collecting bucket acls, defacls."
    try:
        categories.buckets.insert_acls(db)
        categories.buckets.insert_defacls(db)
    except Exception as err:
        print "Failed to fetch bucket ACLS/DEFACLS."
        logging.exception("bucket acls/defacl exception: %s", str(err))

    print "Collecting compute instances, groups, member instances."
    try:
        categories.compute_engine.insert_instances(projectId, db)
        insert_entity(projectId, "compute", ["instanceTemplates"], "Instance Template")
        categories.compute_engine.insert_instance_groups(projectId, db)
        categories.compute_engine.add_member_instances(projectId, db)
    except Exception as err:
        print "Failed to fetch compute engine instances."
        logging.exception("compute engine instance exception: %s", str(err))

    print  "Collecting network rules."
    try:
        add_network_rules(projectId, db)
        add_affected_instances(projectId, db)
    except Exception as err:
        print "Failed to display instances/rules with instances."
        logging.exception("add network rules/instance exception: %s", str(err))

    print "Collecting compute snapshots."
    try:
        insert_entity(projectId, "compute", ["snapshots"], "Snapshot")
    except Exception as err:
        print "Failed to fetch instance snapshots."
        logging.exception("snapshot exception: %s", str(err))

    print "Collecting sqladmin instances."
    try:
        insert_entity(projectId, "sqladmin", ["instances"], "SQL Instance", "v1beta4")
    except Exception as err:
        print "Failed to fetch SQL instances."
        logging.exception("SQL instance exception: %s", str(err))

    print "Collecting pubsub instances."
    try:
        insert_entity(projectId, "pubsub", ["projects", "topics"], "Topics",
                      "v1", "projects/", "topics")
        insert_entity(projectId, "pubsub", ["projects", "subscriptions"], "Pub/Sub",
                      "v1", "projects/", "subscriptions")
    except Exception as err:
        print "Failed to fetch Pub/Sub topics/subscriptions."
        logging.exception("pub/sub exception: %s", str(err))
