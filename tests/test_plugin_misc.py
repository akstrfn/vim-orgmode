#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append(u'../ftplugin')

from vim import vim

from orgmode._vim import indent_orgmode, fold_orgmode, ORGMODE

from orgmode.py3compat.encode_compatibility import *

ORGMODE.debug = True

START = True
END = False

counter = 0
class MiscTestCase(unittest.TestCase):
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
				u_encode(u'exists("g:org_debug")'): u_encode(u'0'),
				u_encode(u'exists("*repeat#set()")'): u_encode(u'0'),
				u_encode(u"v:count"): u_encode(u'0'),
				u_encode(u'b:changedtick'): u_encode(u'%d' % counter),
				u_encode(u"v:lnum"): u_encode(u'0')}
		vim.current.buffer[:] = [ u_encode(i) for i in u"""* Überschrift 1
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
		ORGMODE.start()

	def test_all_folds(self):
		# TODO this wont work on CI because now it loads my org setup probably
		vim.command("set ft=org")
		folds = [0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 4, 4, 4, 3, 1, 1, 1]
		for num, fold_lvl in enumerate(folds):
			vim_lvl = vim.command_output("echo foldlevel({})".format(num))
			self.assertEqual(fold_lvl, int(vim_lvl))

	# TODO convert these tests to something useful. These tests should be with
	# feedkeys(">>") and similar.
	def test_indent_noheading(self):
		vim.current.window.cursor = (1, 0)
		vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'1')
		indent_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 0)

	def test_indent_heading(self):
		# test first heading
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'2')
		indent_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 0)

	def test_indent_heading_middle(self):
		# test first heading
		vim.current.window.cursor = (3, 0)
		vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'3')
		indent_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'let b:indent_level = 2'))

	def test_indent_heading_middle2(self):
		# test first heading
		vim.current.window.cursor = (4, 0)
		vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'4')
		indent_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'let b:indent_level = 2'))

	def test_indent_heading_end(self):
		# test first heading
		vim.current.window.cursor = (5, 0)
		vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'5')
		indent_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'let b:indent_level = 2'))

	def test_fold_heading_start(self):
		# test first heading
		vim.current.window.cursor = (2, 0)
		vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'2')
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'let b:fold_expr = ">1"'))

	def test_fold_heading_middle(self):
		# test first heading
		vim.current.window.cursor = (3, 0)
		vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'3')
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'let b:fold_expr = 1'))

	def test_fold_heading_end(self):
		# test first heading
		vim.current.window.cursor = (5, 0)
		vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'5')
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'let b:fold_expr = 1'))

	def test_fold_heading_end_of_last_child(self):
		# test first heading
		vim.current.window.cursor = (16, 0)
		vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'16')
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		# which is also end of the parent heading <1
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'let b:fold_expr = ">3"'))

	def test_fold_heading_end_of_last_child_next_heading(self):
		# test first heading
		vim.current.window.cursor = (17, 0)
		vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'17')
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'let b:fold_expr = ">1"'))

	def test_fold_middle_subheading(self):
		# test first heading
		vim.current.window.cursor = (13, 0)
		vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'13')
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'let b:fold_expr = ">4"'))

	def test_fold_middle_subheading2(self):
		# test first heading
		vim.current.window.cursor = (14, 0)
		vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'14')
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'let b:fold_expr = 4'))

	def test_fold_middle_subheading3(self):
		# test first heading
		vim.current.window.cursor = (15, 0)
		vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'15')
		fold_orgmode()
		self.assertEqual(len(vim.CMDHISTORY), 1)
		self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'let b:fold_expr = 4'))

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(MiscTestCase)
