# import os
# import subprocess


# if not os.path.isfile('/tmp/nvim'):
#     os.environ["NVIM_LISTEN_ADDRESS"] = '/tmp/nvim'
#     subprocess.Popen(["nvim", "--headless"])

import neovim
vim = neovim.attach('socket', path='/tmp/nvim')
