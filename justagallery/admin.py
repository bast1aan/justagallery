from django.contrib import admin
from django.db.models import QuerySet, Model
from django.http import HttpRequest

from . import models

class _OwnerMixin(admin.ModelAdmin):
	""" Extension to make admin use only objects that are owned by the logged in user """
	model: Model
	def get_queryset(self, request: HttpRequest):
		""" Filter on objects for current user """
		qs: QuerySet = super().get_queryset(request)
		if not request.user.is_superuser and hasattr(qs.model, 'owner'):
			qs = qs.filter(owner=request.user)
		return qs

	def save_model(self, request, obj, form, change):
		""" Set owner to current user """
		if not obj.id and hasattr(obj, 'owner') and not request.user.is_superuser:
			obj.owner = request.user
		return super().save_model(request, obj, form, change)

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		""" Only relate to objects that user owns """
		if hasattr(db_field.related_model, 'owner'):
			if not request.user.is_superuser:
				# Only show objects that user owns
				kwargs['queryset'] = db_field.related_model.objects.filter(owner=request.user)
		formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
		if db_field.name == 'owner':
			if not request.user.is_superuser:
				# Only show current user to choose as owner
				formfield.queryset = formfield.queryset.filter(pk=request.user.pk)
			if not formfield.initial:
				# Set initial value to current user
				formfield.initial = request.user.pk
			formfield.required = True  # Owner is required
		return formfield

class ThumbnailFormatAdmin(admin.ModelAdmin):
	model = models.ThumbnailFormat
	list_display = ('width', 'height', 'crop')
	fields = ('width', 'height', 'crop')
	ordering = ('width', 'height', 'crop')

class CategoryAdmin(_OwnerMixin, admin.ModelAdmin):
	model = models.Category
	fields = ['parent', 'title', 'description', 'slug', 'default_thumbnail_format', 'display_formats', 'owner']
	list_display = ('title', 'parent', 'slug', 'created_at', 'updated_at')
	ordering = ('-parent', '-created_at', )
	list_filter = ('parent',)
	search_fields = ('title',)

class ImageAdmin(_OwnerMixin, admin.ModelAdmin):
	model = models.Image
	fields = ['category', 'title', 'description', 'file', 'display_formats', 'owner']
	list_display = ('title', 'category', 'created_at', 'updated_at')
	ordering = ('-category', '-created_at', )
	list_filter = ('category',)
	search_fields = ('title',)

admin.site.register(models.ThumbnailFormat, ThumbnailFormatAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Image, ImageAdmin)

