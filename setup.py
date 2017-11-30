from setuptools import setup

setup(name='evol',
      version='0.1.1',
      description='A Grammar for Evolutionary Algorithms and Heuristics',
      author=['Vincent D. Warmerdam', 'Rogier van der Geer'],
      author_email='vincentwarmerdam@gmail.com',
      url='https://github.com/koaning/evol',
      packages=['evol', 'evol.helpers'],
      keywords=['genetic', 'algorithms', 'heuristics'],
      install_requires=['pytest'],)