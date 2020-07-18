LOG_PATH := /tmp/impact_police.log
IPA_PORT_NGINX := 5011
IPA_PORT_POSTGRES := 5012
IPA_PORT_WEBAPP := 5013

.EXPORT_ALL_VARIABLES:

up: ingest services_working
	@echo "Successfully deployed..."
	@echo "Nginx is listening on $(IPA_PORT_NGINX)"
	@echo "Postgres is listening on $(IPA_PORT_POSTGRES)"
	@echo "Webapp is listening on $(IPA_PORT_WEBAPP)"

clean: down
	/bin/rm -vf $(LOG_PATH)

ingest: deploy
	# import law enforcement agencies
	python import_law_enforcement_from_csvs.py
	# import lawyers
	python import_lawyer_from_datadir.py
	# import geodata?
	python import_geodata.py

deploy: images
	daemon --chdir=$(CURDIR) --output=$(LOG_PATH) -- docker-compose up
	python wait_on_pg.py

lint:
	python -m black $(shell find . -name "*.py")
	python -m isort $(shell find . -name "*.py")

down:
	docker-compose down

cachebust:
	cat webapp/Dockerfile.template | perl -pe "s/CACHEBUST/$(shell date +%s)/" > webapp/Dockerfile

images: cachebust
	docker-compose build
	grep image docker-compose.yaml | cut -f 2- -d: | grep : | xargs -n1 -t docker pull

services_working: nginx_proxy_working nginx_working webapp_working

nginx_proxy_working: ingest
	@curl --silent --fail http://localhost:$(IPA_PORT_NGINX)/foo > /dev/null  || { echo "Nginx proxy to webapp is not working!"; tail -n 50 $(LOG_PATH); exit 1; }

nginx_working: ingest
	@curl --silent --fail http://localhost:$(IPA_PORT_NGINX)/statictest > /dev/null || { echo "Nginx static files route is not working!"; tail -n 50 $(LOG_PATH); exit 1; }

webapp_working: ingest
	python wait_on_webapp.py
