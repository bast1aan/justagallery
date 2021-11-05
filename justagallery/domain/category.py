from typing import Iterator, Optional

from django.db.models import Model
from justagallery import models


def get_display_formats(model: Model) -> Iterator[models.ThumbnailFormat]:
	""" Retrieve display formats recursivly to the root category. """
	if isinstance(model, models.Image):
		display_formats: [models.ThumbnailFormat] = model.display_formats.all()
		if len(display_formats) > 0:
			return display_formats
		model = model.category
	if isinstance(model, models.Category):
		while model:
			display_formats: [models.ThumbnailFormat] = model.display_formats.all()
			if len(display_formats) > 0:
				return display_formats
			model = model.parent

def get_default_thumbnail_format(category: models.Category) -> Optional[models.ThumbnailFormat]:
	""" Retrieve default thumbnail format recursively to the root category. """
	return next(get_default_thumbnail_formats(category), None)

def get_default_thumbnail_formats(category: models.Category) -> Iterator[models.ThumbnailFormat]:
	""" Retrieve all default thumbnail formats recursively to the root category. """
	while category:
		default_thumbnail_format: models.ThumbnailFormat = category.default_thumbnail_format
		if default_thumbnail_format:
			yield default_thumbnail_format
		category = category.parent
