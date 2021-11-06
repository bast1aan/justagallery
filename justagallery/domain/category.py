from typing import Iterator, Optional, Any

from . import entities


def get_display_formats(model: Any) -> Iterator[entities.ThumbnailFormat]:
	""" Retrieve display formats recursivly to the root category. """
	if isinstance(model, entities.Image):
		display_formats = model.display_formats.all()
		if len(display_formats) > 0:
			return display_formats
		model = model.category
	if isinstance(model, entities.Category):
		while model:
			display_formats = model.display_formats.all()
			if len(display_formats) > 0:
				return display_formats
			model = model.parent

def get_default_thumbnail_format(category: entities.Category) -> Optional[entities.ThumbnailFormat]:
	""" Retrieve default thumbnail format recursively to the root category. """
	return next(get_default_thumbnail_formats(category), None)

def get_default_thumbnail_formats(category: entities.Category) -> Iterator[entities.ThumbnailFormat]:
	""" Retrieve all default thumbnail formats recursively to the root category. """
	while category:
		default_thumbnail_format = category.default_thumbnail_format
		if default_thumbnail_format:
			yield default_thumbnail_format
		category = category.parent

def get_default_image(category: entities.Category) -> entities.Image:
	"""
		Calculate default image of category, according to following algorithm:
		First try to find a defined default_image in the category, if not found
		try the same within the category's child categories.
		If nothing found, try to find first image found in the category or its
		child categories.
	"""

	def default_image(category: entities.Category) -> entities.Image:
		if category.default_image:
			return category.default_image
		for category in category.children.all():
			return default_image(category)

	def first_image(category: entities.Category) -> entities.Image:
		first = category.images.first()
		if first:
			return first
		for category in category.children.all():
			return first_image(category)

	image = default_image(category)
	if not image:
		image = first_image(category)
	return image
