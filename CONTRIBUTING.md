# Contributing

## Testing

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
