# Torlist

Servicio que permite consultar ips utilizadas por exit nodes de Tor y manejar una whitelist para excluir del listado ciertas IPs.

# Build

    docker build -t torlist .

# Run

    docker run -p 8000:8000 -e TORLIST_API_KEY=yoursecureapikeygoeshere torlist

# Docs

Pueden revisar los endpoints disponibles en la Swagger UI ubicada en http://127.0.0.1:8000/docs.

# Todo

* Reemplazar uso de `requests` por `aiohttp`.
