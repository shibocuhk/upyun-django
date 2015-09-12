from distutils.core import setup

setup(
    name='upyun-django',
    version='0.0.1',
    packages=['upyun-django'],
    url='http://bruceshi.me',
    license='MIT',
    author='bruceshi',
    author_email='shibocuhk@gmail.com',
    description='django upyun support',
    install_requires=[
        'upyun',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
    ],
)
