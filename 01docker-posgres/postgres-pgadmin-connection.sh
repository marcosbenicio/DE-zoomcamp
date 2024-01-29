docker run -d \
    -e POSTGRES_USER="marcosbenicio" \
    -e POSTGRES_PASSWORD="0102" \
    -e POSTGRES_DB="ny_taxi" \
    -v $(pwd)/taxi-trip-postgres:/var/lib/postgresql/data \
    -p 5432:5432 \
    --network=pg-network \
    --name pg-database \
    postgres:13

docker run -d \
    -e PGADMIN_DEFAULT_EMAIL="marcosbenicio@admin.com" \
    -e PGADMIN_DEFAULT_PASSWORD="0102" \
    -p 8080:80 \
    --network=pg-network \
    --name pgadmin-interface \
    dpage/pgadmin4
