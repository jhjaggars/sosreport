from distutils.core import setup
import subprocess

if __name__ == "__main__":
    # Generate gpg key
    subprocess.call("gpg --batch --gen-key gpgkeys/gpg.template")

    setup(name="sosreport",
        version="2.3",
        description="A set of tools to gather troubleshooting information from a system",
        long_description="\n".join((
        "Sos is a set of tools that gathers information about system",
        "hardware and configuration.  The information can then be used for",
        "diagnostic purposes and debugging.  Sos is commonly used to help",
        "support technicians and developers.")),
        license="GPLv2+",
        url='http://github.com/sosreport/sosreport',
        packages=['sos', 'sos.policies', 'sos.plugins'],
        data_files=[('/usr/share/man/man1', ['man/en/sosreport.1']),
                    ('/usr/share/man/man5', ['man/en/sos.conf.5']),
                    ('/usr/share/sos', ['LICENSE', 'README', 'TODO', 'gpgkeys/rhsupport.pub']),
                    ('/etc/sos', ['sos.conf']),
                    ]
        )
