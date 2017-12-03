### Local development

Python can help you. Don't reinstall all the time, rather use a virtulenv that has a link to the code.

```
python setup.py develop
```

### Generating New Documentation

Updating documentation is currently a manual step. From the `docs` folder:

```
pdoc --html --overwrite evol
cp -rf evol/* .
rm -rf evol
```

If you want to confirm that it works you can open the `index.html` file.

### Pushing New Version to PyPi

From the root folder, run:

```
python setup.py sdist
python setup.py bdist_wheel --universal
twine upload dist/*
```
