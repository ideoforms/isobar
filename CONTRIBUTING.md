# Contributing

## Testing

To run flake8 PEP8 style checker:
```
flake8 isobar
```

To run unit tests:
```
python3 setup.py test
```

To generate a coverage report:
```
pip3 install pytest-cov
pytest --cov=isobar tests
```

To regenerate the per-class pattern docs for the README:
```
aux/scripts/generate-docs.py
```
