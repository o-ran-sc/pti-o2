from setuptools import setup
from setuptools import find_packages

setup(
    name="mock_smo",
    version="1.0",
    packages=find_packages(),
    license="LICENSE",
    description="Mock SMO server for O2 IMS and DMS",
    install_requires=[
        'httplib2',
    ]
)
