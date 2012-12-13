import os
import tempfile
import zipfile
import tarfile
import shutil

class Archive(object):

    _name = "unset"

    def prepend(self, src):
        if src:
            name = os.path.split(self._name)[-1]
            renamed = os.path.join(name, src.lstrip(os.sep))
            return renamed

    def add_link(self, dest, link_name):
        pass

    def get_dest(self, src, dest=None):
        return self.prepend(dest) if dest else self.prepend(src)

    def compress(self, method):
        """Compress an archive object via method. ZIP archives are ignored. If
        method is automatic then the following technologies are tried in order: xz,
        bz2 and gzip"""

        self.close()


class DirectoryArchive(Archive):

    #XXX: doesn't work with tmp_dir option yet
    def __init__(self, name, tmp_dir=None):
        print "PARAMS: ", name, tmp_dir
        self.directory = tempfile.mkdtemp(dir=tmp_dir)
        self._name = os.path.join(self.directory, name)
        print "ARCHIVE NAME: ", self._name
        os.mkdir(self._name)

    def name(self):
        return self._name

    def prepend(self, src):
        renamed = os.path.join(self._name, src.lstrip(os.sep))
        print "PREPEND: ", renamed
        return renamed

    def add_file(self, src, dest=None):
        dest = self.get_dest(src, dest)
        self._ensure(dest)
        shutil.copy2(src, dest)

    def add_string(self, content, dest):
        dest = self.prepend(dest)
        self._ensure(dest)
        with open(dest, 'w') as f:
            f.write(content)

    def add_link(self, dest, link_name):
        dest = self.prepend(dest)
        link_name = self.prepend(link_name)
        self._ensure(link_name)
        os.symlink(dest, link_name)

    def open_file(self, name):
        return open(self.prepend(name))

    def _ensure(self, path):
        try:
            os.makedirs(os.path.dirname(path))
        except:
            pass

    def close(self):
        print "closing", self._name


