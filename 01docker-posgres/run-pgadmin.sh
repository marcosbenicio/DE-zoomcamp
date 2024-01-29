docker run -it \
    -e PGADMIN_DEFAULT_EMAIL="marcosbenicio@admin.com" \
    -e PGADMIN_DEFAULT_PASSWORD="0102" \
    -p 8080:80 \
    dpage/pgadmin4
