### To test the EMA Interface, make html file containing URLs and script
### containing curl calls.

import re

global_id = u'b9e8353b-e113-4b03-856f-c118e0b70666'
activation_code = '427621639782'

gets = [ 'GetUserProfile',
         'GetUserProfile/bogus_uid',
         'GetUserProfile/%s' % activation_code,
 
         'GetReportSurvey',
         'GetReportSurvey/1',
 
         ]

puts = [ 'Report',
         'Report/bogus_uid/bogus_reports',
  ]


html_file = 'test.html'
bash_file = 'test.sh'

ema_user = 'ema'
ema_password = 'emapass'

base = 'http://localhost:8000/ema/'
#base = 'http://178.18.82.138:8000/ema/'

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
for resource in gets:
    w('<li><a href="' + resource + format + '">' + resource + '</a>')
w('<ul>')
w('</body>')

fd.close()

# Write curl script

fd = open(bash_file, 'w')

header = """#!/bin/bash
base='%s'
silent='-s'
#include='-i'
#json='-H "Accept:application/json"'
post='-X POST -H Content-type:application/json'
opts=$silent $include $json
data=$(cat report.json)

e () {
  echo '>>>' $*
  $*
  echo
}
""" % base

w(header)

# Gets

w('# GETs')
for resource in gets:
    w('e curl $opts ${base}' + resource + format)

# Puts

def ww(s):
    w("echo '>>>' " + s)
    w(s)

w('# PUTs')
ww('curl $post $opts --data \"$data\" ${base}Report')
w('echo')

fd.close()