class TarFileArchive(Archive):

    def __init__(self, name):
        self._name = name
        self._suffix = "tar"
        self.tarfile = tarfile.open(self.name(),
                    mode="w", format=tarfile.PAX_FORMAT)

    # this can be used to set permissions if using the
    # tarfile.add() interface to add directory trees.
    def copy_permissions_filter(self, tar_info):
        orig_path = tar_info.name[len(os.path.split(self._name)[-1]):]
        fstat = os.stat(orig_path)
        context = self.get_selinux_context(orig_path)
        if(context):
            tar_info.pax_headers['RHT.security.selinux'] = context
        self.set_tar_info_from_stat(tar_info,fstat)
        return tar_info

    def get_selinux_context(self, path):
        try:
            (rc, c) = selinux.getfilecon(path)
            return c
        except:
            return None

    def set_tar_info_from_stat(self, tar_info, fstat):
        tar_info.mtime = fstat.st_mtime
        tar_info.pax_headers['atime'] = "%.9f" % fstat.st_atime
        tar_info.pax_headers['ctime'] = "%.9f" % fstat.st_ctime
        tar_info.mode = fstat.st_mode
        tar_info.uid = fstat.st_uid
        tar_info.gid = fstat.st_gid

    def name(self):
        return "%s.%s" % (self._name, self._suffix)

    def add_parent(self, path):
        if (path == '/'):
            return
        path = os.path.split(path)[0]
        self.add_file(path)

    def add_file(self, src, dest=None):
        if dest:
            dest = self.prepend(dest)
        else:
            dest = self.prepend(src)

        tar_info = tarfile.TarInfo(name=dest)

        if os.path.isdir(src):
            tar_info.type = tarfile.DIRTYPE
            fileobj = None
        else:
            fp = open(src, 'rb')
            content = fp.read()
            fp.close()
            tar_info.size = len(content)
            fileobj = StringIO(content)
        fstat = os.stat(src)
        # FIXME: handle this at a higher level?
        if src.startswith("/sys/") or src.startswith ("/proc/"):
            context = None
        else:
            context = self.get_selinux_context(src)
            if context:
                tar_info.pax_headers['RHT.security.selinux'] = context
        self.set_tar_info_from_stat(tar_info,fstat)
        self.add_parent(src)
        self.tarfile.addfile(tar_info, fileobj)

    def add_string(self, content, dest):
        fstat = None
        if os.path.exists(dest):
            fstat = os.stat(dest)
        dest = self.prepend(dest)
        tar_info = tarfile.TarInfo(name=dest)
        tar_info.size = len(content)
        if fstat:
            context = self.get_selinux_context(dest)
            if context:
                tar_info.pax_headers['RHT.security.selinux'] = context
            self.set_tar_info_from_stat(tar_info, fstat)
        else:
            tar_info.mtime = time.time()
        self.tarfile.addfile(tar_info, StringIO(content))

    def add_link(self, dest, link_name):
        tar_info = tarfile.TarInfo(name=self.prepend(link_name))
        tar_info.type = tarfile.SYMTYPE
        tar_info.linkname = dest
        tar_info.mtime = time.time()
        self.tarfile.addfile(tar_info, None)

    def open_file(self, name):
        try:
            self.tarfile.close()
            self.tarfile = tarfile.open(self.name(), mode="r")
            name = self.prepend(name)
            file_obj = self.tarfile.extractfile(name)
            file_obj = StringIO(file_obj.read())
            return file_obj
        finally:
            self.tarfile.close()
            self.tarfile = tarfile.open(self.name(), mode="a")

    def close(self):
        self.tarfile.close()

    def compress(self, method):
        super(TarFileArchive, self).compress(method)

        methods = ['xz', 'bzip2', 'gzip']

        if method in methods:
            methods = [method]

        last_error = Exception("compression failed for an unknown reason")
        log = logging.getLogger('sos')

        for cmd in methods:
            try:
                command = shlex.split("%s %s" % (cmd,self.name()))
                p = Popen(command, stdout=PIPE, stderr=PIPE, bufsize=-1)
                stdout, stderr = p.communicate()
                if stdout:
                    log.info(stdout)
                if stderr:
                    log.error(stderr)
                self._suffix += "." + cmd.replace('ip', '')
                return self.name()
            except Exception, e:
                last_error = e
        else:
            raise last_error


class ZipFileArchive(Archive):

    def __init__(self, name):
        self._name = name
        try:
            import zlib
            self.compression = zipfile.ZIP_DEFLATED
        except:
            self.compression = zipfile.ZIP_STORED

        self.zipfile = zipfile.ZipFile(self.name(), mode="w", compression=self.compression)

    def name(self):
        return "%s.zip" % self._name

    def compress(self, method):
        super(ZipFileArchive, self).compress(method)
        return self.name()

    def add_file(self, src, dest=None):
        src = str(src)
        if dest:
            dest = str(dest)

        if os.path.isdir(src):
            # We may not need, this, but if we do I only want to do it
            # one time
            regex = re.compile(r"^" + src)
            for path, dirnames, filenames in os.walk(src):
                for filename in filenames:
                    filename = "/".join((path, filename))
                    if dest:
                        self.zipfile.write(filename,
                                self.prepend(re.sub(regex, dest, filename)))
                    else:
                        self.zipfile.write(filename, self.prepend(filename))
        else:
            if dest:
                self.zipfile.write(src, self.prepend(dest))
            else:
                self.zipfile.write(src, self.prepend(src))

    def add_string(self, content, dest):
        info = zipfile.ZipInfo(self.prepend(dest),
                date_time=time.localtime(time.time()))
        info.compress_type = self.compression
        info.external_attr = 0400 << 16L
        self.zipfile.writestr(info, content)

    def open_file(self, name):
        try:
            self.zipfile.close()
            self.zipfile = zipfile.ZipFile(self.name(), mode="r")
            name = self.prepend(name)
            file_obj = self.zipfile.open(name)
            return file_obj
        finally:
            self.zipfile.close()
            self.zipfile = zipfile.ZipFile(self.name(), mode="a")

    def close(self):
        self.zipfile.close()
