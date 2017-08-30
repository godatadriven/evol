from distutils.core import setup

setup(name='evol',
      version='0.1',
      description='A Grammar for Evolutionary Algorithms and other Heuristics',
      author='Vincent D. Warmerdam',
      author_email='vincentwarmerdam@gmail.com',
      url='https://github.com/koaning/evol',
      packages=['evol', 'evol.helpers'],
      install_requires=['pytest'],)