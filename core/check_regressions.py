"""
    Helper function to calculate what changed between previous and current
    gscout runs
"""
import os

from tinydb import TinyDB
from core.utils import archive_regressions

def flatten_regvals(regvals):
    """
        simplify regression to top-level key-value pairs
    """
    simplevals = {}
    for key in regvals:
        tmpval = regvals[key]
        if isinstance(tmpval, (list, dict)):
            if len(tmpval) == 1 and isinstance(tmpval, list) and len(tmpval[0]) == 1:
                simplevals[key] = tmpval[0]
        else:
            simplevals[key] = tmpval

    return simplevals

def compare_regs(first, second):
    """
        Eliminate cases where the same object is counted as new/fixed reg.
        Occurs in networks, e.g.
    """
    new_regs = []
    for reg in first:
        prune = False
        if reg in second:
            prune = True
        else:
            rule = reg.keys()[0]
            values = flatten_regvals(reg[rule])
            fvalues = []
            for freg in second:
                frule = freg.keys()[0]
                if rule == frule:
                    fvalues.append(flatten_regvals(freg[frule]))
            if values in fvalues:
                prune = True
        if not prune:
            new_regs.append(reg)
    return new_regs

def check_regressions(dbstr, project):
    """
        Compare regression table from DB
    """
    odbstr = dbstr + '.old'
    odb = TinyDB(odbstr)
    db = TinyDB(dbstr)
    regs = db.table('Regression').all()
    old_regs = odb.table('Regression').all()

    if 'ARCHIVE_DIR' in os.environ:
        archive_regressions(os.environ['ARCHIVE_DIR'], project, regs)

    newregs = compare_regs(regs, old_regs)
    fixregs = compare_regs(old_regs, regs)
    return newregs, fixregs


#t1, t2 = check_regressions('../test_dbs/test_db.json', project=None)
#pprint("New Regressions:" + str(len(t1)))
#pprint("Fixed Regressions:" + str(len(t2)))
