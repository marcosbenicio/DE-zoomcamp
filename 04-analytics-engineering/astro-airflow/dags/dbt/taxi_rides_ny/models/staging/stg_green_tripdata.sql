{{  config( materialized='view')  }}

WITH tripdata AS 
(
    SELECT *,
    row_number() OVER(PARTITION BY vendor_id, lpep_pickup_datetime) AS rn
    FROM {{ source('staging','green_taxi_external_2019') }}
    WHERE vendor_id IS NOT NULL 
)
SELECT
    -- identifiers
    {{ dbt_utils.generate_surrogate_key(['vendor_id', 'lpep_pickup_datetime']) }} AS trip_id,
    {{ dbt.safe_cast("vendor_id", api.Column.translate_type("integer")) }} AS vendor_id,
    {{ dbt.safe_cast("ratecode_id", api.Column.translate_type("integer")) }} AS ratecode_id,
    {{ dbt.safe_cast("pu_location_id", api.Column.translate_type("integer")) }} AS pickup_locationid,
    {{ dbt.safe_cast("do_location_id", api.Column.translate_type("integer")) }} AS dropoff_locationid,
    
    -- timestamps
    CAST(lpep_pickup_datetime AS timestamp) AS pickup_datetime,
    CAST(lpep_dropoff_datetime AS timestamp) AS dropoff_datetime,
    
    -- trip info
    store_and_fwd_flag,
    {{ dbt.safe_cast("passenger_count", api.Column.translate_type("integer")) }} AS passenger_count,
    CAST(trip_distance AS numeric) AS trip_distance,
    {{ dbt.safe_cast("trip_type", api.Column.translate_type("integer")) }} AS trip_type,

    -- payment info
    CAST(fare_amount AS numeric) AS fare_amount,
    CAST(extra AS numeric) AS extra,
    CAST(mta_tax AS numeric) AS mta_tax,
    CAST(tip_amount AS numeric) AS tip_amount,
    CAST(tolls_amount AS numeric) AS tolls_amount,
    CAST(ehail_fee AS numeric) AS ehail_fee,
    CAST(improvement_surcharge AS numeric) AS improvement_surcharge,
    CAST(total_amount AS numeric) AS total_amount,
    COALESCE({{ dbt.safe_cast("payment_type", api.Column.translate_type("integer")) }},0) AS payment_type,
    {{ get_payment_type_description("payment_type") }} AS payment_type_description
FROM tripdata
WHERE rn = 1


-- dbt build --select <model_name> --vars '{'is_test_run': 'false'}'
{% if var('is_test_run', default=true) %}

    LIMIT 100

{% endif %}