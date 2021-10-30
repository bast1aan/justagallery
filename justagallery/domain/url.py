from typing import Dict, Optional, Tuple

from .. import models

_URLS_TO_CATEGORY: Dict[str, models.Category] = {}


def get_category_by_url(url: str) -> Optional[models.Category]:
	url_parts = url.split('/')
	try:
		category = None
		for url_part in url_parts:
			category = models.Category.objects.filter(parent=category, slug=url_part).first()
		return category
	except models.Category.DoesNotExist:
		return None


def get_url_by_category(category: models.Category) -> str:
	url_parts = []
	while(category):
		url_parts.append(category.slug)
		category = category.parent
	url_parts.reverse()
	return '/' + '/'.join(url_parts) + '/'


def get_url_by_image(image: models.Image, format: models.ThumbnailFormat = None) -> str:
	category_part = get_url_by_category(image.category)
	url = "{}{}.html".format(category_part, image.slug)
	if format:
		url += '?format={}'.format(_get_size(format))
	return url


def get_thumbnail_url(image: models.Image, thumbnail_format: models.ThumbnailFormat) -> str:
	return "/thumbnails/{}/{}/{}".format(
		image.category_id,
		_get_size(thumbnail_format),
		image.slug
	)

def _get_size(format: models.ThumbnailFormat) -> str:
	return "{}x{}{}".format(
		format.width,
		format.height,
		"-c" if format.crop else ""
	)

def get_size_from_str(size: str) -> Tuple[int, int, bool]:
	"""
		:raises ValueError if format or sizes are wrong
	"""
	if size.endswith('-c'):
		crop = True
		size = size[:-2]
	else:
		crop = False
	width, height = (int(s) for s in size.split('x'))
	if width < 1 or height < 1:
		raise ValueError('width and height should be greater than or equals to 1')
	return width, height, crop
