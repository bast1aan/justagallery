from datetime import datetime

from django.db import models

def upload_to(instance: models.Model, filename: str) -> str:
	if isinstance(instance, Image):
		return "{}/{}".format(instance.category.id, filename)
	return filename


class ThumbnailFormat(models.Model):
	id = models.AutoField(primary_key=True)
	width = models.IntegerField()
	height = models.IntegerField()
	crop = models.BooleanField(default=False)

	class Meta:
		db_table = 'thumbnail_formats'

	def __str__(self):
		return "{}x{}{}".format(
			self.width,
			self.height,
			' (Cropped)' if self.crop else ''
		)


class Category(models.Model):
	id = models.AutoField(primary_key=True)
	parent = models.ForeignKey('self', on_delete=models.RESTRICT, related_name='children', blank=True, null=True)
	title = models.CharField(max_length=255)
	slug = models.CharField(max_length=255)
	description = models.TextField()
	created_at = models.DateTimeField(default=datetime.now)
	updated_at = models.DateTimeField(default=datetime.now)
	default_thumbnail_format = models.ForeignKey(ThumbnailFormat, on_delete=models.RESTRICT,
		related_name='default_for_categories', blank=True, null=True)
	display_formats = models.ManyToManyField(ThumbnailFormat, related_name='categories', blank=True)

	def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
		self.updated_at = datetime.now()
		super().save(force_insert, force_update, using, update_fields)

	def __str__(self):
		return self.title

	class Meta:
		indexes = [models.Index(fields=['slug']), models.Index(fields=['created_at'])]
		db_table = 'categories'
		unique_together = ('parent', 'slug')


class Image(models.Model):
	id = models.AutoField(primary_key=True)
	category = models.ForeignKey(Category, on_delete=models.RESTRICT, related_name='images')
	title = models.CharField(max_length=255)
	slug = models.CharField(max_length=255)
	file = models.FileField(upload_to=upload_to)
	description = models.TextField()
	created_at = models.DateTimeField(default=datetime.now)
	updated_at = models.DateTimeField(default=datetime.now)
	display_formats = models.ManyToManyField(ThumbnailFormat, related_name='images', blank=True)

	def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
		self.updated_at = datetime.now()
		super().save(force_insert, force_update, using, update_fields)

	def __str__(self):
		return self.title

	class Meta:
		indexes = [models.Index(fields=['slug']), models.Index(fields=['created_at'])]
		db_table = 'images'
		unique_together = ('category', 'slug')
