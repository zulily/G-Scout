#!/usr/bin/env python
"""
   This script collects security-related settings from a Google project. It
   - Archives them to a TinyDB named after the Google Project ID.
   - Runs rules against the tables in the TinyDB to determine issues.
   - Writes those issues as regressions back to the DB.
   - Generates HTML pages of the current state of the issues in the project.
   - Compares the current regressions in the DB against the previous set.
      - New regressions are sent to the given slack channels using a red bar.
      - Fixed regressions are sent to the given slack channels using a green bar.
      - All regressions are sent using html mail via SMTP to the given email addresses.

   gscout.py, called by "gscout" shell script in this directory.
   Usage:
       ./gscout <project name>
   Copyright 2018 zulily, Inc.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import errno
import os
import logging

import google.auth
from tinydb import TinyDB

from core.fetch import fetch
from core.rules import rules
from core.display_results import display_results
from core.check_regressions import check_regressions
from core.utils import report_regressions


CREDS, DEF_PROJ_ID = google.auth.default()

logging.basicConfig(filename="log.txt")
logging.getLogger().setLevel(logging.ERROR)
# Silence some errors
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

def get_project():
    """
        Retained in case logic should change.
    """
    return DEF_PROJ_ID


def init_dirs(project_id, db_string):
    """
        Initialize necessary directories
    """
    reqdirs = ["Report Output", "project_dbs", "Report Output/" + project_id]
    for reqdir in reqdirs:
        try:
            os.makedirs(reqdir)
        except OSError as err:
            if err.errno == errno.EEXIST:
                pass

    olddb = db_string + '.old'
    try:
        os.unlink(olddb)
    except OSError as err:
        if err.errno == errno.ENOENT:
            pass
        else:
            logging.exception(str(err))

    if os.path.exists(db_string):
        os.rename(db_string, olddb)


def main():
    """
        Main function, driving regression discovery.
    """
    try:
        project = get_project()
        if project:
            print 'Scouting ' + project
            dbstr = "project_dbs/" + project + ".json"
            init_dirs(project, dbstr)
        else:
            print "Project ID not found"
    except Exception as err:
        print "Could not list project due to Google Credential errors."
        print str(err)
        exit(1)

    curdb = TinyDB(dbstr)
    try:
        fetch(project, curdb)
    except Exception as err:
        print "Error fetching " +  project
        logging.exception(str(err))

    try:
        print"Checking rules."
        rules(project)
    except Exception as err:
        logging.exception(err)

    print"Generating results web pages."
    display_results(curdb, project)

    print"Checking for regressions."
    newregs, fixregs = check_regressions(dbstr, project)

    print"Reporting regressions."
    report_regressions(newregs, fixregs)


if __name__ == "__main__":
    main()

