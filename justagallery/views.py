from dataclasses import dataclass

from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import render

from . import models
from . import domain

def index(request: HttpRequest) -> HttpResponse:
	categories = models.Category.objects.filter(parent=None).order_by('-created_at').all()
	return render(request, 'index.html.j2', dict(categories=categories), using='jinja2')


def category(request: HttpRequest, url) -> HttpResponse:
	url = url.strip('/')
	category = domain.get_category_by_url(url)
	if not category:
		raise Http404('Category not found')
	if category.parent:
		parent_url = domain.get_url_by_category(category.parent)
	else:
		parent_url = ''
	child_categories = [
		{
			'url': domain.get_url_by_category(child_category),
			'title': child_category.title
		} for child_category in category.children.all()
	]
	images = [
		{
			'title': image.title
		} for image in category.images.all()
	]

	template_vars = dict(
		category=category,
		parent_url=parent_url,
		child_categories=child_categories,
		images=images,
	)
	return render(request, 'category.html.j2', template_vars, using='jinja2')
