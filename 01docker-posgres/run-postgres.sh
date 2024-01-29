docker run -it \
-e POSTGRES_USER="marcosbenicio" \
-e POSTGRES_PASSWORD="0102" \
-e POSTGRES_DB="ny_taxi" \
-v $(pwd)/taxi-trip-postgres:/var/lib/postgresql/data \
-p 5432:5432 \
postgres:13