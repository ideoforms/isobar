# Contributing

## Code style

To run a style check with flake8:

```
flake8 isobar
```

## Testing

To run unit tests:

```
python3 setup.py test
```

To generate a unit test coverage report:

```
pip3 install pytest-cov
pytest --cov=isobar tests
```

To automatically run unit tests on commit:
```
echo pytest > .git/hooks/pre-commit
```

## Documentation

To generate and serve the docs:

```
pip3 install mkdocs mkdocs-material
mkdocs serve
```

To deploy docs to GitHub:
```
mkdocs gh-deploy
```

To regenerate the per-class pattern docs for the pattern library docs and README:

```
aux/scripts/generate-docs.py -m > docs/patterns/library.md
aux/scripts/generate-docs.py
```

## Distribution

To push to PyPi:

* increment version in `setup.py`
* `git tag vx.y.z`, `git push --tags`, and create GitHub release
* `python3 setup.py sdist`
* `twine upload dist/isobar-x.y.z.tar.gz`
