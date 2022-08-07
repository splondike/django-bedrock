A starter template for Django projects, based on the things I like to have in them.

The main project template is in `project-template`. Once you've copied that out you'll need to make some changes for your specific repository.

# Initial setup

The following are some post copy setup steps you might like to make. I considered using the Python cookiecutter project to automate this, but it seemed like a bit more effort than it was worth.

Project:

1. Change the name, author etc. in `pyproject.toml`.
1. Change the blurb in `README.md`.
1. Add in a LICENSE file for your project.

Frontend:

1. Change the opengraph and description stuff in `main/templates/main/layout.html`.
1. Change the favicon in `main/templates/main/layout.html`.

Hosting:

1. Decide whether you need these settings

```
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
```

# Extra functionality

I've only included the things in the template that I would want in pretty much every project. Here are some extra packages you might like to add:

Python:
* https://github.com/uptick/django-dramatiq-pg - Alternative to Celery. This package configures it to store the task queue in Postgres.
* https://huey.readthedocs.io/en/latest/contrib.html#django - Another alternative to celery.
* https://pypi.org/project/django-mailer/ - Simple email queue stored in the database.
* https://github.com/vintasoftware/django-templated-email - Nicer way of making emails in Django
* django-tables2 - Sortable, paginatable tables
* django-filter - Nice URL based filters for tables2
* django-crispy-forms - Nice forms

Frontend:
* css.gg - Nice icons
* htmx - AHAH using HTML attributes.
* alpine.js - Simple interractivity using HTML attributes

# Licenses

This project is licenced under the 0BSD license. My intention is anybody can take anything they like from it without needing to credit this project. For example you can copy paste any of it into your commercial project.

The licenses of the directly included Python dependencies are:

* django - BSD 3-clause
* psycopg2 - LGPL
* django-extensions - MIT
* whitenoise - MIT
* circus - Apache v2
* gunicorn - MIT

* pytest - MIT
* pytest-django - BSD 3-clause
* pytest-cov - MIT
* factory-boy - MIT
* Werkzeug - BSD 3-clause
* flake8 - MIT
* pylint - GPLv2
* pylint-django - GPLv2

And the CSS:

* picocss - MIT

And the JS:

* parcel - MIT
* concurrently - MIT
* copy-and-watch - MIT
* livereload - MIT
