### Generating New Documentation


### Pushing New Version to PyPi

From the root folder, run:

```
python setup.py sdist
python setup.py bdist_wheel --universal
twine upload dist/*
```
