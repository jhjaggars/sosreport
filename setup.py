import os
from distutils.core import setup

import sos

def get_data_files():

    # unix-test :)
    if os.path.isdir("/usr/share/man"):
        return [('/usr/share/man/man1', ['man/en/sosreport.1']),
                ('/usr/share/man/man5', ['man/en/sos.conf.5']),
                ('/usr/share/sos', ['LICENSE', 'README', 'TODO']),
                ('/etc/sos', ['sos.conf']),
                ]
    else:
        return []

if __name__ == "__main__":
    setup(name="sosreport",
        version=sos.__version__,
        description="A set of tools to gather troubleshooting information from a system",
        long_description="""Sos is a set of tools that gathers information about system
hardware and configuration.  The information can then be used for
diagnostic purposes and debugging.  Sos is commonly used to help
support technicians and developers""",
        license="GPLv2+",
        url='http://github.com/sosreport/sosreport',
        packages=['sos', 'sos.policies', 'sos.plugins'],
        data_files=get_data_files(),
        )
