Powerline style prompt for Bash
===============================

A [Powerline](https://github.com/Lokaltog/vim-powerline) like prompt for Bash:

![MacVim+Solarized+Powerline+CtrlP](https://raw.github.com/milkbikis/dotfiles-mac/master/bash-powerline-screenshot.png)

Features
--------

The prompt determines if you are inside of a repository and if so displays useful information.

### Git
*  Displays the current branch with color to indicate whether the branch is dirty or not
*  A '+' appears when untracked files are present
*  When the local branch differs from the remote, the difference in number of commits is
shown along with '⇡' or '⇣' indicating whether a git push or pull is pending

### Svn
*  Shows the number of locally changed files

### Mercurial
*  Shows the current branch also with colors indicating whether the branch is dirty or not
*  Indicates if files are added or missing

### Other
*  Changes color if the last command exited with a failure code
*  If you're too deep into a directory tree, shortens the displayed path with an ellipsis
*  Shows the current Python [virtualenv](http://www.virtualenv.org/) environment
*  It's all done in a Python script, so you could go nuts with it
*  Colors are configurable

Setup
-----

1. This script uses ANSI color codes to display colors in a terminal.
These are notoriously non-portable, so may not work for you out of the box,
but try setting your $TERM to xterm-256color, because that works for me.
2. This script uses unicode characters not normally present in font. You should
either download a patched font or patch your own and then set your terminal to use the patched version.
See https://github.com/Lokaltog/vim-powerline/wiki/Patched-fonts
3. Clone this repository somewhere:
4. Edit the following with the path to powerline-bash.py and add it to your .bashrc:

        function _update_ps1()
        {
           export PS1="$(<path to repo>/powerline-bash.py $?)"
        }

        export PROMPT_COMMAND="_update_ps1"
        
Options
-------
~~~~~
usage: powerline-bash.py [-h] [--cwd-only] [--mode {patched,compatible}]
                         [--config config_file]
                         [prev_error]

positional arguments:
  prev_error            return code of the previous command

optional arguments:
  -h, --help            show this help message and exit
  --cwd-only            display only the current directory and none of the
                        path.
  --mode {patched,compatible}
                        in compatible mode characters in non patched fonts
                        will be used
  --config config_file  path to color configuration file
~~~~~~


Color Configuration
-------------------

To use a different color scheme, create a `.powerline-bash` file in your home directory.
This is a json file, specified like so:

~~~~~
{
    "segments": {
        "path":         [16, 254],
        "cwd":          [16, 254],
        "branch_clean": [26, 15],
        "branch_dirty": [161, 15],
        "cmd_passed":   [16, 254],
        "cmd_failed":   [9, 254],
        "svn_changes":  [26, 15],
        "virtual_env":  [35, 254]
    },
    "other": {
        "separator": 240
    }
}
~~~~~

The first number in the list is the foreground color and the second is the background.
The color numbers are from this page: http://www.calmar.ws/vim/color-output.png

