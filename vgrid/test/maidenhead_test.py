from vgrid.utils import maidenhead
from vgrid.conversion.cell2geojson import *
import json
latitude, longitude = 10.775275567242561, 106.70679737574993

maidenhead_resolution = 4 #[1-->4]
maidenhead_code = maidenhead.toMaiden(latitude, longitude, maidenhead_resolution)
maidenGrid = maidenhead.maidenGrid(maidenhead_code)
print(f'Maidenhead Code at resolution = {maidenhead_resolution}: {maidenhead_code}')
print(f'Convert {maidenhead_code} to center and cell in WGS84 = {maidenGrid}')

data = maidenhead2geojson(maidenhead_code)
print(data)
output_file = f'maidenhead{maidenhead_resolution}.geojson'

with open(output_file, 'w') as f:
    json.dump(data, f, indent=2)  # 'indent' makes the JSON output more readable
print(f'GeoJSON written to {output_file}')