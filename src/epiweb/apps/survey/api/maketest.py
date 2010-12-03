### To test the EMA Interface, make html file containing URLs and script
### containing curl calls.

import re

html_file = 'test.html'
fd = open(html_file, 'w')

def w(s):
  fd.write(s + '\n')

base = 'http://localhost:8000/ema/'
# base = 'http://178.18.82.138:8000/ema/v1/' 

fj = '?format=json'
title = 'Tests for the Epiwork Mobile Application Interface'

header = """<html>
<head>
<title>%s</title>
<base href="%s"/>
</head>
<body>
<h1>%s</h1>
""" % (title, base, title)

res = [ 'GetUserProfile',
        'GetUserProfile/bogus_uid',
        'GetUserProfile/be4e5f36-714c-482a-a754-30a200874f75',

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

w(header)
w('<ul>')
for r in res:
  url = r
#  url = re.sub('\?', fj + '&', r)
#  if url == r:
#    url = r + '/' + fj
  w('<li><a href="' + url + '">' + r + '</a>')
w('<ul>')
w('</body>')


fd.close()

# Curl script goes here...

bash_file = 'test.sh'
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
  w('e curl $silent $include $header ${base}' + r)

fd.close()
