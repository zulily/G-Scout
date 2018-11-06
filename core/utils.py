"""
    Helper function used for slack and email integration.
"""
import datetime
import json
import gzip
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from pprint import pformat
import requests

from core.display_results import format_html_regressions

WEBHOOK_URL = 'https://hooks.slack.com'
REQUIRE_TLS = True

def archive_regressions(archive_dir, project, regs):
    """
        Write the regressions table to its own DB, then gzip.
    """
    nowstr = datetime.datetime.now().strftime("%y%m%d%H%M")
    archive_file = archive_dir + '/' + project + '_regs_' + nowstr + '.txt.gz'
    content = pformat(regs)
    with gzip.open(archive_file, 'wb') as filehandle:
        filehandle.write(content)


def format_slack_regression(title, color, reg):
    """
        Flatten regressions into a slack message
    """
    payload = {}
    keylist = []
    attachdict = {}
    rule = reg.keys()[0]
    attachdict['text'] = title + ': ' + rule
    attachdict['color'] = color
    for key in reg[rule]:
        field = {}
        field['title'] = key
        field['short'] = False
        tmpval = reg[rule][key]
        if isinstance(tmpval, (list, dict)):
            if len(tmpval) == 1 and isinstance(tmpval, list):
                field['value'] = tmpval[0]
            else:
                field['value'] = json.dumps(tmpval)
        else:
            field['value'] = tmpval
        keylist.append(field)
    attachdict['fields'] = keylist
    payload['attachments'] = [attachdict]
    return payload


def post_regressions_slack(title, color, reg):
    """
       Send regs/fixes to slack
    """
    url = WEBHOOK_URL + os.environ['SECURITY_WEBHOOK']
    header = {"Content-type" : "application/json"}
    payload = format_slack_regression(title, color, reg)
    response = requests.post(url, json=payload, headers=header)
    if 'TEAM_WEBHOOK' in os.environ:
        url = WEBHOOK_URL + os.environ['TEAM_WEBHOOK']
        response = requests.post(url, json=payload, headers=header)


def send_report(new_regs, new_fixes):
    """
       Send report in HTML via SMTP
    """
    recipient = os.environ['TEAM_DL']
    cc_dl = os.environ['SECURITY_DL']
    sender = os.environ['AUTH_USERNAME']
    proj = os.environ['GOOGLE_PROJECT_NAME']
    
    #Terrible hack for multiple recipients in the "To" line
    multi_recipients = False
    if "," in recipient:
        multi_recipients = recipient.split(",")

    msg = MIMEMultipart('alternative')
    if multi_recipients:
        msg['To'] = multi_recipients
        to_addrs = multi_recipients + cc_dl
    else:
        msg['To'] = recipient
        to_addrs = recipient + cc_dl
    msg['CC'] = cc_dl
    msg['From'] = sender
    msg['Subject'] = 'Google Cloud Regression Report for ' + proj

    #  format plain text
    json_msg = 'New Regressions:\n' + json.dumps(new_regs, separators=('\n', ':'))
    json_msg += 'Regressions Fixed:\n' + json.dumps(new_fixes, separators=('\n', ':'))

    # format html
    html_regs = format_html_regressions(title='New Regressions', regs=new_regs)
    html_fixes = format_html_regressions(title='Regressions Fixed',
                                         regs=new_fixes)

    html_header = '<html><head></head><body>'
    html_footer = '</body></html>'
    msg_html = html_header + html_regs + html_fixes + html_footer

    msg.attach(MIMEText(json_msg, 'plain'))
    msg.attach(MIMEText(msg_html, 'html'))

    try:
        server = smtplib.SMTP(os.environ['SMTPHost'],
                              os.environ['SMTPPort'])
        server.ehlo()
        if REQUIRE_TLS:
            server.starttls()
        #stmplib docs recommend calling ehlo() before & after starttls()
        server.ehlo()
        server.login(sender, os.environ['AUTH_PASS'])
        server.sendmail(sender, to_addrs, msg.as_string())
        server.close()
    # Display an error message if something goes wrong.
    except Exception as err:
        print 'Error: ' +  str(err)
    else:
        print 'Email sent!'


def report_regressions(new_regs, new_fixes):
    """
        Send new regressions, fixes to slack. Send summary to email.
    """

    proj = os.environ['GOOGLE_PROJECT_NAME']
    for reg in new_regs:
        post_regressions_slack(title=proj + ': New Regression', color='#FF0000', reg=reg)
    for reg in new_fixes:
        post_regressions_slack(title=proj + ': Fixed Regression', color='#008000', reg=reg)
    if (len(new_regs) + len(new_fixes)) > 1:
        send_report(new_regs, new_fixes)
