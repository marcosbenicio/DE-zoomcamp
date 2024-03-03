{{ config(materialized='table') }}
SELECT 
    location_id, 
    borough, 
    zone, 
    REPLACE(service_zone,'Boro','Green') AS service_zone 
FROM {{ ref('taxi_zone_lookup') }}