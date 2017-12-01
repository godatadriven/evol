### Local development

Python can help you. Don't reinstall all the time, rather use a virtulenv that has a link to the code.

```
python setup.py develop
```

### Generating New Documentation

This is handled by the build process. But if you want to test locally;

```
pdoc --http evol
```

### Pushing New Version to PyPi

From the root folder, run:

```
python setup.py sdist
python setup.py bdist_wheel --universal
twine upload dist/*
```
