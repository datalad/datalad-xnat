PYTHON ?= python

clean:
	$(PYTHON) setup.py clean
	rm -rf dist build docs/build docs/source/generated *.egg-info
	-find . -name '*.pyc' -delete
	-find . -name '__pycache__' -type d -delete

release-pypi: clean
	# better safe than sorry
	git grep -q '^##.*??? ??' -- CHANGELOG.md && exit 1 || true
	test ! -e dist
	python setup.py sdist
	python setup.py bdist_wheel --universal
	twine upload dist/*
