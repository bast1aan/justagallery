"""
	Entities used in the domain.
	These are abstract interfaces defining their behaviour without
	depending on the implementation and underlying framework.
"""

from datetime import datetime
from typing import TypeVar, Optional, Sized, Generic, Iterator, Protocol

T = TypeVar('T')

class SetIterator(Iterator[T], Sized):
	...

class EntityManager(Generic[T]):
	""" Non-iteratable version of EntitySet """
	def all(self) -> 'EntitySet[T]':
		...
	def first(self) -> Optional[T]:
		...
	def count(self) -> int:
		...
	def filter(self, **kwargs) -> 'EntitySet[T]':
		...

class EntitySet(EntityManager[T], SetIterator[T]):
	...

class Repository(Generic[T]):
	def filter(self, **kwargs) -> EntitySet[T]:
		...

class User(Protocol):
	pk: int
	is_anonymous: bool
	def get_username(self) -> str: ...

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
	display_formats: EntityManager[ThumbnailFormat]
	images: EntityManager['Image']
	children: EntityManager['Category']
	views: int
	owner: User
	hidden: bool
	private: bool

class Image:
	id: int
	category: Category
	title: str
	slug: str
	description: str
	created_at: datetime
	updated_at: datetime
	display_formats: EntityManager[ThumbnailFormat]
	owner: User
