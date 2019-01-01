import evol
from setuptools import setup
from os import path


def load_readme():
    this_directory = path.abspath(path.dirname(__file__))
    with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        return f.read()


setup(
    name='evol',
    version=evol.__version__,
    description='A Grammar for Evolutionary Algorithms and Heuristics',
    long_description=load_readme(),
    long_description_content_type='text/markdown',
    license='MIT License',
    author=['Vincent D. Warmerdam', 'Rogier van der Geer'],
    author_email='vincentwarmerdam@gmail.com',
    url='https://github.com/godatadriven/evol',
    packages=['evol', 'evol.helpers'],
    keywords=['genetic', 'algorithms', 'heuristics'],
    install_requires=['pathos>=0.2.2.1'],
    python_requires='>=3.6',
    tests_require=[
        "pytest==3.3.1"
    ],
    extras_require={
        "dev": ["flake8==3.5.0", "pytest==3.3.1"]
    },
    classifiers=['Intended Audience :: Developers',
                 'Intended Audience :: Science/Research',
                 'Programming Language :: Python :: 3.6',
                 'Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: MIT License',
                 'Topic :: Scientific/Engineering',
                 'Topic :: Scientific/Engineering :: Artificial Intelligence']
)
