from vgrid.utils import geohash
from vgrid.conversion.cell2geojson import *
import json
latitude, longitude = 10.775275567242561, 106.70679737574993

geohash_resolution = 9 # [1-->30]
geohash_code = geohash.encode(latitude, longitude, geohash_resolution)
geohash_decode = geohash.decode(geohash_code, True)
print(f'Geohash Code at resolution = {geohash_resolution}: {geohash_code}')
print(f'Decode {geohash_code} to WGS84 = {geohash_decode}')

data = geohash2geojson(geohash_code)
print(data)

output_file = f'geohash{geohash_resolution}.geojson'
with open(output_file, 'w') as f:
    json.dump(data, f, indent=2)  
print(f'GeoJSON written to {output_file}')