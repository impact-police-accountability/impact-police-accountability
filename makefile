
up: deploy ingest

ingest: deploy
	python import_from_csvs.py

deploy: images
	daemon --chdir=$(CURDIR) --output=/tmp/impact_police.log -- docker-compose up

lint:
	python -m pip install --upgrade isort black > /dev/null
	python -m black $(shell find . -name "*.py")
	python -m isort $(shell find . -name "*.py")

down:
	docker-compose down

images:
	docker-compose build


