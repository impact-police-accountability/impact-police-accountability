LOG_PATH := /tmp/impact_police.log

up: deploy ingest

clean: down
	/bin/rm -vf $(LOG_PATH)

ingest: deploy
	python import_from_csvs.py

deploy: images
	daemon --chdir=$(CURDIR) --output=$(LOG_PATH) -- docker-compose up

lint:
	python -m black $(shell find . -name "*.py")
	python -m isort $(shell find . -name "*.py")

down:
	docker-compose down

images:
	docker-compose build
	grep image docker-compose.yaml | cut -f 2- -d: | grep : | xargs -n1 -t docker pull

nginx_proxy_working:
	@curl --silent --fail http://localhost:12346/foo > /dev/null  || { echo "Nginx proxy to webapp is not working!"; exit 1; }

nginx_working:
	@curl --silent --fail http://localhost:12346/statictest > /dev/null || { echo "Nginx static files route is not working!"; exit 1; }

webapp_working:
	@curl --silent --fail http://localhost:12347/foo > /dev/null || { echo "The webapp is not working!"; exit 1; }
