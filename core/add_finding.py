from tinydb import Query


def add_finding(db, entity_table, entity, rule_title):
    regress_table = db.table('Regression')
    finding_table = db.table('Finding')
    rule_table = db.table('Rule')
    finding_table.insert({
        "entity": {"table": entity_table, "id": entity.eid},
        "rule": {"table": "rule", "id": rule_table.search(Query().title == rule_title)[0].eid}
    })
    regress_table.insert({
        rule_title: entity
    })
