flake8 evol
flake8 tests
if [ -x "$(command -v py.test-3)" ]; then
  py.test-3
else
  python -m pytest
fi