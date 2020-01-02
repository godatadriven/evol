import codecs
from os import path
from re import search, M
from setuptools import setup, find_packages


def load_readme():
    this_directory = path.abspath(path.dirname(__file__))
    with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        return f.read()


here = path.abspath(path.dirname(__file__))


def read(*parts):
    with codecs.open(path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='evol',
    version=find_version('evol', '__init__.py'),
    description='A Grammar for Evolutionary Algorithms and Heuristics',
    long_description=load_readme(),
    long_description_content_type='text/markdown',
    license='MIT License',
    author=['Vincent D. Warmerdam', 'Rogier van der Geer'],
    author_email='vincentwarmerdam@gmail.com',
    url='https://github.com/godatadriven/evol',
    packages=find_packages(),
    keywords=['genetic', 'algorithms', 'heuristics'],
    python_requires='>=3.6',
    tests_require=[
        "pytest>=3.3.1", "attrs==19.1.0", "flake8>=3.7.9"
    ],
    extras_require={
        "dev": ["pytest>=3.3.1", "attrs==19.1.0", "flake8>=3.7.9"],
        "docs": ["sphinx_rtd_theme", "Sphinx>=2.0.0"],
    },
    setup_requires=[
        "pytest-runner"
    ],
    install_requires=[
        "multiprocess>=0.70.6.1"
    ],
    classifiers=['Intended Audience :: Developers',
                 'Intended Audience :: Science/Research',
                 'Programming Language :: Python :: 3.6',
                 'Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: MIT License',
                 'Topic :: Scientific/Engineering',
                 'Topic :: Scientific/Engineering :: Artificial Intelligence']
)
