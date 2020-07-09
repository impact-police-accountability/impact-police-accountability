LOG_PATH := /tmp/impact_police.log

up: ingest services_working

clean: down
	/bin/rm -vf $(LOG_PATH)

ingest: deploy
	# import law enforcement agencies
	true || python import_from_csvs.py
	# import lawyers
	true || python import_lawyer_from_datadir.py

deploy: images
	daemon --chdir=$(CURDIR) --output=$(LOG_PATH) -- docker-compose up
	python wait_on_pg.py

lint:
	python -m black $(shell find . -name "*.py")
	python -m isort $(shell find . -name "*.py")

down:
	docker-compose down

images:
	docker-compose build
	grep image docker-compose.yaml | cut -f 2- -d: | grep : | xargs -n1 -t docker pull

services_working: nginx_proxy_working nginx_working webapp_working

nginx_proxy_working: ingest
	@curl --silent --fail http://localhost:12346/foo > /dev/null  || { echo "Nginx proxy to webapp is not working!"; tail -n 50 $(LOG_PATH); exit 1; }

nginx_working: ingest
	@curl --silent --fail http://localhost:12346/statictest > /dev/null || { echo "Nginx static files route is not working!"; tail -n 50 $(LOG_PATH); exit 1; }

webapp_working: ingest
	@curl --silent --fail http://localhost:12347/foo > /dev/null || { echo "The webapp is not working!"; tail -n 50 $(LOG_PATH); exit 1; }
