from typing import Protocol, Union

from django.contrib import admin
from django.contrib.admin import FieldListFilter, RelatedFieldListFilter
from django.contrib.auth.models import User
from django.db.models import QuerySet, Model, Q
from django import forms
from django.http import HttpRequest

from . import models


class HasUser(Protocol):
	user: User


class _OwnerListFilter(RelatedFieldListFilter):
	""" Related field list filter that only shows choices that user owns """
	def field_choices(self, field, request: HasUser, model_admin):
		if not request.user.is_superuser:
			ordering = self.field_admin_ordering(field, request, model_admin)
			return field.get_choices(include_blank=False, ordering=ordering, limit_choices_to={'owner': request.user})
		else:
			return super().field_choices(field, request, model_admin)

FieldListFilter.register(lambda f: f.remote_field and hasattr(f.related_model, 'owner'), _OwnerListFilter,
	take_priority=True)


class _OwnerMixin(admin.ModelAdmin):
	""" Extension to make admin use only objects that are owned by the logged in user """
	model: Model
	def get_queryset(self, request: HasUser):
		""" Filter on objects for current user """
		qs: QuerySet = super().get_queryset(request)
		if not request.user.is_superuser and hasattr(qs.model, 'owner'):
			qs = qs.filter(owner=request.user)
		return qs

	def save_model(self, request: HasUser, obj, form, change):
		""" Set owner to current user """
		if not obj.id and hasattr(obj, 'owner') and not request.user.is_superuser:
			obj.owner = request.user
		return super().save_model(request, obj, form, change)

	def formfield_for_foreignkey(self, db_field, request: HasUser, **kwargs):
		""" Only relate to objects that user owns """
		if hasattr(db_field.related_model, 'owner'):
			if not request.user.is_superuser:
				# Only show objects that user owns
				if 'queryset' not in kwargs:
					kwargs['queryset'] = db_field.related_model.objects
				kwargs['queryset'].filter(owner=request.user)
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


class CategoryForm(forms.ModelForm):
	instance: models.Category
	images = forms.FileField(
		widget=forms.ClearableFileInput(attrs={"multiple": True}),
		label="Add images",
		required=False,
	)

	def save_images(self, request: HasUser, category: models.Category):
		"""Process each uploaded image."""
		for upload in self.files.getlist("images"):
			image = models.Image(category=category, file=upload, owner=request.user)
			image.save()



class ThumbnailFormatAdmin(admin.ModelAdmin):
	model = models.ThumbnailFormat
	list_display = ('width', 'height', 'crop')
	fields = ('width', 'height', 'crop')
	ordering = ('width', 'height', 'crop')


class CategoryAdmin(_OwnerMixin, admin.ModelAdmin):
	model = models.Category
	fields = ['parent', 'title', 'description', 'slug', 'default_thumbnail_format', 'display_formats', 'owner',
		'default_image', 'hidden', 'private', 'sequence', 'images']
	list_display = ('title', 'parent', 'slug', 'created_at', 'updated_at')
	ordering = ('-parent', 'sequence', )
	list_filter = ('parent',)
	search_fields = ('title',)
	form = CategoryForm

	def save_related(self, request, form: CategoryForm, formsets, change):
		super().save_related(request, form, formsets, change)
		form.save_images(request, form.instance)

	def formfield_for_foreignkey(self, db_field, request: Union[HttpRequest, HasUser], **kwargs):
		if db_field.name == 'default_image':
			try:
				category_id = int(request.resolver_match.kwargs['object_id'])
			except Exception:
				category_id = 0  # would select nothing
			kwargs['queryset'] = models.Image.objects.filter(
				Q(category_id=category_id) | Q(category__parent_id=category_id))
		formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
		return formfield

	def formfield_for_dbfield(self, db_field, request, **kwargs):
		formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
		formfield.widget.can_delete_related = False
		formfield.widget.can_change_related = False
		formfield.widget.can_add_related = False
		formfield.widget.can_view_related = False
		return formfield


class ImageAdmin(_OwnerMixin, admin.ModelAdmin):
	model = models.Image
	fields = ['category', 'title', 'description', 'file', 'display_formats', 'owner', 'sequence']
	list_display = ('title', 'category', 'created_at', 'updated_at')
	ordering = ('-category', 'sequence', )
	list_filter = ('category',)
	search_fields = ('title',)


admin.site.register(models.ThumbnailFormat, ThumbnailFormatAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Image, ImageAdmin)

