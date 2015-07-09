#!/usr/bin/env python
import sys, os

try:
    from setuptools import setup
except ImportError:
    print("avakas requires setuptools")
    sys.exit(1)

def main():
    vsn_path = "%s/version" % os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(vsn_path):
        print("%s is missing" % vsn_path)
        sys.exit(1)

    vsn_file = open(vsn_path, 'r')
    version = vsn_file.read()
    vsn_file.close()

    setup(name='avakas',
          version=version,
          description='Interact with project version metadata',
          author='Jonathan Freedman',
          author_email='jonafree@gmail.com',
          url='https://github.com/otakup0pe/avakas',
          install_requires=['semantic_version'],
          scripts=[
              'avakas'
          ])

if __name__ == "__main__":
    main()
