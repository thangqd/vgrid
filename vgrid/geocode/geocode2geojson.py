from vgrid.geocode import mgrs, maidenhead, geohash, georef, olc, s2sphere
from vgrid.geocode.s2sphere import LatLng, CellId
from geopy.distance import geodesic
import geojson, os
import geopandas as gpd
from shapely.geometry import Polygon, Point
import h3

def olc2geojson(olc_code):
    # Decode the Open Location Code into a CodeArea object
    coord = olc.decode(olc_code)
    
    if coord:
        # Create the bounding box coordinates for the polygon
        min_lat, min_lon = coord.latitudeLo, coord.longitudeLo
        max_lat, max_lon = coord.latitudeHi, coord.longitudeHi

        center_lat, center_lon = coord.latitudeCenter, coord.longitudeCenter
        precision = coord.codeLength 
       
        lat_len = geodesic((min_lat, min_lon), (max_lat, min_lon)).meters 
        lon_len = geodesic((min_lat, min_lon), (min_lat, max_lon)).meters  

        bbox_width =  f'{round(lon_len,1)} m'
        bbox_height =  f'{round(lat_len,1)} m'
        if lon_len >= 10000:
            bbox_width = f'{round(lon_len/1000,1)} km'
            bbox_height = f'{round(lat_len/1000,1)} km'

        # Define the polygon based on the bounding box
        polygon_coords = [
            [min_lon, min_lat],  # Bottom-left corner
            [max_lon, min_lat],  # Bottom-right corner
            [max_lon, max_lat],  # Top-right corner
            [min_lon, max_lat],  # Top-left corner
            [min_lon, min_lat]   # Closing the polygon (same as the first point)
        ]
        
        geojson_feature = geojson.Feature(
            geometry=geojson.Polygon([polygon_coords]),
            properties={
                "olc": olc_code,  # Include the OLC as a property
                "center_lat": center_lat,
                "center_lon": center_lon,
                "bbox_height": bbox_height,
                "bbox_width": bbox_width,
                "precision": precision  # Using the code length as precision
                }
            )

        feature_collection = geojson.FeatureCollection([geojson_feature])
        return feature_collection


def maidenhead2geojson(maidenhead_code):
    # Decode the Open Location Code into a CodeArea object
    center_lat, center_lon, min_lat, min_lon, max_lat, max_lon, _ = maidenhead.maidenGrid(maidenhead_code)
    precision = int(len(maidenhead_code)/2)
    
    lat_len = geodesic((min_lat, min_lon), (max_lat, min_lon)).meters 
    lon_len = geodesic((min_lat, min_lon), (min_lat, max_lon)).meters  
    
    bbox_width =  f'{round(lon_len,1)} m'
    bbox_height =  f'{round(lat_len,1)} m'
    
    if lon_len >= 10000:
        bbox_width = f'{round(lon_len/1000,1)} km'
        bbox_height = f'{round(lat_len/1000,1)} km'
        
    if center_lat:
        # Define the polygon based on the bounding box
        polygon_coords = [
            [min_lon, min_lat],  # Bottom-left corner
            [max_lon, min_lat],  # Bottom-right corner
            [max_lon, max_lat],  # Top-right corner
            [min_lon, max_lat],  # Top-left corner
            [min_lon, min_lat]   # Closing the polygon (same as the first point)
        ]

        # Create the GeoJSON structure
        geojson_feature = geojson.Feature(
            geometry=geojson.Polygon([polygon_coords]),
            properties={
                "maidenhead": maidenhead_code,  # Include the OLC as a property
                "center_lat": center_lat,
                "center_lon": center_lon,
                "bbox_height": bbox_height,
                "bbox_width": bbox_width,
                "precision": precision  # Using the code length as precision
                }
            )

        feature_collection = geojson.FeatureCollection([geojson_feature])
        return feature_collection

def gars2geojson(gars_code):
    wkt_polygon = gars_code.polygon
    if wkt_polygon:
        # # Create the bounding box coordinates for the polygon
        x, y = wkt_polygon.exterior.xy
        precision_minute = gars_code.resolution
        
        min_lon = min(x)
        max_lon = max(x)
        min_lat = min(y)
        max_lat = max(y)

        # Calculate center latitude and longitude
        center_lon = (min_lon + max_lon) / 2
        center_lat = (min_lat + max_lat) / 2

        # Calculate bounding box width and height
        lat_len = geodesic((min_lat, min_lon), (max_lat, min_lon)).meters 
        lon_len = geodesic((min_lat, min_lon), (min_lat, max_lon)).meters  

        bbox_width =  f'{round(lon_len,1)} m'
        bbox_height =  f'{round(lat_len,1)} m'

        if lon_len >= 10000:
            bbox_width = f'{round(lon_len/1000,1)} km'
            bbox_height = f'{round(lat_len/1000,1)} km'

        geojson_feature = geojson.Feature(
            geometry=geojson.Polygon([list(wkt_polygon.exterior.coords)]),
             properties={
                "gars": gars_code.gars_id,  # Include the OLC as a property
                "center_lat": center_lat,
                "center_lon": center_lon,
                "bbox_height": bbox_height,
                "bbox_width": bbox_width,
                "precision_minute": precision_minute  # Using the code length as precision
                }
        )

        # Create GeoJSON FeatureCollection
        feature_collection = geojson.FeatureCollection([geojson_feature])

        return feature_collection

