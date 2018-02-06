import json

import neovim
vim = neovim.attach('child', argv=json.loads('["nvim", "--embed"]'))

# HACKS BEGIN: make tests work before all of them are converted to better ones
# now that we have neovim for testing
vim.CMDHISTORY = []
vim.CMDRESULTS = {}
vim.EVALHISTORY = []
vim.EVALRESULTS = {
		u'exists("g:org_debug")': 0,
		u'exists("b:org_debug")': 0,
		u'exists("*repeat#set()")': 0,
		u'exists("b:org_plugins")': 0,
		u'exists("g:org_plugins")': 0,
		u'b:changedtick': 0,
		}


def eval_decorator(fun):
	""" capture eval history """
	def tmp_fun(*args, **kwargs):
		vim.EVALHISTORY.extend(args)
		return fun(*args, **kwargs)
	return tmp_fun


def command_decorator(fun):
	""" capture command history """
	def tmp_fun(*args, **kwargs):
		vim.CMDHISTORY.extend(args)
		return fun(*args, **kwargs)
	return tmp_fun

vim.eval = eval_decorator(vim.eval)
vim.command = command_decorator(vim.command)
# HACKS END
