### This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from sos.plugins import Plugin, RedHatPlugin
import time
import os

class process(Plugin, RedHatPlugin):
    """process information
    """
    def setup(self):
        self.collectExtOutput("/bin/ps auxwww", root_symlink = "ps")
        self.collectExtOutput("/bin/ps auxwwwm")
        self.collectExtOutput("/bin/ps alxwww")
        self.collectExtOutput("/usr/bin/pstree", root_symlink = "pstree")
        self.collectExtOutput("/usr/sbin/lsof -b +M -n -l", root_symlink = "lsof")

    def find_mountpoint(s):
        if (os.path.ismount(s) or len(s)==0): return s
        else: return mountpoint(os.path.split(s)[0])
