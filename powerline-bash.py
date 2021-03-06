#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import socket
import subprocess
import sys
import re
import argparse
import json


def warn(msg):
    print('[powerline-bash] {}'.format(msg))

def enum(**enums):
    return type('Enum', (), enums)

seg_types = enum(PATH='path',
                 CWD='cwd',
                 BRANCH_CLEAN='branch_clean',
                 BRANCH_DIRTY='branch_dirty',
                 CMD_PASSED='cmd_passed',
                 CMD_FAILED='cmd_failed',
                 SVN_CHANGES='svn_changes',
                 VIRT_ENV='virtual_env',
                 HOSTNAME='hostname')

symbols = {
    'compatible': {
        'separator': u'\u25B6',
        'separator_thin': u'\u276F',
        'separator_right': u'\u25C0',
        'separator_right_thin': u'\u276E',
        'ellipsis': u'\u2026',
    },
    'patched': {
        'separator': u'\u2B80',
        'separator_thin': u'\u2B81',
        'separator_right': u'\u2B82',
        'separator_right_thin': u'\u2B83',
        'ellipsis': u'\u2026',
    }
}

class Color:
    # The following link is a pretty good resources for color values:
    # http://www.calmar.ws/vim/color-output.png

    colors = {
        'segments': {
            'path':         [250, 237],
            'cwd':          [254, 237],
            'branch_clean': [0,  148],
            'branch_dirty': [15, 161],
            'cmd_passed':   [15, 236],
            'cmd_failed':   [15, 161],
            'svn_changes':  [22, 148],
            'virtual_env':  [35, 22],
            'hostname':     [0, 38],
        },
        'other': {
            'separator': 244,
        }
    }
    def __init__ (self, config):

        try:
            config_filename = config or os.path.expanduser("~") + \
                              '/.config/powerline-bash'
            with open(config_filename, 'r') as f:
                user_colors = json.load(f)
        except ValueError:
            warn('Could not parse config file.')
            return
        except:
            return


        # merge the config file settings in with the defaults
        for chr_type,chr_names in user_colors.items():
            for chr_name,color_range in chr_names.items():
                self.colors[chr_type][chr_name] = color_range

    def get (self, seg_type):
        return self.colors['segments'][seg_type]

    def getSeparator (self):
        return self.colors['other']['separator']


class Segment:
    def __init__ (self, content, seg_type, bold=False):
        self.content = content
        self.type    = seg_type
        self.bold    = bold

    def width (self):
        return len(self.content) + 1


