[![Build status](https://travis-ci.org/City-of-Helsinki/aggregaattori.svg)](https://travis-ci.org/City-of-Helsinki/aggregaattori)
[![codecov](https://codecov.io/gh/City-of-Helsinki/aggregaattori/branch/master/graph/badge.svg)](https://codecov.io/gh/City-of-Helsinki/aggregaattori)
[![Requirements](https://requires.io/github/City-of-Helsinki/aggregaattori/requirements.svg?branch=master)](https://requires.io/github/City-of-Helsinki/aggregaattori/requirements/?branch=master)

# aggregaattori

Aggregates stories based on multiple APIs.

## Prerequisites

* PostgreSQL (>= 9.3)
* Python (>= 3.4)

## Installation

### Database

aggregaattori runs on PostgreSQL. Install the server on Debian-based systems with:

```bash
sudo apt install postgresql
```

Then create a database user and the database itself as the `postgres` system user:

```bash
sudo -u postgres createuser -P -R -S aggregaattori
sudo -u postgres createdb -l fi_FI.UTF8 -E UTF8 -T template0 -O aggregaattori aggregaattori
sudo -u postgres psql aggregaattori -c "CREATE EXTENSION postgis;"
```

### Code

Clone the repo:
```
git clone https://github.com/City-of-Helsinki/aggregaattori.git
cd aggregaattori
```

Initiate a virtualenv and install the Python requirements:
```
pyenv virtualenv aggregaattori-env
pyenv local aggregaattori-env
```
alternatively if you have virtualenvwrapper installed:
```
mkvirtualenv aggregaattori
workon aggregaattori
```
And then finally
```
pip install -r requirements.txt
```

Create a file .env in the repo base directory containing the following:
```
ALLOWED_HOSTS=127.0.0.1,localhost
DEBUG = True
```

Run migrations:
```
python manage.py migrate
```

Create admin user:
```
python manage.py createsuperuser
```

Run dev server:
```
python manage.py runserver
```
and open your browser to http://127.0.0.1:8000/admin/ using the admin user credentials.
