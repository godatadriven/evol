"""
Evol 
---------------------------------------

This documentation has been automatically generated via `pdoc`.

Evol is a library that helps you make evolutionary algorithms. The
goal is to have a library that is fun and clear to use, but not fast. 

If you're looking at the library for the first time we recommend
that you first take a look at the examples in the /examples folder
on github. It is usually a better starting point to get started. 

Any details can be discovered on the docs. We hope that this 
library makes it fun to write heuristics again.
 
Contributing Guide
---------------------------------------

### Local development

Python can help you. Don't reinstall all the time, rather use a 
virtulenv that has a link to the code.

    python setup.py develop

When you submit a pull request it will be tested in travis. Once 
the build is green the review can start. Please try to keep your 
branch up to date to ensure you're not missing any tests. Larger 
commits need to be discussed in github before we can accept them.  

### Generating New Documentation

Updating documentation is currently a manual step. From the `docs` folder:

    pdoc --html --overwrite evol
    cp -rf evol/* .
    rm -rf evol

If you want to confirm that it works you can open the `index.html` file.

You can generate the docs by running the following code in the
/docs folder. 

    pdoc --html evol
"""

from .individual import Individual
from .evolution import Evolution
from .population import Population, ContestPopulation
