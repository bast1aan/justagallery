from django.contrib import admin
from django.core.exceptions import ValidationError

from . import models

class ThumbnailFormatAdmin(admin.ModelAdmin):
	model = models.ThumbnailFormat
	list_display = ('width', 'height', 'crop')
	fields = ('width', 'height', 'crop')
	ordering = ('width', 'height', 'crop')

class CategoryAdmin(admin.ModelAdmin):
	model = models.Category
	fields = ['parent', 'title', 'description', 'slug', 'default_thumbnail_format', 'display_formats']
	list_display = ('parent', 'title', 'slug', 'created_at', 'updated_at')
	ordering = ('-parent', '-created_at', )

class ImageAdmin(admin.ModelAdmin):
	model = models.Image
	fields = ['category', 'title', 'description', 'file', 'display_formats']
	list_display = ('category', 'title', 'created_at', 'updated_at')
	ordering = ('-category', '-created_at', )

admin.site.register(models.ThumbnailFormat, ThumbnailFormatAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Image, ImageAdmin)

