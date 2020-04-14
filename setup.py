from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='distributed_counter',
    version='0.0.2',
    description='distributed increment/decrement counter leveraging dynamodb',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/wontonst/distributed-counter-py',
    author='Roy Zheng',
    packages=find_packages(exclude=['tests','docs']),
    install_requires=['boto3'],
)
