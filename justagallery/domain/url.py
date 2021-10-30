from typing import Dict, Optional

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


def get_url_by_image(image: models.Image) -> str:
	category_part = get_url_by_category(image.category)
	return "{}{}.html".format(category_part, image.slug)


def get_thumbnail_url(image: models.Image, thumbnail_format: models.ThumbnailFormat) -> str:
	size = "{}x{}{}".format(
		thumbnail_format.width,
		thumbnail_format.height,
		"-c" if thumbnail_format.crop else ""
	)
	return "/thumbnails/{}/{}/{}".format(
		image.category_id,
		size,
		image.slug
	)
