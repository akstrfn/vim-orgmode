#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys
sys.path.append(u'../ftplugin')

from vim import vim
from orgmode._vim import indent_orgmode, fold_orgmode, ORGMODE
from orgmode.py3compat.encode_compatibility import *

ORGMODE.debug = True

def foldlevel(line):
	""" Helper function to call get the fold level of a specific line """
	return int(vim.eval("foldlevel({})".format(line)))

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
		vim.command("set ft=org")
		vim.feedkeys("zM")

	def test_all_fold_levels(self):
		# first line is 0 because vim counts from 1
		folds = [0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 4, 4, 4, 3, 1, 1, 1]
		for num, fold_lvl in enumerate(folds):
			vim_lvl = foldlevel(num)
			self.assertEqual(fold_lvl, vim_lvl)

	# TODO From EditStructure: all of the following should be tested
	# ["<ah", "<<", "<{", "<ih", "<ar", "<[[", "<ir", ">ah", ">>", ">}", ">ih",
	# ">ar", ">]]", ">ir", "<C-d>", "<C-t>"]
	def test_indent_noheading(self):
		line = 1
		vim.current.window.cursor = (line, 0)
		self.assertEqual(foldlevel(line), 0)
		vim.feedkeys(">>")
		self.assertEqual(foldlevel(line), 0)
		vim.feedkeys("<<")
		self.assertEqual(foldlevel(line), 0)

	def test_indent_heading(self):
		line = 2
		vim.current.window.cursor = (line, 0)
		self.assertEqual(foldlevel(line), 1)
		vim.feedkeys(">>")
		self.assertEqual(foldlevel(line), 2)
		vim.feedkeys("<<")
		self.assertEqual(foldlevel(line), 1)

	# TODO: indent_level and fold_expr variables should be phased out in the
	# future to simplify the folding and indenting. Commented them out until
	# better way of doing this is found and implemented. Since now all of these
	# tests are broken and partially unecessary when other tests are working.
	# def test_indent_heading_middle(self):
	# 	# test first heading
	# 	vim.current.window.cursor = (3, 0)
	# 	vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'3')
	# 	indent_orgmode()
	# 	self.assertEqual(len(vim.CMDHISTORY), 1)
	# 	self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'let b:indent_level = 2'))

	# def test_indent_heading_middle2(self):
	# 	# test first heading
	# 	vim.current.window.cursor = (4, 0)
	# 	vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'4')
	# 	indent_orgmode()
	# 	self.assertEqual(len(vim.CMDHISTORY), 1)
	# 	self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'let b:indent_level = 2'))

	# def test_indent_heading_end(self):
	# 	# test first heading
	# 	vim.current.window.cursor = (5, 0)
	# 	vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'5')
	# 	indent_orgmode()
	# 	self.assertEqual(len(vim.CMDHISTORY), 1)
	# 	self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'let b:indent_level = 2'))

	# def test_fold_heading_start(self):
	# 	# test first heading
	# 	vim.current.window.cursor = (2, 0)
	# 	vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'2')
	# 	fold_orgmode()
	# 	self.assertEqual(len(vim.CMDHISTORY), 1)
	# 	self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'let b:fold_expr = ">1"'))

	# def test_fold_heading_middle(self):
	# 	# test first heading
	# 	vim.current.window.cursor = (3, 0)
	# 	vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'3')
	# 	fold_orgmode()
	# 	self.assertEqual(len(vim.CMDHISTORY), 1)
	# 	self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'let b:fold_expr = 1'))

	# def test_fold_heading_end(self):
	# 	# test first heading
	# 	vim.current.window.cursor = (5, 0)
	# 	vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'5')
	# 	fold_orgmode()
	# 	self.assertEqual(len(vim.CMDHISTORY), 1)
	# 	self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'let b:fold_expr = 1'))

	# def test_fold_heading_end_of_last_child(self):
	# 	# test first heading
	# 	vim.current.window.cursor = (16, 0)
	# 	vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'16')
	# 	fold_orgmode()
	# 	self.assertEqual(len(vim.CMDHISTORY), 1)
	# 	# which is also end of the parent heading <1
	# 	self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'let b:fold_expr = ">3"'))

	# def test_fold_heading_end_of_last_child_next_heading(self):
	# 	# test first heading
	# 	vim.current.window.cursor = (17, 0)
	# 	vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'17')
	# 	fold_orgmode()
	# 	self.assertEqual(len(vim.CMDHISTORY), 1)
	# 	self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'let b:fold_expr = ">1"'))

	# def test_fold_middle_subheading(self):
	# 	# test first heading
	# 	vim.current.window.cursor = (13, 0)
	# 	vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'13')
	# 	fold_orgmode()
	# 	self.assertEqual(len(vim.CMDHISTORY), 1)
	# 	self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'let b:fold_expr = ">4"'))

	# def test_fold_middle_subheading2(self):
	# 	# test first heading
	# 	vim.current.window.cursor = (14, 0)
	# 	vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'14')
	# 	fold_orgmode()
	# 	self.assertEqual(len(vim.CMDHISTORY), 1)
	# 	self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'let b:fold_expr = 4'))

	# def test_fold_middle_subheading3(self):
	# 	# test first heading
	# 	vim.current.window.cursor = (15, 0)
	# 	vim.EVALRESULTS[u_encode(u'v:lnum')] = u_encode(u'15')
	# 	fold_orgmode()
	# 	self.assertEqual(len(vim.CMDHISTORY), 1)
	# 	self.assertEqual(vim.CMDHISTORY[-1], u_encode(u'let b:fold_expr = 4'))

def suite():
	return unittest.TestLoader().loadTestsFromTestCase(MiscTestCase)
