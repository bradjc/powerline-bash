#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import re
import argparse


def warn(msg):
    print '[powerline-bash] ', msg


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

seg_types = enum('PATH', 'CWD', 'BRANCH_CLEAN', 'BRANCH_DIRTY', 'CMD_PASSED',
                 'CMD_FAILED', 'SVN_CHANGES', 'VIRT_ENV')


symbols = {
    'compatible': {
        'separator': u'\u25B6',
        'separator_thin': u'\u276F'
    },
    'patched': {
        'separator': u'\u2B80',
        'separator_thin': u'\u2B81'
    }
}

class Color:
    # The following link is a pretty good resources for color values:
    # http://www.calmar.ws/vim/color-output.png
    """
    PATH_BG = 237  # dark grey
    PATH_FG = 250  # light grey
    CWD_FG = 254  # nearly-white grey
    SEPARATOR_FG = 244

    REPO_CLEAN_BG = 148  # a light green color
    REPO_CLEAN_FG = 0  # black
    REPO_DIRTY_BG = 161  # pink/red
    REPO_DIRTY_FG = 15  # white

    CMD_PASSED_BG = 236
    CMD_PASSED_FG = 15
    CMD_FAILED_BG = 161
    CMD_FAILED_FG = 15

    SVN_CHANGES_BG = 148
    SVN_CHANGES_FG = 22  # dark green

    VIRTUAL_ENV_BG = 35  # a mid-tone green
    VIRTUAL_ENV_FG = 22

    colors = {
        seg_types.PATH: (250, 237),
        seg_types.CWD: (254, 237),
        seg_types.BRANCH_CLEAN: (0, 148),
        seg_types.BRANCH_DIRTY: (15, 161),
        seg_types.CMD_PASSED: (15, 236),
        seg_types.CMD_FAILED: (15, 161),
        seg_types.SVN_CHANGES: (22, 148),
        seg_types.VIRT_ENV: (35, 22),
    }
    """
    """
    BG = 15

    PATH_BG = BG  # dark grey
    PATH_FG = 237  # light grey
    CWD_FG = 234  # nearly-white grey
    SEPARATOR_FG = 16

    REPO_CLEAN_BG = 254  # a light green color
    REPO_CLEAN_FG = 26  # black
    REPO_DIRTY_BG = 254  # pink/red
    REPO_DIRTY_FG = 161  # white

    CMD_PASSED_BG = BG
    CMD_PASSED_FG = 16
    CMD_FAILED_BG = BG
    CMD_FAILED_FG = 9

    SVN_CHANGES_BG = BG
    SVN_CHANGES_FG = 22  # dark green

    VIRTUAL_ENV_BG = BG  # a mid-tone green
    VIRTUAL_ENV_FG = 35

    colors = {
        seg_types.PATH: (237, 15),
        seg_types.CWD: (16, 15),
        seg_types.BRANCH_CLEAN: (26, 254),
        seg_types.BRANCH_DIRTY: (161, 254),
        seg_types.CMD_PASSED: (16, 15),
        seg_types.CMD_FAILED: (9, 15),
        seg_types.SVN_CHANGES: (22, 254),
        seg_types.VIRT_ENV: (35, 15),
    }
"""
    SEPARATOR_FG = 240
    colors = {
        seg_types.PATH: (237, 254),
        seg_types.CWD: (16, 254),
        seg_types.BRANCH_CLEAN: (26, 15),
        seg_types.BRANCH_DIRTY: (161, 15),
        seg_types.CMD_PASSED: (16, 254),
        seg_types.CMD_FAILED: (9, 254),
        seg_types.SVN_CHANGES: (22, 15),
        seg_types.VIRT_ENV: (35, 254),
    }
    def __init__ (self):
        pass

    def get (self, seg_type):
        return self.colors[seg_type]

    def getSeparator (self):
        return self.SEPARATOR_FG




class Segment:
    def __init__ (self, content, seg_type, bold=False):
        self.content = content
        self.type    = seg_type
        self.bold    = bold