def geohash2geojson(geohash_code):
    # Decode the Open Location Code into a CodeArea object
    bbox =  geohash.bbox(geohash_code)
    if bbox:
        min_lat, min_lon = bbox['s'], bbox['w']  # Southwest corner
        max_lat, max_lon = bbox['n'], bbox['e']  # Northeast corner
        
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2
        
        precision =  len(geohash_code)

        lat_len = geodesic((min_lat, min_lon), (max_lat, min_lon)).meters 
        lon_len = geodesic((min_lat, min_lon), (min_lat, max_lon)).meters  
        
        bbox_width =  f'{round(lon_len,1)} m'
        bbox_height =  f'{round(lat_len,1)} m'
        if lon_len >= 10000:
            bbox_width = f'{round(lon_len/1000,1)} km'
            bbox_height = f'{round(lat_len/1000,1)} km'
            
        # Define the polygon based on the bounding box
        polygon_coords = [
            [min_lon, min_lat],  # Bottom-left corner
            [max_lon, min_lat],  # Bottom-right corner
            [max_lon, max_lat],  # Top-right corner
            [min_lon, max_lat],  # Top-left corner
            [min_lon, min_lat]   # Closing the polygon (same as the first point)
        ]

        # Create the GeoJSON structure
        geojson_feature = geojson.Feature(
            geometry=geojson.Polygon([polygon_coords]),
            properties={
                "geohsah": geohash_code,  
                "center_lat": center_lat,
                "center_lon": center_lon,
                "bbox_height": bbox_height,
                "bbox_width": bbox_width,
                "precision": precision  # Using the code length as precision
                }
            )

        feature_collection = geojson.FeatureCollection([geojson_feature])
        return feature_collection

def mgrs2geojson(mgrs_code,lat,lon):
    origin_lat, origin_lon, min_lat, min_lon, max_lat, max_lon,precision = mgrs.mgrscell(mgrs_code)

    lat_len = geodesic((min_lat, min_lon), (max_lat, min_lon)).meters 
    lon_len = geodesic((min_lat, min_lon), (min_lat, max_lon)).meters  
    
    bbox_width =  f'{round(lon_len,1)} m'
    bbox_height =  f'{round(lat_len,1)} m'
    
    if lon_len >= 10000:
        bbox_width = f'{round(lon_len/1000,1)} km'
        bbox_height = f'{round(lat_len/1000,1)} km'
        
    if origin_lat:
        # Define the polygon based on the bounding box
        polygon_coords = [
            [min_lon, min_lat],  # Bottom-left corner
            [max_lon, min_lat],  # Bottom-right corner
            [max_lon, max_lat],  # Top-right corner
            [min_lon, max_lat],  # Top-left corner
            [min_lon, min_lat]   # Closing the polygon (same as the first point)
        ]

        mgrs_polygon = Polygon(polygon_coords)

        # Create the original GeoJSON feature
        geojson_feature = geojson.Feature(
            geometry=geojson.Polygon([polygon_coords]),
            properties={
                "mgrs": mgrs_code,
                "origin_lat": origin_lat,
                "origin_lon": origin_lon,
                "bbox_height": bbox_height,
                "bbox_width": bbox_width,
                "precision": precision
            }
        )

        # Load the GZD GeoJSON file from the same folder
        gzd_geojson_path = os.path.join(os.path.dirname(__file__), 'gzd.geojson')
        with open(gzd_geojson_path) as f:
            gzd_geojson = geojson.load(f)

        # Convert the GZD GeoJSON to a GeoDataFrame
        gzd_gdf = gpd.GeoDataFrame.from_features(gzd_geojson['features'], crs="EPSG:4326")

        # Convert the MGRS polygon to a GeoSeries for intersection
        mgrs_gdf = gpd.GeoDataFrame(geometry=[mgrs_polygon], crs="EPSG:4326")

        # Perform the intersection
        intersection_gdf = gpd.overlay(mgrs_gdf, gzd_gdf, how='intersection')

        # Check if the intersection result is empty
        if not intersection_gdf.empty:
            # Convert lat/lon to a Shapely point
            point = Point(lon, lat)

            # Check if the point is inside any of the intersection polygons
            for intersection_polygon in intersection_gdf.geometry:
                if intersection_polygon.contains(point):
                    # Return the intersection as GeoJSON if the point is inside
                    intersection_geojson = geojson.Feature(
                        geometry=geojson.Polygon([list(intersection_polygon.exterior.coords)]),
                        properties={
                            "mgrs": mgrs_code,
                            "origin_lat": origin_lat,
                            "origin_lon": origin_lon,
                            "bbox_height": bbox_height,
                            "bbox_width": bbox_width,
                            "precision": precision
                        }
                    )
                    intersection_feature_collection = geojson.FeatureCollection([intersection_geojson])
                    return intersection_feature_collection

        # If no intersection or point not contained, return the original MGRS GeoJSON
        # Create a FeatureCollection
        feature_collection = geojson.FeatureCollection([geojson_feature])
        return feature_collection


