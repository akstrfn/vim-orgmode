# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append(u'../ftplugin')

from vim import vim
from orgmode._vim import ORGMODE
from orgmode.py3compat.encode_compatibility import *

def foldclosed(line):
	return int(vim.eval('foldclosed({})'.format(line)))

counter = 0
class ShowHideTestCase(unittest.TestCase):
	def setUp(self):
		global counter
		counter += 1
		vim.CMDHISTORY = []
		vim.CMDRESULTS = {}
		vim.EVALHISTORY = []
		vim.EVALRESULTS = {
				# no org_todo_keywords for b
				u_encode(u'exists("b:org_todo_keywords")'): u_encode('0'),
				# global values for org_todo_keywords
				u_encode(u'exists("g:org_todo_keywords")'): u_encode('1'),
				u_encode(u'g:org_todo_keywords'): [u_encode(u'TODO'), u_encode(u'|'), u_encode(u'DONE')],
				u_encode(u'exists("g:org_debug")'): u_encode(u'0'),
				u_encode(u'exists("b:org_debug")'): u_encode(u'0'),
				u_encode(u'exists("*repeat#set()")'): u_encode(u'0'),
				u_encode(u'b:changedtick'): u_encode(u'%d' % counter),
				u_encode(u"v:count"): u_encode(u'0')}
		if not u'ShowHide' in ORGMODE.plugins:
			ORGMODE.register_plugin(u'ShowHide')
		self.showhide = ORGMODE.plugins[u'ShowHide']
		vim.current.buffer[:] = [u_encode(i) for i in u"""
* Überschrift 1
Text 1

Bla bla
** Überschrift 1.1
Text 2

Bla Bla bla
** Überschrift 1.2
Text 3

**** Überschrift 1.2.1.falsch

Bla Bla bla bla
*** Überschrift 1.2.1
* Überschrift 2
* Überschrift 3
  asdf sdf
""".split(u'\n') ]
		self.buff = vim.current.buffer[:]
		# TODO this wont work on CI because now it loads my local org setup probably
		vim.command("set ft=org")

	def tearDown(self):
		vim.command("set ft=")

	def test_no_heading_toggle_folding(self):
		vim.current.window.cursor = (1, 0)
		self.assertEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(vim.EVALHISTORY[-1], u_encode(u'feedkeys("<Tab>", "n")'))
		self.assertEqual(vim.current.window.cursor, [1, 0])

	def test_toggle_folding_first_heading_with_no_children(self):
		vim.current.buffer[:] = [u_encode(i) for i in u"""
* Überschrift 1
Text 1

Bla bla
* Überschrift 2
* Überschrift 3
  asdf sdf
""".split(u'\n') ]
		# TODO this wont work on CI because now it loads my local org setup probably'
		# refresh new vim buffer
		vim.command("set ft=org")

		vim.feedkeys("zR")
		for i in range(len(vim.current.buffer)):
			self.assertEqual(foldclosed(i), -1)
		vim.feedkeys("zM")
		for i, val in enumerate([-1, -1, 2, 2, 2, 2, -1, 7, 7]):
			self.assertEqual(foldclosed(i), val)

		vim.current.window.cursor = (2, 0)
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 1zo'))
		self.assertEqual(vim.current.window.cursor, [2, 0])

	def test_toggle_folding_close_one(self):
		vim.current.window.cursor = (13, 0)
		vim.feedkeys("zO")
		self.assertEqual(foldclosed(13), -1)
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(vim.CMDHISTORY[-2], u_encode(u'13,15foldclose!'))
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 2zo'))
		self.assertEqual(vim.current.window.cursor, [13, 0])

	def test_toggle_folding_open_one(self):
		vim.current.window.cursor = (10, 0)
		vim.feedkeys("zM")
		# self.assertEqual(foldclosed(10), 10)
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 1zo'))
		self.assertEqual(vim.current.window.cursor, [10, 0])

	def test_toggle_folding_close_multiple_all_open(self):
		vim.feedkeys("zR")
		vim.current.window.cursor = (2, 0)
		self.assertEqual(foldclosed(2), -1)
		self.assertEqual(foldclosed(6), -1)
		self.assertEqual(foldclosed(10), -1)
		self.assertEqual(foldclosed(13), -1)
		self.assertEqual(foldclosed(16), -1)
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'2,16foldclose!'))
		self.assertEqual(vim.current.window.cursor, [2, 0])

	def test_toggle_folding_open_multiple_all_closed(self):
		vim.feedkeys("zM")
		vim.current.window.cursor = (2, 0)
		self.assertEqual(foldclosed(2), 2)
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 1zo'))
		self.assertEqual(vim.current.window.cursor, [2, 0])

	def test_toggle_folding_open_multiple_first_level_open(self):
		vim.current.window.cursor = (2, 0)
		vim.feedkeys("zM")
		vim.feedkeys("zr")
		self.assertEqual(foldclosed(2), -1)
		self.assertEqual(foldclosed(6), 6)
		self.assertEqual(foldclosed(10), 10)
		self.assertEqual(foldclosed(13), 13)
		self.assertEqual(foldclosed(16), 16)
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(vim.CMDHISTORY[-2], u_encode(u'normal! 6gg1zo'))
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 10gg1zo'))
		self.assertEqual(vim.current.window.cursor, [2, 0])

	def test_toggle_folding_open_multiple_second_level_half_open(self):
		self.assertEqual(foldclosed(2), -1)
		self.assertEqual(foldclosed(6), -1)
		self.assertEqual(foldclosed(10), 10)
		self.assertEqual(foldclosed(13), 13)
		self.assertEqual(foldclosed(16), 16)

		vim.current.window.cursor = (2, 0)
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(vim.CMDHISTORY[-4], u_encode(u'normal! 6gg2zo'))
		self.assertEqual(vim.CMDHISTORY[-3], u_encode(u'normal! 10gg2zo'))
		self.assertEqual(vim.CMDHISTORY[-2], u_encode(u'normal! 13gg2zo'))
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 16gg2zo'))
		self.assertEqual(vim.current.window.cursor, [2, 0])

	def test_toggle_folding_open_multiple_other_second_level_half_open(self):
		vim.current.window.cursor = (2, 0)
		self.assertEqual(foldclosed(2), -1)
		self.assertEqual(foldclosed(6), 6)
		self.assertEqual(foldclosed(10), -1)
		self.assertEqual(foldclosed(13), 13)
		self.assertEqual(foldclosed(16), 16)
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(vim.CMDHISTORY[-4], u_encode(u'normal! 6gg2zo'))
		self.assertEqual(vim.CMDHISTORY[-3], u_encode(u'normal! 10gg2zo'))
		self.assertEqual(vim.CMDHISTORY[-2], u_encode(u'normal! 13gg2zo'))
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 16gg2zo'))
		self.assertEqual(vim.current.window.cursor, [2, 0])

	def test_toggle_folding_open_multiple_third_level_half_open(self):
		vim.current.window.cursor = (2, 0)
		self.assertEqual(foldclosed(2), -1)
		self.assertEqual(foldclosed(6), -1)
		self.assertEqual(foldclosed(10), -1)
		self.assertEqual(foldclosed(13), -1)
		self.assertEqual(foldclosed(16), 16)
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(vim.CMDHISTORY[-4], u_encode(u'normal! 6gg3zo'))
		self.assertEqual(vim.CMDHISTORY[-3], u_encode(u'normal! 10gg3zo'))
		self.assertEqual(vim.CMDHISTORY[-2], u_encode(u'normal! 13gg3zo'))
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 16gg3zo'))
		self.assertEqual(vim.current.window.cursor, [2, 0])

	def test_toggle_folding_open_multiple_other_third_level_half_open(self):
		vim.current.window.cursor = (2, 0)
		self.assertEqual(foldclosed(2), -1)
		self.assertEqual(foldclosed(6), -1)
		self.assertEqual(foldclosed(10), -1)
		self.assertEqual(foldclosed(13), 13)
		self.assertEqual(foldclosed(16), -1)
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(vim.CMDHISTORY[-4], u_encode(u'normal! 6gg3zo'))
		self.assertEqual(vim.CMDHISTORY[-3], u_encode(u'normal! 10gg3zo'))
		self.assertEqual(vim.CMDHISTORY[-2], u_encode(u'normal! 13gg3zo'))
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 16gg3zo'))
		self.assertEqual(vim.current.window.cursor, [2, 0])

	def test_toggle_folding_open_multiple_other_third_level_half_open_second_level_half_closed(self):
		vim.current.window.cursor = (2, 0)
		self.assertEqual(foldclosed(2), -1)
		self.assertEqual(foldclosed(6), 6)
		self.assertEqual(foldclosed(10), -1)
		self.assertEqual(foldclosed(13), 13)
		self.assertEqual(foldclosed(16), -1)
		self.assertNotEqual(self.showhide.toggle_folding(), None)
		self.assertEqual(vim.CMDHISTORY[-4], u_encode(u'normal! 6gg3zo'))
		self.assertEqual(vim.CMDHISTORY[-3], u_encode(u'normal! 10gg3zo'))
		self.assertEqual(vim.CMDHISTORY[-2], u_encode(u'normal! 13gg3zo'))
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 16gg3zo'))
		self.assertEqual(vim.current.window.cursor, [2, 0])

	def test_no_heading_toggle_folding_reverse(self):
		vim.current.window.cursor = (1, 0)
		self.assertEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(vim.EVALHISTORY[-1], u_encode(u'feedkeys("<Tab>", "n")'))
		self.assertEqual(vim.current.window.cursor, [1, 0])

	def test_toggle_folding_first_heading_with_no_children_reverse(self):
		vim.current.buffer[:] = [ u_encode(i) for i in u"""
* Überschrift 1
Text 1

Bla bla
* Überschrift 2
* Überschrift 3
  asdf sdf
""".split(u'\n') ]
		vim.current.window.cursor = (2, 0)
		vim.command("set ft=org")
		vim.feedkeys("zR")
		vim.command("2,5foldclose!")
		self.assertEqual(foldclosed(2), 2)
		self.assertEqual(foldclosed(6), -1)
		self.assertEqual(foldclosed(7), -1)

		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'2,5foldopen!'))
		self.assertEqual(vim.current.window.cursor, [2, 0])

	def test_toggle_folding_close_one_reverse(self):
		vim.current.window.cursor = (13, 0)
		self.assertEqual(foldclosed(13), -1)
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 13ggzc'))
		self.assertEqual(vim.current.window.cursor, [13, 0])

	def test_toggle_folding_open_one_reverse(self):
		vim.current.window.cursor = (10, 0)
		# self.assertEqual(foldclosed(10), 10)
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'10,16foldopen!'))
		self.assertEqual(vim.current.window.cursor, [10, 0])

	def test_toggle_folding_close_multiple_all_open_reverse(self):
		vim.current.window.cursor = (2, 0)
		vim.feedkeys('zR')
		self.assertEqual(foldclosed(2), -1)
		self.assertEqual(foldclosed(6), -1)
		self.assertEqual(foldclosed(10), -1)
		self.assertEqual(foldclosed(13), -1)
		self.assertEqual(foldclosed(16), -1)
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(vim.CMDHISTORY[-2], u_encode(u'normal! 13ggzc'))
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 16ggzc'))
		self.assertEqual(vim.current.window.cursor, [2, 0])

	def test_toggle_folding_open_multiple_all_closed_reverse(self):
		vim.current.window.cursor = (2, 0)
		vim.feedkeys('zM')
		self.assertEqual(foldclosed(2), 2)
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'2,16foldopen!'))
		self.assertEqual(vim.current.window.cursor, [2, 0])

	def test_toggle_folding_open_multiple_first_level_open_reverse(self):
		vim.current.window.cursor = (2, 0)
		self.assertEqual(foldclosed(2), -1)
		self.assertEqual(foldclosed(6), 6)
		self.assertEqual(foldclosed(10), 10)
		self.assertEqual(foldclosed(13), 13)
		self.assertEqual(foldclosed(16), 16)
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 2ggzc'))
		self.assertEqual(vim.current.window.cursor, [2, 0])

	def test_toggle_folding_open_multiple_second_level_half_open_reverse(self):
		vim.current.window.cursor = (2, 0)
		vim.feedkeys('zR')
		self.assertEqual(foldclosed(2), -1)
		self.assertEqual(foldclosed(6), -1)
		self.assertEqual(foldclosed(10), 10)
		self.assertEqual(foldclosed(13), 13)
		self.assertEqual(foldclosed(16), 16)
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 6ggzc'))
		self.assertEqual(vim.current.window.cursor, [2, 0])

	def test_toggle_folding_open_multiple_other_second_level_half_open_reverse(self):
		vim.current.window.cursor = (2, 0)
		self.assertEqual(foldclosed(2), -1)
		self.assertEqual(foldclosed(6), 6)
		self.assertEqual(foldclosed(10), -1)
		self.assertEqual(foldclosed(13), 13)
		self.assertEqual(foldclosed(16), 16)
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 10ggzc'))
		self.assertEqual(vim.current.window.cursor, [2, 0])

	def test_toggle_folding_open_multiple_third_level_half_open_reverse(self):
		vim.current.window.cursor = (2, 0)
		self.assertEqual(foldclosed(2), -1)
		self.assertEqual(foldclosed(6), -1)
		self.assertEqual(foldclosed(10), -1)
		self.assertEqual(foldclosed(13), -1)
		self.assertEqual(foldclosed(16), 16)
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 13ggzc'))
		self.assertEqual(vim.current.window.cursor, [2, 0])

	def test_toggle_folding_open_multiple_other_third_level_half_open_reverse(self):
		vim.current.window.cursor = (2, 0)
		self.assertEqual(foldclosed(2), -1)
		self.assertEqual(foldclosed(6), -1)
		self.assertEqual(foldclosed(10), -1)
		self.assertEqual(foldclosed(13), 13)
		self.assertEqual(foldclosed(16), -1)
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 16ggzc'))
		self.assertEqual(vim.current.window.cursor, [2, 0])

	def test_toggle_folding_open_multiple_other_third_level_half_open_second_level_half_closed_reverse(self):
		vim.current.window.cursor = (2, 0)
		self.assertEqual(foldclosed(2), -1)
		self.assertEqual(foldclosed(6), 6)
		self.assertEqual(foldclosed(10), -1)
		self.assertEqual(foldclosed(13), 13)
		self.assertEqual(foldclosed(16), -1)
		self.assertNotEqual(self.showhide.toggle_folding(reverse=True), None)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'normal! 16ggzc'))
		self.assertEqual(vim.current.window.cursor, [2, 0])

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(ShowHideTestCase)
