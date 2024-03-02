output_staging=$(dbt run-operation generate_schema_yml --args '{"directory": "staging", "prefix": "stg_"}')
echo "$output_staging" >> models/staging/schema.yml

# Run codegen for core models
output_core=$(dbt run-operation generate_schema_yml --args '{"directory": "core"}')
echo "$output_core" >> models/core/schema.yml