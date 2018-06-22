from setuptools import setup

setup(
    name='collectdtesting',
    version='0.0.3',
    description='Utilities for doing integration testing of collectd plugins',
    packages=['collectdtesting'],
    include_package_data=True,
    author='Ben Keith',
    author_email='bkeith@signalfx.com',
    install_requires=[
        'docker>=3.0.0',
        'signalfx>=1.0',
    ],
    python_requires='>=3.5',
)
