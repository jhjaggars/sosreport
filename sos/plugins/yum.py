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
import os

class yum(Plugin, RedHatPlugin):
    """yum information
    """

    files = ('/etc/yum.conf',)
    packages = ('yum',)
    optionList = [("yumlist", "list repositories and packages", "slow", False),
                  ("yumdebug", "gather yum debugging data", "slow", False)]

    def setup(self):
        rhelver = self.policy().rhelVersion()

        # Pull all yum related information
        self.addCopySpecs([
            "/etc/yum",
            "/etc/yum.repos.d",
            "/etc/yum.conf",
            "/var/log/yum.log"])

        # Get a list of channels the machine is subscribed to.
        self.collectExtOutput("/usr/bin/yum -C repolist")

        # candlepin info
        self.addForbiddenPath("/etc/pki/entitlements/key.pem")
        self.addForbiddenPath("/etc/pki/entitlements/*-key.pem")
        self.addCopySpecs([
            "/etc/pki/product/*.pem",
            "/etc/pki/consumer/cert.pem",
            "/etc/pki/entitlement/*.pem",
            "/etc/rhsm/",
            "/var/log/rhsm/rhsm.log",
            "/var/log/rhsm/rhsmcertd.log"])
        self.collectExtOutput("subscription-manager list --installed")
        self.collectExtOutput("subscription-manager list --consumed")

        if self.getOption("yumlist"):
            # List various information about available packages
            self.collectExtOutput("/usr/bin/yum list")

        if self.getOption("yumdebug") and self.isInstalled('yum-utils'):
            # RHEL6+ alternative for this whole function:
            # self.collectExtOutput("/usr/bin/yum-debug-dump '%s'" % os.path.join(self.cInfo['dstroot'],"yum-debug-dump"))
            ret, output, rtime = self.callExtProg("/usr/bin/yum-debug-dump")
            try:
                self.collectExtOutput("/bin/zcat %s" % (output.split()[-1],))
            except IndexError:
                pass
