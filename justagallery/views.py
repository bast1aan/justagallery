from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from . import models

def index(request: HttpRequest) -> HttpResponse:
	categories = models.Category.objects.filter(parent=None).order_by('-created_at').all()
	return render(request, 'index.html.j2', dict(categories=categories), using='jinja2')
