from django.db.models import Model
from justagallery import models


def get_display_formats(model: Model) -> [models.ThumbnailFormat]:
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
