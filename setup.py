from ez_setup import use_setuptools

use_setuptools()
from setuptools import setup

setup(
    name='upyun-django',
    version='0.0.2',
    packages=['upyun_django'],
    url='http://bruceshi.me',
    license='MIT',
    author='bruceshi',
    author_email='shibocuhk@gmail.com',
    description='django upyun support',
    install_requires=[
        'upyun',
        'ez_setup'
    ],
    tests_require=['Django'],
    test_suite='tests.main',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
    ],
)
