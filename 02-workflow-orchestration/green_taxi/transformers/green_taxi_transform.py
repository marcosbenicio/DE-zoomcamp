import pandas as pd
import regex as re

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(data, *args, **kwargs):
    
    # Check is all columns are snake case
    def is_snake_case(name):
        return re.match(r'^[a-z_][a-z0-9_]*$', name) is not None

    # convert all camel columns names to snake
    def camel_to_snake(name):
        return re.sub(r'(?<=[a-z0-9])([A-Z])|(?<=[A-Z])([A-Z])(?=[a-z])', r'_\g<0>', name).lower()
    
    # Remove rows where the passenger count is 0 or the trip distance is 0.
    condition = (data['passenger_count'] > 0) & (data['trip_distance'] > 0)
    data = data[condition]
    
    # Create a new column 'lpep_pickup_date' by converting 'lpep_pickup_datetime' to a date.
    data['lpep_pickup_date'] = pd.to_datetime(data['lpep_pickup_datetime']).dt.date.copy()
    
    # Rename columns in Camel Case to Snake Case
    data.columns = [camel_to_snake(column) for column in data.columns]
        
    assert all(is_snake_case(column) for column in data.columns), "Not all column names are in snake case."
    assert (data['passenger_count'] > 0).all(), "'passenger_count' contains non-positive values."
    assert (data['trip_distance'] > 0).all(), "'trip_distance' contains non-positive values."
    
    return data 


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
