#!/bin/bash
set -x
# PUT example for registering a survey response.

curl -v -X POST -i -H "Content-type: application/json" -s --data '{
  "prot_v" : "1.0",
  "serv": 99,
  "uid": "b9e8353b-e113-4b03-856f-c118e0b70666",
  "reports": [{ "uid" : "b9e8353b-e113-4b03-856f-c118e0b70666",
                "surv_v" : "gold-standard-weekly-1.6",
                "ts" : 1262304000000,
                "data": [{ "id" : "WeeklyQ1",
                           "value" : ["17"] },
                         { "id" : "WeeklyQ1b",
                            "value" : "0" }
                        ]
               }
             ]
}
' http://ema:emapass@localhost:8000/ema/Report