def georef2geojson(georef_code):
    center_lat, center_lon, min_lat, min_lon, max_lat, max_lon,precision = georef.georefcell(georef_code)

    lat_len = geodesic((min_lat, min_lon), (max_lat, min_lon)).meters 
    lon_len = geodesic((min_lat, min_lon), (min_lat, max_lon)).meters
    
    bbox_width =  f'{round(lon_len,1)} m'
    bbox_height =  f'{round(lat_len,1)} m'
    
    if lon_len >= 10000:
        bbox_width = f'{round(lon_len/1000,1)} km'
        bbox_height = f'{round(lat_len/1000,1)} km'
        
    if center_lat:
        # Define the polygon based on the bounding box
        polygon_coords = [
            [min_lon, min_lat],  # Bottom-left corner
            [max_lon, min_lat],  # Bottom-right corner
            [max_lon, max_lat],  # Top-right corner
            [min_lon, max_lat],  # Top-left corner
            [min_lon, min_lat]   # Closing the polygon (same as the first point)
        ]

        # Create the GeoJSON structure
        geojson_feature = geojson.Feature(
            geometry=geojson.Polygon([polygon_coords]),
            properties={
                "georef": georef_code,  # Include the OLC as a property
                "center_lat": center_lat,
                "center_lon": center_lon,
                "bbox_height": bbox_height,
                "bbox_width": bbox_width,
                "precision": precision  # Using the code length as precision
                }
            )

        # Create a FeatureCollection
        feature_collection = geojson.FeatureCollection([geojson_feature])
        return feature_collection


def h32geojson(h3_code):
    # Get the boundary coordinates of the H3 cell
    boundary = h3.cell_to_boundary(h3_code)
    if boundary:
        # Get the center coordinates of the H3 cell
        center_lat, center_lon = h3.cell_to_latlng(h3_code)
        precision = h3.get_resolution(h3_code)
        edge_len = h3.average_hexagon_edge_length(precision,unit='m')
        # Create the GeoJSON Feature
        geojson_feature = geojson.Feature(
            geometry=geojson.Polygon([[
                [lon, lat] for lat, lon in boundary
            ]]),
            properties={
                "h3": h3_code,
                "center_lat": center_lat,
                "center_lon": center_lon,
                "edge_len": edge_len,
                "precision": precision
            }
        )
        
        # Create a FeatureCollection
        feature_collection = geojson.FeatureCollection([geojson_feature])

        return feature_collection


def s22geojson(cell_id_token):
     # Create an S2 cell from the given cell ID
    cell_id= CellId.from_token(cell_id_token)
    cell = s2sphere.Cell(cell_id)
    if cell:
        # Get the vertices of the cell (4 vertices for a rectangular cell)
        vertices = [cell.get_vertex(i) for i in range(4)]
        
        # Create GeoJSON structure
        geojson_vertices = []

        # Extract latitude and longitude from each vertex
        for vertex in vertices:
            lat_lng = LatLng.from_point(vertex)  # Convert Point to LatLng
            longitude = lat_lng.lng().degrees  # Access the degree value for longitude
            latitude = lat_lng.lat().degrees    # Access the degree value for latitude
            # print(f"Extracted Point: Longitude = {longitude}, Latitude = {latitude}")  # Debug statement
            geojson_vertices.append((longitude, latitude))

        # Close the polygon by adding the first vertex again
        geojson_vertices.append(geojson_vertices[0])  # Closing the polygon

        # Create a GeoJSON Polygon
        geojson_polygon = geojson.Polygon([geojson_vertices])

        # Get center of the cell
        center = cell.get_center()
        center_lat_lng = LatLng.from_point(center)
        center_lat = center_lat_lng.lat().degrees
        center_lon = center_lat_lng.lng().degrees

        # Get rectangular bounds of the cell
        rect_bound = cell.get_rect_bound()
        min_lat = rect_bound.lat_lo().degrees
        max_lat = rect_bound.lat_hi().degrees
        min_lon = rect_bound.lng_lo().degrees
        max_lon = rect_bound.lng_hi().degrees
        
        lat_len = geodesic((min_lat, min_lon), (max_lat, min_lon)).meters 
        lon_len = geodesic((min_lat, min_lon), (min_lat, max_lon)).meters
        
        bbox_width =  f'{round(lon_len,1)} m'
        bbox_height =  f'{round(lat_len,1)} m'
        
        if lon_len >= 10000:
            bbox_width = f'{round(lon_len/1000,1)} km'
            bbox_height = f'{round(lat_len/1000,1)} km'
        # Create properties dictionary for the FeatureCollection
        
        geojson_feature = geojson.Feature(geometry=geojson_polygon, properties = {
            "s2": cell_id.id(),
            "center_lat": center_lat,
            "center_lon": center_lon,
            "bbox_width":bbox_width,
            "bbox_height":bbox_height,
            "level": cell_id.level() 
        })

        # Create a FeatureCollection
        feature_collection = geojson.FeatureCollection([geojson_feature])

        return feature_collection