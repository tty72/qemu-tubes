import os
import sys
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

if sys.version_info < (2, 7, 0):
    sys.stderr.write("QTubes requires Python 2.7 or newer.\n")
    sys.exit(-1)

requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    'pyramid_genshi',
    "tw2.core",
    "tw2.forms",
    "tw2.dynforms",
    "tw2.sqla",
    "tw2.jqplugins.jqgrid",
    ]

setup(name='QemuTubes',
      version='0.6',
      description='QemuTubes',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python :: 2.7",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Operating System :: Unix",
        ],
      author='Noah Davis',
      author_email='ndavis@tty72.com',
      url='https://github.com/tty72/qemu-tubes',
      keywords='web wsgi bfg pylons pyramid qemu kvm',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='qemutubes',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = qemutubes:main
      [console_scripts]
      initialize_QemuTubes_db = qemutubes.scripts.initializedb:main
      """,
      )
