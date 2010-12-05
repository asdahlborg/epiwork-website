### To test the EMA Interface, make html file containing URLs and script
### containing curl calls.

import re

global_id = 'be4e5f36-714c-482a-a754-30a200874f75'

res = [ 'GetUserProfile',
        'GetUserProfile/bogus_uid',
        'GetUserProfile/%s' % global_id,

        'GetReportSurvey',
        'GetReportSurvey/1',

        'GetImage',
        'GetImage/bogus_type/bogus_uid',

        'Report',
        'Report/bogus_uid/bogus_reports',

        'GetLanguage',
        'GetLanguage/bogus_arg',

        'GetStatsHeaders',
        'GetStatsHeaders/bogus_language',

        'GetStatistic',
        'GetStatistic/bogus_uid/bogus_id/bogus_lang',
        ]

html_file = 'test.html'
bash_file = 'test.sh'

ema_user = 'ema'
ema_password = 'emapass'

base = 'http://localhost:8000/ema/'
# base = 'http://178.18.82.138:8000/ema/v1/'

base = re.sub('//', '//%s:%s@' % (ema_user, ema_password), base)

title = 'Tests for the Epiwork Mobile Application Interface'

fe = ''
fj = '/?format=json'
fy = '/?format=yaml'
format = fe

def w(s):
  fd.write(s + '\n')

# Write html test file

fd = open(html_file, 'w')

header = """<html>
<head>
<title>%s</title>
<base href="%s"/>
</head>
<body>
<h1>%s</h1>
<br>(only the GET resources work through the browser)<br>
""" % (title, base, title)

w(header)
w('<ul>')
for r in res:
  url = r
  w('<li><a href="' + url + format + '">' + r + '</a>')
w('<ul>')
w('</body>')

fd.close()

# Write curl script

fd = open(bash_file, 'w')

header = """#!/bin/bash
base='%s'
#header='-H "Accept: application/json"'
#include='-i'
silent='-s'

e () {
  echo '>>>' $*
  eval $*
  echo
}
""" % base

w(header)

for r in res:
  w('e curl $silent $include $header ${base}' + r + format)

fd.close()
