import os
from typing import NamedTuple

from PIL import Image

class Size(NamedTuple):
	x: int
	y: int

def create_thumbnail(orig: str, dest: str, size: Size, crop: bool):
	destdir = os.path.dirname(dest)
	if not os.path.exists(destdir):
		os.makedirs(destdir)
	with Image.open(orig) as im:
		if crop:
			im = _crop_max_square(im)
		im.thumbnail(size)
		im.save(dest, 'JPEG', quality=86)

def _crop_center(im, crop_size: Size):
	img_size = Size(*im.size)
	return im.crop((
		(img_size.x - crop_size.x) // 2,
		(img_size.y - crop_size.y) // 2,
		(img_size.x + crop_size.x) // 2,
		(img_size.y + crop_size.y) // 2
	))

def _crop_max_square(im):
	return _crop_center(im, Size(*(min(im.size),)*2))
