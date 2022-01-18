# Libraries

## sphinxapi

The `sphinxapi` library has been copied from [sphinxsearch/sphinx/blob/2.2.11-release/api/sphinxapi.py](https://github.com/sphinxsearch/sphinx/blob/2.2.11-release/api/sphinxapi.py). This library has been then enhanced with the following features:

- Use same code style as the service
- Fixing some linting issues
- Added support for python3
  - This has been inspired by [atuchak/sphinxapi-py3](https://github.com/atuchak/sphinxapi-py3) which is published as pypi package (https://pypi.org/project/sphinxapi-py3/). Unfurtunately this package is not maintened anymore and has some issues therefore we cannot use it.
- Added `ResetFiltersOnly()`
- Various bug fixes
