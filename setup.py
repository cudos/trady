import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.md")).read()
CHANGES = open(os.path.join(here, "CHANGES.txt")).read()

requires = [
    "setuptools",
    "pyramid>=1.3",
    "pyramid_jinja2",
    "waitress",
]

if sys.version_info[:3] < (2,5,0):
    raise RuntimeError("This application requires Python 2.6+")

setup(name="trady",
      version="0.0.1",
      description="An open trading platform",
      long_description=README + "\n\n" + CHANGES,
      classifiers=[
        "Framework :: Pylons",
        "Framework :: BFG",
         "Intended Audience :: Financial and Insurance Industry",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author="Jens Hoffmann",
      author_email="xmcpam@gmail.com",
      #url="http://pylons-devel@googlegroups.com",
      #license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      keywords="web wsgi bfg pyramid pylons finance trading",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite="trady.tests",
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = trady:main
      [console_scripts]
      initialize_trady_db = trady.scripts.initializedb:main
      """,
)
