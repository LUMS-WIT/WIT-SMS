import os, re, datetime, csv
import matplotlib.pyplot as plt


class SoilMoistureData:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.data = []
        self.metadata = []
        self.total_files = 0

    def read_data(self):
        files = [f for f in os.listdir(self.folder_path) if f.endswith(".csv") and 'witsms_gpi' in f]
        self.total_files = len(files)
        print(f"Reading {self.total_files} files...")  # Debugging output

        for file in files:
            file_path = os.path.join(self.folder_path, file)
            gpi = re.search('gpi=(\d+)', file).group(1)
            lat = re.search('lat=([-+]?[0-9]*\.?[0-9]+)', file).group(1)
            lon = re.search('lon=([-+]?[0-9]*\.?[0-9]+)', file).group(1)
            timestamps = []
            soil_moistures = []

            with open(file_path, 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip header
                for col in reader:
                    if col[1]:  # Ensuring the soil moisture value is not empty
                        try:
                            timestamp = datetime.datetime.strptime(col[0], "%Y-%m-%d %H:%M:%S")
                            soil_moisture = float(col[1]) / 100 # coverting to 0-1 scale
                            timestamps.append(timestamp)
                            soil_moistures.append(soil_moisture)
                        except ValueError as e:
                            print(f"Error parsing line in {file}: {e}")  # Error output

            # Ensure data is not empty before appending
            if timestamps:
                self.data.append((timestamps, soil_moistures))  # Storing timestamps and soil moisture values
                start_date = min(timestamps).strftime("%Y-%m-%d")
                end_date = max(timestamps).strftime("%Y-%m-%d")
                count_soil_moisture = len(soil_moistures)
                self.metadata.append({
                    'gpi': gpi,
                    'latitude': lat,
                    'longitude': lon,
                    'start_date': start_date,
                    'end_date': end_date,
                    'count': count_soil_moisture, 
                    'overlaps': 0
                })

    def print_metadata(self):
        headers = ['gpi', 'latitude', 'longitude', 'start_date', 'end_date', 'count', 'overlaps']
        print(",".join(headers))
        for entry in self.metadata:
            row = [entry[header] for header in headers]
            print(",".join(map(str, row)))
    
    def get_metadata(self):
        """
        Returns the metadata as a list of dictionaries.
        Each dictionary contains the metadata of one dataset.
        """
        return self.metadata

    def save_metadata_to_csv(self, filename='metadata.csv'):
        headers = ['gpi', 'latitude', 'longitude', 'start_date', 'end_date', 'count', 'overlaps']
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for entry in self.metadata:
                writer.writerow(entry)
    
    def get_lat_lon_by_gpi(self, gpi):
        for item in self.metadata:
            if item['gpi'] == gpi:
                return (item['latitude'], item['longitude'])
        return None  # Return None if no matching GPI is found  

    def get_soil_moisture_by_location(self, lat=None, lon=None, gpi=None):
        if gpi:  # Get data by GPI if provided
            for (timestamps, soil_moistures), meta in zip(self.data, self.metadata):
                if meta['gpi'] == gpi:
                    return timestamps, soil_moistures
        elif lat and lon:  # Get data by latitude and longitude
            for (timestamps, soil_moistures), meta in zip(self.data, self.metadata):
                if meta['latitude'] == str(lat) and meta['longitude'] == str(lon):
                    return timestamps, soil_moistures
        return None, None  # Return None if no data is found

    def plot_data_gpi(self, gpi=None):
        # Plot data only for the specified GPI
        if gpi:
            found = False
            for (timestamps, soil_moistures), meta in zip(self.data, self.metadata):
                if meta['gpi'] == gpi:
                    plt.figure(figsize=(10, 6))
                    plt.plot(timestamps, soil_moistures, label=f"GPI {meta['gpi']} at ({meta['latitude']}, {meta['longitude']})")
                    plt.title(f"Soil Moisture Time Series for GPI {meta['gpi']} - Values: {meta['count']}")
                    plt.xlabel('Date')
                    plt.ylabel('Soil Moisture')
                    plt.legend()
                    plt.show()
                    found = True
                    break  # Stop after plotting the specified GPI
            if not found:
                raise ValueError(f'GPI {gpi} not available in metadata')
        else:
            # If no GPI is specified, plot all data
            for (timestamps, soil_moistures), meta in zip(self.data, self.metadata):
                plt.figure(figsize=(10, 6))
                plt.plot(timestamps, soil_moistures, label=f"GPI {meta['gpi']} at ({meta['latitude']}, {meta['longitude']})")
                plt.title(f"Soil Moisture Time Series for GPI {meta['gpi']} - Values: {meta['count']}")
                plt.xlabel('Date')
                plt.ylabel('Soil Moisture')
                plt.legend()
                plt.show()


# Example usage:

# wit_sms_path = 'D:\SEBAL\datasets\witsms\processed\SWF SMS\daily'
# soil_moisture_data = SoilMoistureData(wit_sms_path)
# soil_moisture_data.read_data()
# soil_moisture_data.print_metadata()  # Print metadata in CSV format

# #soil_moisture_data.save_metadata_to_csv()  # Save metadata to a CSV file


# # Plotting data for a specific GPI
# soil_moisture_data.plot_data_gpi()