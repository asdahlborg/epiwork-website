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

res = [ #'surveyuser',
        'GetUserProfile',
        'GetUserProfile/be4e5f36-714c-482a-a754-30a200874f75',
        #'GetUserProfile/schema',
        #'GetUserProfile/?user__global_id=193807d8-4a30-4601-9bc5-bc59db1696cd',

        'GetReportSurvey',
        'GetReportSurvey/1',
        #'GetReportSurvey/schema',
        #'GetReportSurvey',
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

