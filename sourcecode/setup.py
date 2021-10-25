from setuptools import setup

setup(
    name='OceanInsightUVVIS',
    version='v2.0.0',
    packages=['uvvis', 'utilities', 'utilities.jsonutils', 'utilities.pintutils', 'utilities.datetimeutils'],
    # package_dir={'': 'sourcecode'},
    url='https://github.com/UoMMIB/OceanInsightUVVIS\sourcecode',
    license='MIT',
    author='Alex Henderson',
    author_email='alex.henderson@manchester.ac.uk',
    description='Text file parser for Ocean Insight UV-VIS files. '
)
