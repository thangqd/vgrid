import locale
import argparse
import csv
import math
from texttable import Texttable

def georef_metrics(res):
    earth_surface_area_km2 = 510_065_621.724 
    base_cells = 288
    num_cells = base_cells
    if res == 0:
        num_cells =  base_cells
    elif res == 1:
        num_cells =  base_cells * (15 * 15)  # Subdivision into 1° x 1° cells
    elif res == 2:
        num_cells = base_cells * (15 * 15) * (60 * 60)  # Subdivision into 1' x 1' cells
    elif res >= 3:
        num_cells =  base_cells * (15 * 15) * (60 * 60) * (100 ** (res - 2))  # Finer subdivisions

    avg_area = (earth_surface_area_km2 / num_cells)*(10**6)
    avg_edge_length = math.sqrt(avg_area)
    return num_cells, avg_edge_length, avg_area


def georef_stats(min_res=0, max_res=5, output_file=None):
    # Create a Texttable object for displaying in the terminal
    t = Texttable()
    
    # Add header to the table, including the new 'Cell Width' and 'Cell Area' columns
    t.add_row(["Resolution", "Number of Cells",  "Avg Edge Length (m)", "Avg Cell Area (sq m)"])
    
    # Check if an output file is specified (for CSV export)
    if output_file:
        # Open the output CSV file for writing
        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Resolution", "Number of Cells", "Avg Edge Length (m)", "Avg Cell Area (sq m)"])
            
            # Iterate through resolutions and write rows to the CSV file
            for res in range(min_res, max_res + 1):
                num_cells, avg_edge_length, avg_area = georef_metrics(res)
                avg_edge_length = round(avg_edge_length,2)
                avg_area = round(avg_area,2)    
                # Write to CSV without formatting locale
                writer.writerow([res, num_cells, avg_edge_length, avg_area])
    else:
        # If no output file is provided, print the result using locale formatting in Texttable
        current_locale = locale.getlocale()  # Get the current locale setting
        locale.setlocale(locale.LC_ALL, current_locale)  # Set locale to current to format numbers
        
        # Iterate through resolutions and add rows to the table
        for res in range(min_res, max_res + 1):
            num_cells, avg_edge_length, avg_area = georef_metrics(res)
           
            formatted_cells = locale.format_string("%d", num_cells, grouping=True)
            
            avg_edge_length = round(avg_edge_length,2)
            formatted_length = locale.format_string("%.2f", avg_edge_length, grouping=True)

            avg_area = round(avg_area,2)    
            formatted_area = locale.format_string("%.2f", avg_area, grouping=True)
            
            # Add a row to the table
            t.add_row([res, formatted_cells, formatted_length, formatted_area])
        
        # Print the formatted table to the console
        print(t.draw())
        

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Export or display GEOREF stats.")
    parser.add_argument('-o', '--output', help="Output CSV file name.")
    parser.add_argument('-minres','--minres', type=int, default=0, help="Minimum resolution.")
    parser.add_argument('-maxres','--maxres', type=int, default=5, help="Maximum resolution.")
    args = parser.parse_args()

    print('Resolution 0: 15 x 15 degrees')
    print('Resolution 1: 1 x 1 degree')
    print('Resolution 2: 1 x 1 minute')
    print('Resolution 3 - 5 = Finer subdivisions (0.1 x 0.1 minute, 0.01 x 0.01 minute, etc.)')

    # Call the function with the provided output file (if any)
    georef_stats(args.minres, args.maxres, args.output)

if __name__ == "__main__":
    main()
