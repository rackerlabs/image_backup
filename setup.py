#!/usr/bin/env python

from setuptools import setup
import sys
if sys.version < "2.2.3":
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

version = "1.0"

setup(
    name="image_backup",
    version=version,
    description="Creates backup server images. Ideally run as a cron job.",
    author="Rackspace",
    author_email="ed.leafe@rackspace.com",
    url="https://github.com/rackspace/image_backup",
    keywords="pyrax rackspace cloud servers openstack backup image",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 2",
    ],
    install_requires=[
        "pyrax",
    ],
    packages=[
        "image_backup"
    ],
)
