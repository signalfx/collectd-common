from setuptools import setup, find_packages

setup(
    name='collectdutil',
    version='0.0.2',
    description='Utilities for development of collectd plugins',
    packages=find_packages(),
    include_package_data=True,
    author='Ben Keith',
    author_email='bkeith@signalfx.com',
    install_requires=[
        'six',
    ],
    python_requires='>=2.6',
)
