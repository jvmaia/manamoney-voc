#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name='managing_money',
    version='0.0.1',
    description='An app to control your finances',
    author='JvMaiia',
    author_email='joaovmferreira@gmail.com',
    license='BSD license',
    packages=find_packages(
        exclude=['docs', 'tests', 'android']
    ),
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: BSD license',
    ],
    install_requires=[
    ],
    options={
        'app': {
            'formal_name': 'Managing Money',
            'bundle': 'com.jvmaiia'
        },
    }
)
