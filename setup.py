import re
from os import path

from setuptools import setup

wdir = path.abspath(path.dirname(__file__))

with open(path.join(wdir, 'flake8_datetimez.py'), encoding='utf-8') as f:
    try:
        version = re.findall(r"^__version__ = '([^']+)'\r?$",
                             f.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')

with open(path.join(wdir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='flake8-datetimez',
    version=version,
    description='A plugin for flake8 to ban naive datetime classes.',
    long_description=long_description,
    keywords='flake8 datetime pyflakes pylint linter qa',
    author='Jungkook Park',
    author_email='jk@elicer.com',
    url='https://github.com/pjknkda/flake8-datetimez',
    license='MIT',
    py_modules=['flake8_datetimez'],
    python_requires='>=3.6',
    install_requires=['flake8 >= 3.0.0'],
    test_suite='test_datetimez',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Framework :: Flake8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
    ],
    entry_points={'flake8.extension': ['DTZ = flake8_datetimez:DateTimeZChecker']},
)
