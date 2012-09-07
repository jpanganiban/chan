from setuptools import setup, find_packages


__name__ = 'chan'
__version__ = '0.1'
__author__ = 'Jesse Panganiban'

install_requires = [
    'lxml',
    'beautifulsoup4',
]

console_scripts = [
]
entry_points = {
    'console_scripts': console_scripts
}

setup(name=__name__,
      version=__version__,
      author=__author__,
      entry_points=entry_points,
      install_requires=install_requires)
