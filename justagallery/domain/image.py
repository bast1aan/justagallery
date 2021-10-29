import os
from typing import NamedTuple

from PIL import Image

class Size(NamedTuple):
	x: int
	y: int

def create_thumbnail(orig: str, dest: str, size: Size):
	destdir = os.path.dirname(dest)
	if not os.path.exists(destdir):
		os.makedirs(destdir)
	with Image.open(orig) as im:
		im.thumbnail(size)
		im.save(dest, 'JPEG', quality=86)