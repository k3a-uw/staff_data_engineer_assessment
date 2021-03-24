FROM postgres:latest

# DEFINITELY WOULD LOAD THESE VIA ENV VARS (CI/CD SECRETS)
# RATHER THAN PUTTING THEM IN THE REPO
ENV POSTGRES_PASSWORD=changeme
ENV POSTGRES_USER=postgres
ENV POSTGRES_DB=postgres

# CREATE DB INITIALIZATION
COPY init.sql /docker-entrypoint-initdb.d/init.sql

## COPY TEST FILES
RUN mkdir /dbtests
COPY tests /dbtests/


