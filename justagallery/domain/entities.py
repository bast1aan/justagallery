"""
	Entities used in the domain.
	These are abstract interfaces defining their behaviour without
	depending on the implementation and underlying framework.
"""

from datetime import datetime
from typing import TypeVar, Optional, Sized, Generic, Iterator

T = TypeVar('T')

class SetIterator(Iterator[T], Sized):
	...

class EntitySet(Generic[T]):
	def all(self) -> SetIterator[T]:
		...
	def first(self) -> Optional[T]:
		...

class Repository(Generic[T]):
	def filter(self, **kwargs) -> EntitySet[T]:
		...

class ThumbnailFormat:
	id: int
	width: int
	height: int
	crop: bool

class Category:
	id: int
	parent: 'Category'
	title: str
	slug: str
	description: str
	created_at: datetime
	updated_at: datetime
	default_thumbnail_format: ThumbnailFormat
	default_image: 'Image'
	display_formats: EntitySet[ThumbnailFormat]
	images: EntitySet['Image']
	children: EntitySet['Category']
	views: int

class Image:
	id: int
	category: Category
	title: str
	slug: str
	description: str
	created_at: datetime
	updated_at: datetime
	display_formats: EntitySet[ThumbnailFormat]
	views: int