import pandas as panda
import pprint

data = panda.read_csv("./yellow_tripdata_2019-01.csv", header=0, chunksize=50)
zone_lookup = panda.read_csv("./taxi_zone_lookup.csv", header= 0)

for chunk in data:
    break #rail to keep only 50 records for test

chunk['tpep_pickup_datetime'] = panda.to_datetime(chunk['tpep_pickup_datetime'])
chunk['tpep_dropoff_datetime'] = panda.to_datetime(chunk['tpep_dropoff_datetime'])

currency_fields = ['fare_amount', 'extra', 'mta_tax', 'tip_amount', 'tolls_amount', 'improvement_surcharge', 'total_amount']
chunk[currency_fields] = chunk[currency_fields].round(2)

data_chunk = chunk.to_dict('records')

lookup_dict = zone_lookup.to_dict('records')
valid_ids = set(zone_lookup['LocationID'])

failed_checks = []
valid_checks = []

for record in data_chunk:
    if any(panda.isna(record[f]) for f in ['passenger_count', 'RatecodeID', 'store_and_fwd_flag', 'payment_type', 'fare_amount', 'total_amount', 'trip_distance']):
        failed_checks.append((record, 'null field'))
    elif record['fare_amount'] < 0 or record['total_amount'] < 0:
     failed_checks.append((record, 'negative amount'))
    elif record['tpep_pickup_datetime'].year < 2019:
        failed_checks.append((record, 'year of record out of given range'))
    elif record['tpep_dropoff_datetime'] < record['tpep_pickup_datetime']:
        failed_checks.append((record, 'dropoff time earlier than pickup time'))
    elif record['passenger_count'] <= 0 or record['passenger_count'] > 8: #8 is a test case figure
        failed_checks.append((record, 'negative or excessive passenger count'))
    elif record['trip_distance'] <= 0:
        failed_checks.append((record, 'zero or negative trip distance'))
    elif record['DOLocationID'] not in valid_ids or record['PULocationID'] not in valid_ids:
        failed_checks.append((record, 'location does not appear in lookup dict'))
    elif record['store_and_fwd_flag'] not in ("Y", "N"):
        failed_checks.append((record, 'invalid flag'))
    elif record['payment_type'] not in ([0,1,2,3,4,5,6]):
        failed_checks.append((record, 'payment type not recognised'))
    elif record['RatecodeID'] not in ([1,2,3,4,5,6,99]):
        failed_checks.append((record, 'rate code ID type not recognised'))
    elif record['VendorID'] not in ([1,2,6,7]):
        failed_checks.append((record, 'vendorID not recognised'))
    else:
        valid_checks.append(record)
  
panda.DataFrame(valid_checks).to_csv('../test/valid_records.csv', index=False)

failed_rows = [{**record, 'reason': reason} for record, reason in failed_checks]
panda.DataFrame(failed_rows).to_csv('../test/failed_records.csv', index=False)