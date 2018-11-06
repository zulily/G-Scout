# G-Scout

This repo is an enhanced fork of [G-Scout](https://github.com/nccgroup/G-Scout). G-Scout is a tool for auditing Google Cloud Platform configurations. By making API calls, applying security rules, and generating HTML files based on the output, G-Scout makes it easy to analyze the security of a GCP environment.

This repo takes G-Scout, updates the authentication to the new google.auth mechanisms, adds regression checking, and pushing the regressions to slack channels as well as HTML email via SMTP.


## Pre-requisites

#### Service Account
This version assumes you have a service account created using the following steps:

   1. Go to the console service accounts page at https://console.cloud.google.com/iam-admin/serviceaccounts/project?project=[project] and create a service account.
   2. Go to IAM management console at https://console.cloud.google.com/iam-admin/iam/project?project=[project] and add Security Reviewer and Viewer permissions to the service account created in step 1.
   3. Generate a Service Account key from https://console.cloud.google.com/apis/credentials?project=[project].
   4. Download the JSON file generated in step 3 into the `keys` sub-directory of your application, naming it something convenient (as you will use that `<friendly_name>`, minus the .json suffix, to run gscout against that project, example filename:  `./keys/mygceproject.json`.

#### Account Configs

This version requires, for each project, in addition to the Service Account JSON file, a config file named the same `<friendly_name>`: example filename `./keys/mygceproject.config`.   The filename should have the following lines, replacing the `<..>` with the appropriate values:

- `export GOOGLE_APPLICATION_CREDENTIALS=./keys/<friendly_name>.json`
- `export GOOGLE_PROJECT_NAME=<friendly_name>`
- `export SECURITY_WEBHOOK=/services/<REPLACE_WITH_SEC_TEAM_SLACK_INCOMING_WEBHOOK_PATH>`
- `export TEAM_WEBHOOK=/services/<REPLACE_WITH_PROJ_TEAM_SLACK_INCOMING_WEBHOOK_PATH>`
- `export SECURITY_DL=<sec_team@example.com>`
- `export TEAM_DL=<proj_team@example.com>`
- `export SMTPHost=<SMTP_FQDN>`
- `export SMTPPort=<PORT_NUMBER>`
- `export AUTH_USERNAME=<SMTP_USERNAME>`
- `export AUTH_PASS=<SMTP_PASSWORD>`
- `export ARCHIVE_DIR=<PATH_TO_FOLDER>`

#### Python Setup

This version also assumes you have the `requirements.txt` contents installed in your python environment. (For virtualenv users, modify the `gscout` script to set your virtualenv activation command path to `${VENV}`'s value.)

## Usage

To run the application:
```
./gscout <friendly_name>
```

The HTML report output will be in the "Report Output" folder, in the `<project-id>` subdirectory.
An archive of the regressions is zipped and placed in the `ARCHIVE_DIR` folder (use zgrep to find history of issues).

To create a custom rule, add it to the `core/rules.py` file. A Rule object takes a name, a category, and a filter function. The function will be passed a json object corresponding to the category. 

