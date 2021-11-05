import logging

from itertools import chain
from dataclasses import dataclass

from django.conf import settings
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import render
from django.views.static import serve

from justagallery.domain.category import get_display_formats, get_default_thumbnail_format, \
	get_default_thumbnail_formats
from .domain.image import create_thumbnail, Size
from . import models
from .domain.url import get_url_by_image, get_category_by_url, get_url_by_category, get_thumbnail_url, get_size_from_str


logger = logging.getLogger(__name__)


def index(request: HttpRequest) -> HttpResponse:
	categories = models.Category.objects.filter(parent=None).order_by('-created_at').all()
	return render(request, 'index.html.j2', dict(categories=categories), using='jinja2')


def category(request: HttpRequest, url) -> HttpResponse:
	@dataclass
	class Item:
		url: str
		title: str
		thumbnail_url: str

	url = url.strip('/')
	category = get_category_by_url(url)
	if not category:
		raise Http404('Category not found')
	if category.parent:
		parent = Item(url=get_url_by_category(category.parent), title=category.parent.title, thumbnail_url='')
	else:
		parent = Item(url='/', title='index', thumbnail_url='')
	default_thumbnail_format = get_default_thumbnail_format(category)
	child_categories = [
		Item(url=get_url_by_category(child_category), title=child_category.title,
				thumbnail_url=get_thumbnail_url(child_category.images.first(), default_thumbnail_format)
					if child_category.images.count() > 0 else '')
			for child_category in category.children.all()
	]
	images = [
		Item(url=get_url_by_image(image), title=image.title,
				thumbnail_url=get_thumbnail_url(image, default_thumbnail_format))
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
	format: str = request.GET.get('format', None)
	category = get_category_by_url(category_slug.strip('/'))
	if not category:
		raise Http404('Category not found')
	try:
		image = models.Image.objects.get(category=category, slug=image_slug)
	except models.Image.DoesNotExist:
		raise Http404('Image not found')

	image_url = get_url_by_image(image)
	if image_url not in request.headers.get('referer', ''):
		image.views += 1
		image.save()
		logger.debug('Increased views counter to {}'.format(image.views))

	display_formats = get_display_formats(image)
	thumbnails = [{
		'width': df.width,
		'height': df.height,
		'crop': df.crop,
		'thumbnail_url': get_thumbnail_url(image, df),
		'image_url': get_url_by_image(image, df),
	} for df in display_formats]
	thumbnails.sort(key=lambda dct: (dct['width'], dct['height'], dct['crop']))

	# use parameter-less URL for default (1st) format
	thumbnails[0]['image_url'] = image_url

	category_url = get_url_by_category(category)

	current_thumbnail_idx = 0
	if format:
		try:
			x, y, crop = get_size_from_str(format)
			for i, thumbnail in enumerate(thumbnails):
				if (x, y, crop) == (thumbnail['width'], thumbnail['height'], thumbnail['crop']):
					current_thumbnail_idx = i
					break
		except ValueError:
			pass

	template_vars = dict(
		image=image,
		thumbnails=thumbnails,
		category_url=category_url,
		current_thumbnail_idx=current_thumbnail_idx
	)
	return render(request, 'image.html.j2', template_vars, using='jinja2')


def thumbnail(request: HttpRequest, category_id, size, image_slug) -> HttpResponse:
	path = "{}/{}/{}".format(category_id, size, image_slug)
	static_serve = lambda: serve(request, path, document_root=settings.THUMBNAILS_ROOT)
	try:
		return static_serve()
	except Http404:
		try:
			image = models.Image.objects.get(category_id=int(category_id), slug=image_slug)
		except models.Image.DoesNotExist:
			raise Http404('Image not found')
		try:
			x, y, crop = get_size_from_str(size)
		except ValueError:
			raise Http404('Wrong size')
		size = Size(x, y)
		formats = chain(get_display_formats(image), get_default_thumbnail_formats(image.category))
		if (size.x, size.y, crop) not in [(dp.width, dp.height, dp.crop) for dp in formats]:
			raise Http404('Unknown size')
		create_thumbnail(image.file.path, settings.THUMBNAILS_ROOT / path, size, crop)
		return static_serve()