class Powerline:

    LSQESCRSQ = '\\[\\e%s\\]'
    reset     = LSQESCRSQ % '[0m'
    bold      = LSQESCRSQ % '[1m'

    def __init__(self, args):
    #    self.separator = Powerline.symbols[mode]['separator']
    #    self.separator_thin = Powerline.symbols[mode]['separator_thin']
        self.segments = []
        self.args = args
        self.color = Color()

    def colorStr(self, prefix, code):
        return self.LSQESCRSQ % ('[%s;5;%sm' % (prefix, code))

    def fgcolor(self, code):
        if code == -1: return self.reset
        return self.colorStr('38', code)

    def bgcolor(self, code):
        if code == -1: return self.reset
        return self.colorStr('48', code)

    def append(self, segment):
        self.segments.append(segment)

    def draw(self):
        out = ''

        segs = self.segments
        segs.append(None)
        for i, s in zip(range(len(segs)), segs):
            if not s:
                break
            fg,bg = self.color.get(s.type)
            sep   = symbols[self.args.mode]['separator']
            sfg   = bg
            sbg   = -1

            if segs[i+1]:

                nfg,nbg = self.color.get(segs[i+1].type)
                sbg = nbg

                if bg == nbg:
                    sep = symbols[self.args.mode]['separator_thin']
                    sfg = self.color.getSeparator()
         #   else:
         #       sep = symbols[self.args.mode]['separator_thin']
          #      sbg = 15


            bold_start = self.bold if s.bold else ''
            bold_end   = self.reset if s.bold else ''

            out += ''.join((
                self.fgcolor(fg),
                self.bgcolor(bg),
                bold_start,
                s.content,
                bold_end,
                self.bgcolor(sbg),
                self.fgcolor(sfg),
                sep))

        return (out + self.reset).encode('utf-8')
            



    def add_cwd_segment(self, cwd, maxdepth, cwd_only=False):
        #powerline.append(' \\w ', 15, 237)
        home = os.getenv('HOME')
        cwd = cwd or os.getenv('PWD')
        cwd = cwd.decode('utf-8')

        if cwd.find(home) == 0:
            cwd = cwd.replace(home, '~', 1)

        if cwd[0] == '/':
            cwd = cwd[1:]

        names = cwd.split('/')
        if len(names) > maxdepth:
            names = names[:2] + [u'\u2026'] + names[2 - maxdepth:]

        if not cwd_only:
            for n in names[:-1]:
                self.append(Segment(' %s ' % n, seg_types.PATH))
        self.append(Segment(' %s ' % names[-1], seg_types.CWD, True))


    def get_hg_status(self):
        has_modified_files = False
        has_untracked_files = False
        has_missing_files = False
        output = subprocess.Popen(['hg', 'status'],
                stdout=subprocess.PIPE).communicate()[0]
        for line in output.split('\n'):
            if line == '':
                continue
            elif line[0] == '?':
                has_untracked_files = True
            elif line[0] == '!':
                has_missing_files = True
            else:
                has_modified_files = True
        return has_modified_files, has_untracked_files, has_missing_files


    def add_hg_segment(powerline, cwd):
        branch = os.popen('hg branch 2> /dev/null').read().rstrip()
        if len(branch) == 0:
            return False
  #      bg = Color.REPO_CLEAN_BG
  #      fg = Color.REPO_CLEAN_FG
        seg_type = seg_types.BRANCH_CLEAN
        has_modified_files, has_untracked_files, has_missing_files = self.get_hg_status()
        if has_modified_files or has_untracked_files or has_missing_files:
            seg_type = seg_types.BRANCH_DIRTY
  #          bg = Color.REPO_DIRTY_BG
  #          fg = Color.REPO_DIRTY_FG
            extra = ''
            if has_untracked_files:
                extra += '+'
            if has_missing_files:
                extra += '!'
            branch += (' ' + extra if extra != '' else '')
        self.append(Segment(' %s ' % branch, seg_type))
        return True


    def get_git_status(self):
        has_pending_commits = True
        has_untracked_files = False
        origin_position = ""
        output = subprocess.Popen(['git', 'status', '--ignore-submodules'],
                stdout=subprocess.PIPE).communicate()[0]
        for line in output.split('\n'):
            origin_status = re.findall(
                    r"Your branch is (ahead|behind).*?(\d+) comm", line)
            if origin_status:
                origin_position = " %d" % int(origin_status[0][1])
                if origin_status[0][0] == 'behind':
                    origin_position += u'\u21E3'
                if origin_status[0][0] == 'ahead':
                    origin_position += u'\u21E1'

            if line.find('nothing to commit') >= 0:
                has_pending_commits = False
            if line.find('Untracked files') >= 0:
                has_untracked_files = True
        return has_pending_commits, has_untracked_files, origin_position


    def add_git_segment(self, cwd):
        #cmd = "git branch 2> /dev/null | grep -e '\\*'"
        p1 = subprocess.Popen(['git', 'branch'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p2 = subprocess.Popen(['grep', '-e', '\\*'], stdin=p1.stdout, stdout=subprocess.PIPE)
        output = p2.communicate()[0].strip()
        if not output:
            return False

        branch = output.rstrip()[2:]
        has_pending_commits, has_untracked_files, origin_position = self.get_git_status()
        branch += origin_position
        if has_untracked_files:
            branch += ' +'

#        bg = Color.REPO_CLEAN_BG
 #       fg = Color.REPO_CLEAN_FG
        seg_type = seg_types.BRANCH_CLEAN
        if has_pending_commits:
            seg_type = seg_types.BRANCH_DIRTY
   #         bg = Color.REPO_DIRTY_BG
    #        fg = Color.REPO_DIRTY_FG

        self.append(Segment(' %s ' % branch, seg_type))
        return True


    def add_svn_segment(self, cwd):
    #    if not os.path.exists(os.path.join(cwd, '.svn')):
     #       return
        '''svn info:
            First column: Says if item was added, deleted, or otherwise changed
            ' ' no modifications
            'A' Added
            'C' Conflicted
            'D' Deleted
            'I' Ignored
            'M' Modified
            'R' Replaced
            'X' an unversioned directory created by an externals definition
            '?' item is not under version control
            '!' item is missing (removed by non-svn command) or incomplete
             '~' versioned item obstructed by some item of a different kind
        '''
        #TODO: Color segment based on above status codes
        try:
            #cmd = '"svn status | grep -c "^[ACDIMRX\\!\\~]"'
            p1 = subprocess.Popen(['svn', 'status'], stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
            p2 = subprocess.Popen(['grep', '-c', '^[ACDIMR\\!\\~]'],
                    stdin=p1.stdout, stdout=subprocess.PIPE)
            output = p2.communicate()[0].strip()
            if len(output) > 0 and int(output) > 0:
                changes = output.strip()
                self.append(Segment(' %s ' % changes, seg_types.SVN_CHANGES))
        except OSError:
            return False
        except subprocess.CalledProcessError:
            return False
        return True


    def add_repo_segment(self, cwd):
        for add_repo_segment in (self.add_git_segment, self.add_svn_segment, self.add_hg_segment):
            try:
                if add_repo_segment(cwd):
                    return
            except subprocess.CalledProcessError:
                pass
            except OSError:
                pass


    def add_virtual_env_segment(self, cwd):
        env = os.getenv("VIRTUAL_ENV")
        if env is None:
            return False

        env_name = os.path.basename(env)
    #    bg = Color.VIRTUAL_ENV_BG
     #   fg = Color.VIRTUAL_ENV_FG
        self.append(Segment(' %s ' % env_name, seg_types.VIRT_ENV))
        return True


    def add_root_indicator(self, error):
   #     bg = Color.CMD_PASSED_BG
   #     fg = Color.CMD_PASSED_FG
        seg_type = seg_types.CMD_PASSED
        if int(error) != 0:
            seg_type = seg_types.CMD_FAILED
   #         fg = Color.CMD_FAILED_FG
   #         bg = Color.CMD_FAILED_BG
        self.append(Segment(' \\$ ', seg_type))


def get_valid_cwd():
    """ We check if the current working directory is valid or not. Typically
        happens when you checkout a different branch on git that doesn't have
        this directory.
        We return the original cwd because the shell still considers that to be
        the working directory, so returning our guess will confuse people
    """
    try:
        cwd = os.getcwd()
    except:
        cwd = os.getenv('PWD')  # This is where the OS thinks we are
        parts = cwd.split(os.sep)
        up = cwd
        while parts and not os.path.exists(up):
            parts.pop()
            up = os.sep.join(parts)
        try:
            os.chdir(up)
        except:
            warn("Your current directory is invalid.")
            sys.exit(1)
        warn("Your current directory is invalid. Lowest valid directory: " + up)
    return cwd

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--cwd-only', action='store_true')
    arg_parser.add_argument('--mode', action='store', default='patched', choices=['patched', 'compatible'])
    arg_parser.add_argument('prev_error', nargs='?', default=0)
    args = arg_parser.parse_args()

    p = Powerline(args=args)
    cwd = get_valid_cwd()
#    add_virtual_env_segment(p, cwd)
    #p.append(Segment(powerline, ' \\u ', 250, 240))
    #p.append(Segment(powerline, ' \\h ', 250, 238))
    p.add_cwd_segment(cwd, 5, args.cwd_only)
    p.add_repo_segment(cwd)
    p.add_root_indicator(args.prev_error)
    sys.stdout.write(p.draw())

# vim: set expandtab:
