from django.http import Http404
from django.shortcuts import render

import models

# Create your views here.

def all(request, template_name='diary/index.html'):
    return render(request, template_name)
