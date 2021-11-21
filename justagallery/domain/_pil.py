import os
import PIL.Image

from . import image


class Image(image.Image):
	""" Implementation using PIL (Pillow) """

	@staticmethod
	def create_thumbnail(orig: str, dest: str, size: image.Size, crop: bool) -> None:
		destdir = os.path.dirname(dest)
		if not os.path.exists(destdir):
			os.makedirs(destdir)
		with PIL.Image.open(orig) as im:
			if crop:
				im = Image._crop_max_square(im)
			im.thumbnail(size)
			im.save(dest, 'JPEG', quality=86)

	@staticmethod
	def get_size(path: str) -> image.Size:
		with PIL.Image.open(path) as im:
			return image.Size(*im.size)

	@staticmethod
	def _crop_center(im, crop_size: image.Size):
		img_size = image.Size(*im.size)
		return im.crop((
			(img_size.x - crop_size.x) // 2,
			(img_size.y - crop_size.y) // 2,
			(img_size.x + crop_size.x) // 2,
			(img_size.y + crop_size.y) // 2
		))

	@staticmethod
	def _crop_max_square(im):
		return Image._crop_center(im, image.Size(*(min(im.size),)*2))



