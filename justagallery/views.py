from dataclasses import dataclass

from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import render

from . import models
from . import domain

def index(request: HttpRequest) -> HttpResponse:
	categories = models.Category.objects.filter(parent=None).order_by('-created_at').all()
	return render(request, 'index.html.j2', dict(categories=categories), using='jinja2')


def category(request: HttpRequest, url) -> HttpResponse:
	@dataclass
	class Item:
		url: str
		title: str

	url = url.strip('/')
	category = domain.get_category_by_url(url)
	if not category:
		raise Http404('Category not found')
	if category.parent:
		parent = Item(url=domain.get_url_by_category(category.parent), title=category.parent.title)
	else:
		parent = Item(url='/', title='index')
	child_categories = [
		Item(url=domain.get_url_by_category(child_category), title=child_category.title)
			for child_category in category.children.all()
	]
	images = [
		Item(url=domain.get_url_by_image(image), title=image.title)
			for image in category.images.all()
	]

	template_vars = dict(
		category=category,
		parent=parent,
		child_categories=child_categories,
		images=images,
	)
	return render(request, 'category.html.j2', template_vars, using='jinja2')


def image(request:HttpRequest, category_slug:str , image_slug: str) -> HttpResponse:
	category = domain.get_category_by_url(category_slug.strip('/'))
	if not category:
		raise Http404('Category not found')
	try:
		image = models.Image.objects.get(category=category, slug=image_slug)
	except models.Image.DoesNotExist:
		raise Http404('Image not found')
	return render(request, 'image.html.j2', dict(image=image), using='jinja2')
