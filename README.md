# service-search-wsgi

| Branch  | Status                                                                                                                                                                                                                                                                                                                      |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| develop | ![Build Status](https://codebuild.eu-central-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiTVQvYjI4bzM2elpSUGFEU2U0bnNtS29qbWJmS0dDVzIwVVpKZkdPVWloN2FLOE1LSnR3dnBVWVEyYnBkUFZ0T1IwTklUdkJTZEZYL015YVNrS21iQ0pVPSIsIml2UGFyYW1ldGVyU3BlYyI6ImJ5ajQwenNPdHVGbmVtQkYiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=develop) |
| master  | ![Build Status](https://codebuild.eu-central-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiTVQvYjI4bzM2elpSUGFEU2U0bnNtS29qbWJmS0dDVzIwVVpKZkdPVWloN2FLOE1LSnR3dnBVWVEyYnBkUFZ0T1IwTklUdkJTZEZYL015YVNrS21iQ0pVPSIsIml2UGFyYW1ldGVyU3BlYyI6ImJ5ajQwenNPdHVGbmVtQkYiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master)  |

## Table of content

- [Table of content](#table-of-content)
- [Description](#description)
- [Versioning](#versioning)
- [Local Development](#local-development)
  - [Make Dependencies](#make-dependencies)
  - [Setting up to work](#setting-up-to-work)
    - [Database access](#database-access)
  - [Linting and formatting your work](#linting-and-formatting-your-work)
  - [Test your work](#test-your-work)
- [Docker](#docker)
- [Deployment](#deployment)
  - [Deployment configuration](#deployment-configuration)

## Description

This is the `SearchServer` service from mf-chsdi3. How the service can be queried, is currently described here:
[api3.geo.admin.ch/search](https://api3.geo.admin.ch/services/sdiservices.html#search). But this will have to be migrated in some way to this repository. This service is a simple Flask Application that query a [Sphinx Search](http://sphinxsearch.com/docs/current.html) Server. Currently supported Sphinx Search server is v2.2.11.

## Versioning

This service uses [SemVer](https://semver.org/) as versioning scheme. The versioning is automatically handled by `.github/workflows/main.yml` file.

See also [Git Flow - Versioning](https://github.com/geoadmin/doc-guidelines/blob/master/GIT_FLOW.md#versioning) for more information on the versioning guidelines.

## Local Development

### Make Dependencies

The **Make** targets assume you have **python3.9**, **pipenv**, **bash**, **curl** and **docker** installed.

### Setting up to work

First, you'll need to clone the repo

```bash
git clone git@github.com:geoadmin/service-search-wsgi
```

Then, you can run the `setup` target to ensure you have everything needed to develop, test and serve locally

Virtual environment to develop and debug the service

```bash
make setup
```

To run the service you will have to adapt **.env.local**, which is a copy of **.env.default** And to set the variables.

For local development you will need access to a running sphinx search server and to the database. To do so you can use 
ssh port forwarding to the DB and to the current sphinx deployment server.

#### Database access

Right now the database BOD is being accessed , to retrieve the <topics> and to do <translations> on labels.

### Linting and formatting your work

In order to have a consistent code style the code should be formatted using `yapf`. Also to avoid syntax errors and non
pythonic idioms code, the project uses the `pylint` linter. Both formatting and linter can be manually run using the
following command:

```bash
make format-lint
```

**Formatting and linting should be at best integrated inside the IDE, for this look at
[Integrate yapf and pylint into IDE](https://github.com/geoadmin/doc-guidelines/blob/master/PYTHON.md#yapf-and-pylint-ide-integration)**

### Test your work

Testing if what you developed work is made simple. You have four targets at your disposal. **test, serve, gunicornserve, dockerrun**

```bash
make test
```

This command run the unit tests.

```bash
summon make serve
```

This will serve the application through Flask without any wsgi in front.

```bash
summon make gunicornserve
```

This will serve the application with the Gunicorn layer in front of the application

```bash
summon make dockerrun
```

This will serve the application with the wsgi server, inside a container.

## Docker

The service is encapsulated in a Docker image. Images are pushed on the `swisstopo-bgdi-builder` account of [AWS ECR](https://eu-central-1.console.aws.amazon.com/ecr/repositories?region=eu-central-1) registry. From each github PR that is merged into develop branch, one Docker image is built and pushed with the following tags:

- `develop.latest`
- `CURRENT_VERSION-beta.INCREMENTAL_NUMBER`

From each github PR that is merged into master, one Docker image is built an pushed with the following tag:

- `VERSION`

Each image contains the following metadata:

- author
- git.branch
- git.hash
- git.dirty
- version

These metadata can be seen directly on the dockerhub registry in the image layers or can be read with the following command

```bash
# NOTE: jq is only used for pretty printing the json output,
# you can install it with `apt install jq` or simply enter the command without it
docker image inspect --format='{{json .Config.Labels}}' 974517877189.dkr.ecr.eu-central-1.amazonaws.com/service-search-wsgi:develop.latest | jq
```

You can also check these metadata on a running container as follows

```bash
docker ps --format="table {{.ID}}\t{{.Image}}\t{{.Labels}}"
```

## Deployment

This service is going to be deployed on a vhost. The configuration of the ***docker-compose.yml*** of the vhost setup is going to be here:
[https://github.com/geoadmin/infra-vhost](https://github.com/geoadmin/infra-vhost)

### Deployment configuration

The service is configured by Environment Variable:

| Env                         | Default                             | Description                                                                                                                                                                                                           |
| --------------------------- | ------------------------------------| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| HTTP_PORT                   | 5000                                | The port on which the service can be queried.                                                                                                                                                                         |
| SEARCH_WORKERS              | `0`                                 | Number of workers. `0` or negative value means that the number of worker are computed from the number of cpu                                                                                                          |
| TESTING                     | False                               | When TESTING=True, the application does not need a db connection to retrieve a list of topics. A list with the topics used in the tests is being set.                                                                 |
| BOD_DB_NAME                 | -                                   | Depending on the staging level usually                                                                                                                                                                                |
| BOD_DB_HOST                 | -                                   | The db host.                                                                                                                                                                                                          |
| BOD_DB_PORT                 | 5432                                | The db port                                                                                                                                                                                                           |
| BOD_DB_USER                 | -                                   | The read-only db user                                                                                                                                                                                                 |
| BOD_DB_PASSWD               | -                                   | The db password.                                                                                                                                                                                                      |
| GEODATA_STAGING             | prod                                | In the database bod, a dataset itself has the attribute staging. This staging (dev, int and prod) is being filtered when querying the indexes.                                                                        |
| SEARCH_SPHINX_HOST          | localhost                           | The host for sphinx search server.                                                                                                                                                                                    |
| SEARCH_SPHINX_PORT          | 9321                                | The port for sphinx search server.                                                                                                                                                                                    |
| SEARCH_SPHINX_TIMEOUT       | 3                                   | Sphinx server timeout                                                                                                                                                                                                 |
| CACHE_DEFAULT_TIMEOUT       | 86400                               | The time in seconds in which the db queries for `topics` and `translations` will be cached. Default 24 hours, as changing rarely.                                                                                     |
| LOGGING_CFG                 | logging-cfg-local.yml               | Logging configuration file                                                                                                                                                                                            |
| FORWARED_ALLOW_IPS          | `*`                                 | Sets the gunicorn `forwarded_allow_ips` (see https://docs.gunicorn.org/en/stable/settings.html#forwarded-allow-ips). This is required in order to `secure_scheme_headers` to works.                                   |
| FORWARDED_PROTO_HEADER_NAME | `X-Forwarded-Proto`                 | Sets gunicorn `secure_scheme_headers` parameter to `{FORWARDED_PROTO_HEADER_NAME: 'https'}`, see https://docs.gunicorn.org/en/stable/settings.html#secure-scheme-headers.                                             |
| SCRIPT_NAME                 | ''                                  | The script name. This will be used once, when we have an idea about how to query search-wsgi later on. F.ex. `/api/search/` f.ex. used by gunicorn (wsgi-server).                                                     |
| CACHE_CONTROL_HEADER        | `'public, max-age=600'`             | Cache-Control header value for the search endpoint                                                                                                                                                                    |
| GZIP_COMPRESSION_LEVEL      | `9`                                 | GZIP compression level                                                                                                                                                                                                |
| WSGI_TIMEOUT                | 1                                   | WSGI timeout, note the final timout used is `SEARCH_SPHINX_TIMEOUT + WSGI_TIMEOUT`, so `WSGI_TIMEOUT` should the maximum amount of time that the WSGI app should have to handle the data received from sphinx server. |
| GUNICORN_WORKER_TMP_DIR     | `None`                              | This should be set to an tmpfs file system for better performance. See https://docs.gunicorn.org/en/stable/settings.html#worker-tmp-dir.                                                                              |
| SERVICE_SPHINX_NAME         | `service-search-sphinx`             | Sets the service name of service-search-sphinx in the `/info` endpoint                                                                                                                                                |
| SERVICE_SPHINX_FILE         | `/usr/local/share/app/version.txt`  | Sets the path of the file with the version metadata from service-search-sphinx, this file has to be mounted from the service-search-sphinx container and will expose the version in `/info` endpoint                  |
