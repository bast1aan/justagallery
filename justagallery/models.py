from datetime import datetime

from django.db import models


class Category(models.Model):
	id = models.AutoField(primary_key=True)
	parent = models.ForeignKey('self', on_delete=models.RESTRICT, related_name='children', blank=True, null=True)
	title = models.CharField(max_length=255)
	slug = models.CharField(max_length=255)
	description = models.TextField()
	created_at = models.DateTimeField(default=datetime.now)
	updated_at = models.DateTimeField(default=datetime.now)

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
	file = models.FileField()
	description = models.TextField()
	created_at = models.DateTimeField(default=datetime.now)
	updated_at = models.DateTimeField(default=datetime.now)

	def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
		self.updated_at = datetime.now()
		super().save(force_insert, force_update, using, update_fields)

	def __str__(self):
		return self.title

	class Meta:
		indexes = [models.Index(fields=['slug']), models.Index(fields=['created_at'])]
		db_table = 'images'
		unique_together = ('category', 'slug')
