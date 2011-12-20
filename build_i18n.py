"""This script will build i18n files"""
import os
import sys
import subprocess
import shlex
from optparse import OptionParser

from sos.utilities import find

class Builder(object):

    def __init__(self, options, args):
        self.options = options
        self.args = args

        self.NLSPACKAGE = "sos"

        self.MSGMERGE = self.which("msgmerge")
        self.XGETTEXT = self.which("xgettext")
        self.MSGFMT = self.which("msgfmt")
        self.MSGCAT = self.which("msgcat")

        self.PO_DIR = os.path.join("i18n", "po")
        try:
            self.MO_DIR = os.path.join('i18n', 'mo')
            if not os.path.isdir(self.MO_DIR):
                os.mkdir(self.MO_DIR)
        except OSError:
            raise Exception("Could not create directory for .mo files at %s" % self.MO_DIR)
        self.POTFILE = os.path.join(self.PO_DIR, self.NLSPACKAGE + ".pot")
        self.PO_FILES = find("*.po", self.PO_DIR)
        self.PY_SRC = find("*.py", "sos")

    def which(self, executable):
        """Attempts to find an executable on the path. If it doesn't find it, then
        it will prompt the user for the path"""

        def is_exe(path):
            return os.path.isfile(path) and os.access(path, os.X_OK)

        if sys.platform == "win32":
            executable += ".exe"

        if self.options.gettext_path and is_exe(os.path.join(self.options.gettext_path, executable)):
            return os.path.join(self.options.gettext_path, executable)

        if is_exe(executable):
            return executable

        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, executable)
            if is_exe(exe_file):
                    return exe_file

        # didn't find it, prompt the user I guess

    def make_potfile(self):
        cmd = shlex.split("%s --default-domain=%s --add-comments --language=python --keyword=_ --keyword=N_ --output=%s %s"
                % (self.XGETTEXT, self.NLSPACKAGE, self.POTFILE, " ".join(self.PY_SRC)))
        subprocess.check_call(cmd)

    def refresh(self, po_file):
        try:
            cmd = shlex.split("%s -v -U --backup=simple %s %s" % (self.MSGMERGE, po_file, self.POTFILE))
            subprocess.check_call(cmd)
            print "Merge of %s succeeded..." % po_file
        except Exception:
            print "Merge of %s failed..." % po_file

    def format(self, po_file):
        try:
            outfile = po_file.replace("/po/", "/mo/").replace(".po", ".mo")
            cmd = shlex.split("%s -o %s %s" % (self.MSGFMT, outfile, po_file))
            subprocess.check_call(cmd)
            print "Format of %s succeeded..." % po_file
        except:
            print "Format of %s failed..." % po_file

    def clean(self):
        for po_backup_file in find("*.po~", self.PO_DIR):
            os.unlink(po_backup_file)

        if 'mo' in self.args:
            import shutil
            shutil.rmtree(self.MO_DIR)

parser = OptionParser()
parser.add_option("-p", "--properties",
        help="generate properties files",
        action="store_true",
        default=False)

parser.add_option("-g", "--gettext-path",
        help="path to gettext executables")

def main():
    opts, args = parser.parse_args()

    builder = Builder(opts, args)

    if 'clean' in args:
        builder.clean()
        return

    builder.make_potfile()
    for po_file in builder.PO_FILES:
        builder.refresh(po_file)
        builder.format(po_file)
    builder.clean()

if __name__ == "__main__":
    main()
