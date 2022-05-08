from setuptools import setup
from setuptools import find_packages

setup(
    name="o2imsdms",
    version="1.0",
    packages=find_packages(),
    license="LICENSE",
    description="Represent O2 IMS and O2 DMS",
    install_requires=[
        'httplib2',
        # 'distributedcloud-client',
        # 'cgtsclient',
        'babel',  # Required by distributedcloud-client
        'PrettyTable<0.8,>=0.7.2',  # Required by distributedcloud-client
    ]
)