class Powerline:

    LSQESCRSQ = '\\[\\e%s\\]'
    reset     = LSQESCRSQ % '[0m'
    bold      = LSQESCRSQ % '[1m'

    def __init__(self, args, cwd):
        self.segmentsl = []
        self.segmentsr = []
        self.segmentsd = []
        self.args      = args
        self.color     = Color(config=args.config)
        self.cwd       = cwd
        self.maxdepth  = 5
        self.width     = int(args.width)

    def colorStr(self, prefix, code):
        return self.LSQESCRSQ % ('[%s;5;%sm' % (prefix, code))

    def fgcolor(self, code):
        if code == -1: return self.reset
        return self.colorStr('38', code)

    def bgcolor(self, code):
        if code == -1: return self.reset
        return self.colorStr('48', code)

    def append(self, segment):
        self.segmentsl.append(segment)

    def append_right(self, segment):
        self.segmentsr.append(segment)

    def append_down(self, segment):
        self.segmentsd.append(segment)

    def draw(self):
        left_len  = sum(c.width() for c in self.segmentsl)
        right_len = sum(c.width() for c in self.segmentsr)

        out = ''

        segs = self.segmentsl
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
        out += self.reset

        outr = ''

        segs = self.segmentsr
        segs.append(None)
        for i, s in zip(range(len(segs)), segs):
            if not s:
                break
            fg,bg = self.color.get(s.type)
            sep   = symbols[self.args.mode]['separator_right']
            sfg   = bg
            sbg   = -1

            if segs[i+1]:

                nfg,nbg = self.color.get(segs[i+1].type)
                sbg = nbg

                if bg == nbg:
                    sep = symbols[self.args.mode]['separator_right_thin']
                    sfg = self.color.getSeparator()

            bold_start = self.bold if s.bold else ''
            bold_end   = self.reset if s.bold else ''

            outr = ''.join((
                self.bgcolor(sbg),
                self.fgcolor(sfg),
                sep,
                self.fgcolor(fg),
                self.bgcolor(bg),
                bold_start,
                s.content,
                bold_end)) + outr
        outr += self.reset

        outd = ''
        segs = self.segmentsd
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

            bold_start = self.bold if s.bold else ''
            bold_end   = self.reset if s.bold else ''

            outd += ''.join((
                self.fgcolor(fg),
                self.bgcolor(bg),
                bold_start,
                s.content,
                bold_end,
                self.bgcolor(sbg),
                self.fgcolor(sfg),
                sep))
        outd += self.reset


    #    print left_len
    #    print right_len
        mid_len = self.width - left_len - right_len
    #    print mid_len
        mid = ' '*mid_len


        return (out + mid + outr + '\n' + outd)


    def add_cwd_segment(self):
        #powerline.append(' \\w ', 15, 237)
        home = os.getenv('HOME')
        cwd = self.cwd or os.getenv('PWD')
        #cwd = cwd.decode('utf-8')

        if cwd.find(home) == 0:
            cwd = cwd.replace(home, '~', 1)

        if cwd[0] == '/':
            cwd = cwd[1:]

        names = cwd.split('/')

        # Get the total number of characters in the string
        total_chars = sum(len(x) for x in names)
        total_chars += (len(names) * 3)

        # Truncate only if width would exceed the width of the terminal minus
        # a buffer.
        if float(total_chars) > 0.8 * float(self.width):
            names = names[:2] + [symbols[self.args.mode]['ellipsis']] + \
                    names[2 - self.maxdepth:]

        if len(names) == 1 and names[0] == '':
            # If we are in the root directory display just the /
            names[0] = '/'

        if not self.args.cwd_only:
            for n in names[:-1]:
                self.append(Segment(' %s ' % n, seg_types.PATH))
        self.append(Segment(' %s ' % names[-1], seg_types.CWD, True))


    def get_hg_status(self):
        has_modified_files = False
        has_untracked_files = False
        has_missing_files = False
        output = subprocess.Popen(['hg', 'status'],
                stdout=subprocess.PIPE).communicate()[0].decode('utf-8')
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


    def add_hg_segment(self):
        branch = os.popen('hg branch 2> /dev/null').read().rstrip()
        if len(branch) == 0:
            return False
        seg_type = seg_types.BRANCH_CLEAN
        has_mod_files, has_untr_files, has_missing_files = self.get_hg_status()
        if has_mod_files or has_untr_files or has_missing_files:
            seg_type = seg_types.BRANCH_DIRTY
            extra = ''
            if has_untr_files:
                extra += '+'
            if has_missing_files:
                extra += '!'
            branch += (' ' + extra if extra != '' else '')
        self.append_right(Segment(' %s ' % branch, seg_type))
        return True


    def get_git_status(self):
        has_pending_commits = True
        has_untracked_files = False
        origin_position = ""
        output = subprocess.Popen(['git', 'status', '--ignore-submodules'],
                stdout=subprocess.PIPE).communicate()[0].decode('utf-8')
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


    def add_git_segment(self):
        #cmd = "git branch 2> /dev/null | grep -e '\\*'"
        p1 = subprocess.Popen(['git', 'branch'], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        p2 = subprocess.Popen(['grep', '-e', '\\*'], stdin=p1.stdout,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p2.communicate()[0].decode('utf-8').strip()
        if not output:
            return False

        branch = output.rstrip()[2:]
        has_pend_com, has_untr, origin_pos = self.get_git_status()
        branch += origin_pos
        if has_untr:
            branch += ' +'

        seg_type = seg_types.BRANCH_DIRTY if has_pend_com \
              else seg_types.BRANCH_CLEAN

        self.append_right(Segment(' %s ' % branch, seg_type))
        return True


    def add_svn_segment(self):
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
            p0 = subprocess.Popen(['svn', 'info'], stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
            output = p0.communicate()[0].decode('utf-8')
            if p0.returncode != 0:
                return False
            p1 = subprocess.Popen(['svn', 'status'], stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
            p2 = subprocess.Popen(['grep', '-c', '^[ACDIMR\\!\\~]'],
                    stdin=p1.stdout, stdout=subprocess.PIPE)
            output = p2.communicate()[0].decode('utf-8').strip()
            if not output:
                return False
            if len(output) > 0 and int(output) > 0:
                changes = output.strip()
                self.append_right(Segment(' %s ' % changes,
                                          seg_types.SVN_CHANGES))
        except OSError:
            return False
        except subprocess.CalledProcessError:
            return False
        return True


    def add_repo_segment(self):
        for add_repo_segment in (self.add_git_segment,
                                 self.add_svn_segment,
                                 self.add_hg_segment):
            try:
                if add_repo_segment():
                    return
            except subprocess.CalledProcessError:
                pass
            except OSError:
                pass


    def add_virtual_env_segment(self):
        env = os.getenv("VIRTUAL_ENV")
        if env is None:
            return False

        env_name = os.path.basename(env)
        self.append(Segment(' %s ' % env_name, seg_types.VIRT_ENV))
        return True


    def add_hostname_segment (self):
        host = socket.gethostname()

        if len(host) > 8:
            host = host[0:8] + symbols[self.args.mode]['ellipsis']

        self.append_right(Segment(' %s ' % host, seg_types.HOSTNAME))


    def add_root_indicator(self):
        seg_type = seg_types.CMD_PASSED
        if int(self.args.prev_error) != 0:
            seg_type = seg_types.CMD_FAILED
        self.append_down(Segment(' $ ', seg_type))


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
    arg_parser.add_argument('--cwd-only',
                            action='store_true',
                            help='display only the current directory and none \
                                  of the path.')
    arg_parser.add_argument('--mode',
                            action='store',
                            default='patched',
                            choices=['patched', 'compatible'],
                            help='in compatible mode characters in non patched \
                                  fonts will be used. Use this if you do not \
                                  have a patched font for your terminal.')
    arg_parser.add_argument('prev_error',
                            nargs='?',
                            default=0,
                            help='return code of the previous command')
    arg_parser.add_argument('--config',
                            action='store',
                            help='path to color configuration file',
                            metavar='config_file')
    arg_parser.add_argument('--width',
                            action='store',
                            help='character width of the terminal',
                            required=True)
    args = arg_parser.parse_args()

    try:
        p = Powerline(args=args, cwd=get_valid_cwd())
        p.add_virtual_env_segment()
        p.add_cwd_segment()

        p.add_hostname_segment()
        p.add_repo_segment()

        p.add_root_indicator()
        sys.stdout.write(p.draw())
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass

