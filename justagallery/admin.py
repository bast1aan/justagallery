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
	list_display = ('title', 'parent', 'slug', 'created_at', 'updated_at')
	ordering = ('-parent', '-created_at', )
	list_filter = ('parent',)
	search_fields = ('title',)

class ImageAdmin(admin.ModelAdmin):
	model = models.Image
	fields = ['category', 'title', 'description', 'file', 'display_formats']
	list_display = ('title', 'category', 'created_at', 'updated_at')
	ordering = ('-category', '-created_at', )
	list_filter = ('category',)
	search_fields = ('title',)

admin.site.register(models.ThumbnailFormat, ThumbnailFormatAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Image, ImageAdmin)

