flake8 evol
flake8 tests
py.test-3
if [ -x "$(command -v py.test-3)" ]; then
  py.test-3
else
  python -m pytest
fi