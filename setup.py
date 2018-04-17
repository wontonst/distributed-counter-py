from setuptools import setup, find_packages


setup(
    name='distributed_counter',
    version='0.0.2',
    description='distributed increment/decrement counter leveraging dynamodb',
    author='Roy Zheng',
    packages=find_packages(exclude=['tests','docs']),
    install_requires=['boto3'],
)
