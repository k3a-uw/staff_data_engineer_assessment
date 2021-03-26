db_connect:
	docker exec -it lifestance_psql psql -U postgres

db_bash:
	docker exec -it lifestance_psql /bin/bash

db_test:
	docker exec -u postgres lifestance_psql psql postgres postgres -f /dbtests/test_person_match.sql

py_bash:
	docker exec -it lifestance_py38 /bin/bash

py_test:
	docker exec -it lifestance_py38 pytest build_clinician_mart.py
	docker exec -it lifestance_py38 python tests/test_w_files.py

py_run:
	docker exec -it lifestance_py38 python build_clinician_mart.py -c "/app/data/source/clinician data.csv" \
	                                                               -p "/app/data/source/providers.csv" \
	                                                               -y "/app/configs/clinician_mart.yml"
full_test:
	docker exec -u postgres lifestance_psql psql postgres postgres -f /dbtests/test_person_match.sql
	docker exec -it lifestance_py38 pytest build_clinician_mart.py
	docker exec -it lifestance_py38 python tests/test_w_files.py

start:
	docker-compose up -d

build:
	docker-compose up --build -d

stop:
	docker-compose down


