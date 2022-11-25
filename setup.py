from setuptools import setup
from setuptools import find_packages

setup(
    name="o2imsdms",
    version="1.0.0",
    packages=find_packages(),
    license="Apache-2.0",
    author='Bin Yang',
    author_email='bin.yang@windriver.com',
    description="Represent StarlingX as an O-RAN O-Cloud by exposing O-RAN Compliant O2 IMS and O2 DMS Interfaces",
    url='https://docs.o-ran-sc.org/projects/o-ran-sc-pti-o2/en/latest/index.html',
    install_requires=[
        'httplib2',
        'distributedcloud-client',
        'cgtsclient',
        'fmclient',
        'babel',  # Required by distributedcloud-client
        'PrettyTable<0.8,>=0.7.2',  # Required by distributedcloud-client
    ]
)
