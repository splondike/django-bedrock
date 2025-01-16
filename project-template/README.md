# My project

A template project with a bunch of stuff I like in a Django project.

## Development

Development is via Docker and docker-compose.

### Run

1. `docker-compose up`
2. Populate your database using the instructions in the "Rebuild database" section.
3. You can access your system at `https://app.localtest.me/`. Email is viewable at `/maildev`.

### Rebuild database

To reset your database from scratch run this:

    docker-compose run --rm backend bash -c "./manage.py reset_db && ./manage.py migrate && ./manage.py createcachetable && ./manage.py seeddb"

This will give you an admin@example.com user with the password 'password'

### 'Valid' HTTPS certificate

The system comes with a self-signed HTTPS certificate which you can click through in the browser.

If you'd like to have a valid certificate, put the cert and the private key in `config/dev/nginx/nginx-local.crt` and `config/dev/nginx/nginx-local.key` then restart docker-compose.

To generate the .crt and .key files you can use `https://github.com/FiloSottile/mkcert`.

    mkcert -CAROOT # Install the rootCA.pem file from this location to your browser
    mkcert -cert-file nginx-local.crt -key-file nginx-local.key app.localtest.me

### Testing

There are some automated tests. You can run these using:

    docker-compose exec backend pytest

If you get an error like `Missing staticfiles manifest entry` then you need to run `./manage.py collectstatic` before running the tests.

### Testing prod container

An example production container is included at `config/prod/`. If you'd like to test this out locally you can use `docker-compose -f docker-compose.prod-test.yml up`.

The container is HTTP only as this is the most common deployment situation; TLS termination is done elsewhere. You can then access the TLS proxied content at https://app.localtest.me/ using the docker-compose setup. You can see the unproxied response at http://app.localtest.me:8080 . The latter may be useful to verify asset compresison as Nginx by default does not compress when behind another instance (it detects this by a Via header which I don't know how to turn off).
