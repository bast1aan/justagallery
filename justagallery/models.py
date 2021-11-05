import os
import logging
from datetime import datetime

from django.contrib.auth.models import User
from django.db import models

logger = logging.getLogger(__name__)

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
	owner = models.ForeignKey(User, on_delete=models.RESTRICT, blank=True, null=True)

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
	title = models.CharField(max_length=255, blank=True)
	slug = models.CharField(max_length=255)
	file = models.FileField(upload_to=upload_to)
	description = models.TextField(blank=True)
	created_at = models.DateTimeField(default=datetime.now)
	updated_at = models.DateTimeField(default=datetime.now)
	display_formats = models.ManyToManyField(ThumbnailFormat, related_name='images', blank=True)
	owner = models.ForeignKey(User, on_delete=models.RESTRICT, blank=True, null=True)
	views = models.IntegerField(default=0)

	def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
		self.updated_at = datetime.now()
		# upload file now, to get the definitive unique file name, necessary for the slug
		self._meta.get_field('file').pre_save(self, None)
		self.slug = os.path.basename(self.file.path)
		if not self.id: # on creation
			if not self.title:
				# derive title from slug (filename)
				self.title, _ = os.path.splitext(self.slug)
			if not self.description:
				# derive description from title
				self.description = self.title
		super().save(force_insert, force_update, using, update_fields)

	def __str__(self):
		return self.title

	def delete(self, using=None, keep_parents=False):
		# Remove file on deletion of record.
		# This could be implemented much better using the storage backend delete,
		# signalling, using transactions, and what more. For now, this is Good Enough.
		path = self.file.path
		ret = super().delete(using, keep_parents)
		try:
			os.unlink(path)
		except Exception as e:
			logger.warning('Cannot remove file {}: {}'.format(path, e))
		return ret

	class Meta:
		indexes = [models.Index(fields=['slug']), models.Index(fields=['created_at'])]
		db_table = 'images'
		unique_together = ('category', 'slug')
