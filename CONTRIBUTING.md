# Contributing

## Code style

To run a style check with flake8:

```
flake8 isobar-ext
```

## Testing

To run unit tests:

```
python3 setup.py test
```

To generate a unit test coverage report:

```
pip3 install pytest-cov
pytest --cov=isobar-ext tests
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
auxiliary/scripts/generate-docs.py -m > docs/patterns/library.md
auxiliary/scripts/generate-docs.py
```

## Distribution
Before pushing to pypl install Poetry is a tool for dependency management and packaging in Python
* `pip install poetry`
* add test pypi repository `poetry config repositories.test-pypi https://test.pypi.org/legacy/`
* add your test.pypl token `poetry config pypi-token.test-pypi  pypi-YYYYYYYY`
* add your pypl token `poetry config pypi-token.pypi pypi-XXXXXXXX`  
note: twine, setuptools, wheel packages are not needed


To push to PyPi:

* bump version  (e.g. `poetry version patch`)  
    details about rule applied for this command: https://python-poetry.org/docs/cli/#version
* check version `poetry verson` e.g. `x.y.z`
* `git tag vx.y.z`, `git push --tags`, and create GitHub release (you check existing tags with `git tag`)
* `poetry build`
* `poetry publish -r test-pypi` to publish to test-pypl and check if results are satisfactory
* `poetry publish` to publish to pypl when you are satisfied with test-pypl

