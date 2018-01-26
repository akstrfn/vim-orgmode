import json

import neovim
vim = neovim.attach('child', argv=json.loads('["nvim", "--embed"]'))
