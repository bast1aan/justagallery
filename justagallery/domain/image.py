from __future__ import annotations
from abc import ABCMeta
from typing import NamedTuple, Type


class Size(NamedTuple):
	x: int
	y: int

class Image(metaclass=ABCMeta):
	@staticmethod
	def create_thumbnail(orig: str, dest: str, size: Size, crop: bool) -> None:
		"""
			Create thumbnail from original image `orig', writing to
			`dest'. The given size is indicating the maximum of either
			dimension. If `crop' is given, the thumbnail is resized to the minimum
			of either dimension, and the leftover of the max dimension is cropped
			away from the perspective of the center of the image.

			:param orig: path to original file
			:param dest: path to destination file
			:param size: x and y size of the thumbnail
			:param crop: whether the thumbnail must be cropped
		"""
		...

	@staticmethod
	def get_size(path: str) -> Size:
		""" Retrieve the size of the given image on disk. """
		...

image: Type[Image] = None # Image implementation used in this module. Defaults to _pil.Image if not set

def _image() -> Type[Image]:
	global image
	if not image:
		# Default implementation is PIL
		from . import _pil
		image = _pil.Image
	return image


def create_thumbnail(orig: str, dest: str, size: Size, crop: bool):
	return _image().create_thumbnail(orig, dest, size, crop)
create_thumbnail.__doc__ = Image.create_thumbnail.__doc__

def get_size(path: str) -> Size:
	return _image().get_size(path)
get_size.__doc__ = Image.get_size.__doc__
