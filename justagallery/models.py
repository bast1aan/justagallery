import os
import logging
from datetime import datetime
from typing import TypeVar, Union, Iterator, Sized, Type, Generic

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from .domain import entities
from .domain.image import get_size

T = TypeVar('T', bound=models.Model)

class SizedIterator(Iterator[T], Sized): ...

logger = logging.getLogger(__name__)

def upload_to(instance: models.Model, filename: str) -> str:
	if isinstance(instance, Image):
		return "{}/{}".format(instance.category.id, filename)
	return filename

class Repository(entities.Repository[T]):
	def __init__(self, model: Type[T]):
		self.model = model
	def filter(self, **kwargs) -> SizedIterator[T]:
		return self.model.objects.filter(**kwargs)


class ThumbnailFormat(models.Model, entities.ThumbnailFormat):
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


class Category(models.Model, entities.Category):
	id = models.AutoField(primary_key=True)
	parent = models.ForeignKey('self', on_delete=models.RESTRICT, related_name='children', blank=True, null=True)
	title = models.CharField(max_length=255)
	slug = models.CharField(max_length=255)
	description = models.TextField()
	created_at = models.DateTimeField(default=datetime.now)
	updated_at = models.DateTimeField(default=datetime.now)
	default_thumbnail_format = models.ForeignKey(ThumbnailFormat, on_delete=models.RESTRICT,
		related_name='default_for_categories', blank=True, null=True)
	default_image = models.ForeignKey('Image', on_delete=models.SET_NULL, blank=True, null=True,
		related_name='default_for_category')
	display_formats = models.ManyToManyField(ThumbnailFormat, related_name='categories', blank=True)
	owner = models.ForeignKey(User, on_delete=models.RESTRICT, blank=True, null=True)
	views = models.IntegerField(default=0)
	hidden = models.BooleanField(default=False)
	private = models.BooleanField(default=False)
	sequence = models.IntegerField(default=0)

	def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
		self.updated_at = datetime.now()
		_save_sequence(self)
		super().save(force_insert, force_update, using, update_fields)

	def __str__(self):
		return self.title

	class Meta:
		indexes = [models.Index(fields=['slug']), models.Index(fields=['created_at']),
			models.Index(fields=['sequence'])]
		db_table = 'categories'
		unique_together = ('parent', 'slug')
		ordering = ('sequence',)


class Image(models.Model, entities.Image):
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
	sequence = models.IntegerField(default=0)
	width = models.IntegerField(default=0)
	height = models.IntegerField(default=0)

	def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
		self.updated_at = datetime.now()
		if not self.file._committed:  # new file uploaded
			# first retrieve width and height from temporary file
			self.width, self.height = get_size(self.file.file.file.name)
			# upload file now, to get the definitive unique file name, necessary for the slug
			self._meta.get_field('file').pre_save(self, None)
			self.slug = os.path.basename(self.file.path)
		if not self.id: # on creation of record
			if not self.title:
				# derive title from slug (filename)
				self.title, _ = os.path.splitext(self.slug)
			if not self.description:
				# derive description from title
				self.description = self.title
		_save_sequence(self)
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
		indexes = [models.Index(fields=['slug']), models.Index(fields=['created_at']),
			models.Index(fields=['sequence'])]
		db_table = 'images'
		unique_together = ('category', 'slug')
		ordering = ('sequence',)

def _save_sequence(instance: Union[Category, Image]):
	"""
		Calculates sequence, based on category of instance and the previous sequence,
		and sets it on the instance, only if it is to be created
	"""
	if not instance.id and not instance.sequence:
		if category := getattr(instance, 'category', None):
			category_q = Q(category=category)
		else:
			category_q = Q(parent=instance.parent)
		prev_instance = instance.__class__.objects.filter(category_q).order_by('-sequence').first()
		if prev_instance and prev_instance.sequence:
			prev_sequence = prev_instance.sequence
		else:
			prev_sequence = 0
		instance.sequence = prev_sequence + 10
