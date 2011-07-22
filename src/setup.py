'''
Created on Jul 20, 2011

@author: jklo
'''
from setuptools import setup, find_packages

setup(
      name="LRMonitor",
      version="0.1",
      author="Jim Klo",
      author_email="jim.klo@sri.com",
      description="Learning Registry Cacti Data Input Script",
      packages=find_packages(),
      long_description="Learning Registry Cacti Data Input Script",
      install_requires=["argparse"],
      license="Apache 2.0 License")