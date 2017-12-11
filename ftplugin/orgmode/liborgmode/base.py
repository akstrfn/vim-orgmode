# -*- coding: utf-8 -*-

"""
	base
	~~~~~~~~~~

	Here are some really basic data structures that are used throughout
	the liborgmode.
"""

try:
	from collections import UserList
except:
	from UserList import UserList

import collections
import sys
from orgmode.py3compat.unicode_compatibility import *


def flatten_list(lst):
	""" Flattens a list

	Args:
		lst (iterable): An iterable that will is non-flat

	Returns:
		list: Flat list
	"""
	# TODO write tests
	def gen_lst(item):
		if isinstance(item, basestring) or isinstance(item, bytes):
			yield item
		elif isinstance(item, collections.Iterable):
			# yield from would be so nice... but c'est la vie
			for val in item:
				for final in gen_lst(val):
					yield final
		else:
			yield item
	return [i for i in gen_lst(lst)]


class Direction():
	u"""
	Direction is used to indicate the direction of certain actions.

	Example: it defines the direction headings get parted in.
	"""
	FORWARD = 1
	BACKWARD = 2


class MultiPurposeList(UserList):
	u"""
	A Multi Purpose List is a list that calls a user defined hook on
	change. The implementation is very basic - the hook is called without any
	parameters. Otherwise the Multi Purpose List can be used like any other
	list.

	The member element "data" can be used to fill the list without causing the
	list to be marked dirty. This should only be used during initialization!
	"""

	def __init__(self, initlist=None, on_change=None):
		UserList.__init__(self, initlist)
		self._on_change = on_change

	def _changed(self):
		u""" Call hook """
		if callable(self._on_change):
			self._on_change()

	def __setitem__(self, i, item):
		if sys.version_info < (3, ) and isinstance(i, slice):
			start, stop, _ = i.indices(len(self))
			UserList.__setslice__(self, start, stop, item)
		else:
			UserList.__setitem__(self, i, item)
		self._changed()

	def __delitem__(self, i):
		if sys.version_info < (3, ) and isinstance(i, slice):
			start, stop, _ = i.indices(len(self))
			UserList.__delslice__(self, start, stop)
		else:
			UserList.__delitem__(self, i)
		self._changed()

	def __getitem__(self, i):
		if sys.version_info < (3, ):
			if isinstance(i, slice):
				# TODO Return just a list. Why?
				return [self[i] for i in range(*i.indices(len(self)))]
				# return UserList([self[i] for i in range(*i.indices(len(self)))])
		return UserList.__getitem__(self, i)

	# NOTE: These wrappers are necessary because of python 2
	def __setslice__(self, i, j, other):
		self.__setitem__(slice(i, j), other)

	def __delslice__(self, i, j):
		self.__delitem__(slice(i, j))

	def __getslice__(self, i, j):
		return self.__getitem__(slice(i, j))

	def __iadd__(self, other):
		res = UserList.__iadd__(self, other)
		self._changed()
		return res

	def __imul__(self, n):
		res = UserList.__imul__(self, n)
		self._changed()
		return res

	def append(self, item):
		UserList.append(self, item)
		self._changed()

	def insert(self, i, item):
		UserList.insert(self, i, item)
		self._changed()

	def pop(self, i=-1):
		item = self[i]
		del self[i]
		return item

	def remove(self, item):
		self.__delitem__(self.index(item))

	def reverse(self):
		UserList.reverse(self)
		self._changed()

	def sort(self, *args, **kwds):
		UserList.sort(self, *args, **kwds)
		self._changed()

	def extend(self, other):
		UserList.extend(self, other)
		self._changed()


def get_domobj_range(content="", position=0, direction=Direction.FORWARD, identify_fun=None):
	""" Get the start and end line number of the dom obj lines from content.

	Args:
		content (str): String to be recognized dom obj.
		position (int): Line number in content where the search starts
		direction (Direction): Search direction.
		identify_fun: An identify function to recognize dom obj(Heading,
			Checkbox) title string.

	Returns:
		Tuple: (start, end) line numbers for the recognized dom obj or (None,
			None) if they were not found.
	"""
	len_cb = len(content)

	if len_cb < position < 0:
		raise IndexError("position is not in the range of the content")

	start = None
	end = None

	if direction == Direction.FORWARD:
		for line_no in range(position, len_cb):
			if identify_fun(content[line_no]):
				if start is None:
					start = line_no
				elif end is None:
					end = line_no - 1
					break
	else:
		# TODO: this searches with position being the middle, I've just
		# refactored it but considering that forward search is different this
		# behaviour can be confusing? Few tests are failing when there is no
		# position + 1. This behaviour is very likely incorrect.
		for line_no in reversed(range(position + 1)):
			if identify_fun(content[line_no]):
				start = line_no
				break
		for line_no in range(position + 1, len_cb):
			if identify_fun(content[line_no]):
				end = line_no - 1
				break

	return (start, end)

# vim: set noexpandtab:
