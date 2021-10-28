from django.contrib import admin
from django.core.exceptions import ValidationError

from . import models

class CategoryAdmin(admin.ModelAdmin):
	model = models.Category
	fields = ['parent', 'title', 'description', 'slug']
	list_display = ('parent', 'title', 'slug', 'created_at', 'updated_at')
	ordering = ('-parent', '-created_at', )

class ImageAdmin(admin.ModelAdmin):
	model = models.Image
	fields = ['category', 'title', 'description', 'slug', 'file']
	list_display = ('category', 'title', 'slug', 'created_at', 'updated_at')
	ordering = ('-category', '-created_at', )

admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Image, ImageAdmin)

