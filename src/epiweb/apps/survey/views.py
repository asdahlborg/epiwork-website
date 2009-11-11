from django import forms
from django.template import Context, loader
from django.http import HttpResponse

questions = [
    [
        { "id": "q0001", "text": "Name", 
          "format": "text", "length": 50
        },
        { "id": "q0002", "text": "Place of birth", 
          "format": "text", "length": 50
        },
        { "id": "q0003", "text": "Data of birth", 
          "format": "date"
        }
    ],
    [
        { "id": "q0004", "text": "Address",
          "format": "text", "length": 100
        },
        { "id": "q0005", "text": "City",
          "format": "text", "length": 50
        },
        { "id": "q0006", "text": "Post Code",
          "format": "text", "length": 10
        }
    ]
]

print questions

def create_field(item):
    label = item.get('text')
    if item['format'] == 'text':
        length = item.get('length', None)
        if length:
            return forms.CharField(label=label, max_length=length)
        else:
            return forms.CharField(label=label)
    else:
        return forms.CharField(label=label)

def create_form(data):
    f = forms.Form()
    for item in data:
        f.fields[item['id']] = create_field(item)
    return f

def index(request):
    form = create_form(questions[0])

    t = loader.get_template('survey/index.html')
    c = Context({
        'form': form
    })
    return HttpResponse(t.render(c))

