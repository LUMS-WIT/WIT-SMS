import pandas as pd
import glob as glob
import numpy as np
import re
import os
import csv 


from config import INDIR, OUTDIR, METADATA_FILE_PATH, METADATA_FILE_SHEETS_YEARS
from config import LOWER_TOLERANCE_MOISTURE, UPPER_TOLERANCE_MOISTURE


def natural_sort(path_list):
  """Sorts a list of file paths with natural sorting for numbers.

  Args:
      path_list: A list of file paths.

  Returns:
      A new list with the file paths sorted naturally.
  """
  def get_alphanum_key(path):
    """
    Extracts keys from filenames for sorting.
    Splits filename into parts and converts numbers to integers.
    """
    components = []
    for c in re.split(r'[^\d]+', path):
      if c.isdigit():
        components.append(int(c))
      else:
        components.append(c.lower())
    return components

  return sorted(path_list, key=get_alphanum_key)

def accumulate(df, value_cols, timestamp_col, average='daily'):
    """
    Computes time-based averages (e.g., daily, 3hourly, hourly and 30minute) for specified value columns 
    in a dataframe, setting the timestamp for each average to a fixed time during the interval.

    Args:
        df: The pandas dataframe with value and timestamp columns.
        value_cols: List of column names containing values to average.
        timestamp_col: Name of the column containing timestamps.
        average: The type of averaging interval ('daily', 'hourly', etc.).

    Returns:
        A new pandas dataframe with averages over specified intervals and fixed timestamps for each interval.
    """
    # Ensure the timestamp column is in datetime format
    df[timestamp_col] = pd.to_datetime(df[timestamp_col])

    if average == 'daily':
        # Set the time part to 12:00 PM for daily averages
        df['TimeStamp'] = df[timestamp_col].dt.floor('D') + pd.Timedelta(hours=12)

        # Group by the new 'FixedTime' column and compute the mean for each group
        avg_df = df.groupby('TimeStamp')[value_cols].mean().reset_index()

    elif average == '3hourly':
        df['TimeStamp'] = df[timestamp_col].dt.floor('3h')
        avg_df = df.groupby('TimeStamp')[value_cols].mean().reset_index()
        # Ensure every 3-hour interval is represented
        if not avg_df.empty:
            all_times = pd.date_range(start=avg_df['TimeStamp'].min(), end=avg_df['TimeStamp'].max(), freq='3h')
            avg_df = avg_df.set_index('TimeStamp').reindex(all_times).reset_index().rename(columns={'index': 'TimeStamp'})
  
    elif average == 'hourly':
        # Set time to every hour
        df['TimeStamp'] = df[timestamp_col].dt.floor('h')
        avg_df = df.groupby('TimeStamp')[value_cols].mean().reset_index()

    elif average == '30minute':
        # Set time to every thirty minutes
        df['TimeStamp'] = df[timestamp_col].dt.floor('30min')
        avg_df = df.groupby('TimeStamp')[value_cols].mean().reset_index()
    
    # Round the averages to 3 decimal places
    for col in value_cols:
        avg_df[col] = avg_df[col].round(3)

    return avg_df

def remove_outliers_and_nan(df,val_col,upper_bound,lower_bound):
    '''
    Removes all rows in the dataframe that have NaN values, or values outside the defined bounds in the val_col
    Args:
      df: The pandas dataframe with value and timestamp columns.
      val_col: Column name containing values to condition removal on.
      upper_bound: maximum value an entry can have outside which it is considered erronous.
      lower_bound: minimum value an entry must have outside which it is considered erronous.

  Returns:
      A new cleaned pandas dataframe with no outliers or NaN values.
    '''
    df_new= df.drop(df[df[val_col].isnull()].index)
    df_new = df_new.drop(df_new[df_new[val_col] > upper_bound].index)
    df_new = df_new.drop(df_new[df_new[val_col] < lower_bound].index)
    return df_new

def remove_redundant_col(df,val_col):
    '''
    Removes the column if all of its values are NaN.
    Args:
      df: The pandas dataframe with value and timestamp columns.
      val_col: Column name containing values to condition removal on.
    
    Returns:
      A new dataframe with or without the val_col (dependent on all NaNs or not).
    '''
    if df[~df[val_col].isnull()].empty:
        return df.drop(val_col,axis = 1)
    return df

def preprocessing(df,average):
    '''
    Args:
      df: The pandas dataframe with value and timestamp columns.
      upper_bound: maximum interval an entry can span
      lower_bound: minimum interval an entry must span
    Returns an averaged out dataframe with no outliers or NaN values.
    '''
    result = remove_redundant_col(df,df.columns[3])
    result = remove_outliers_and_nan(result,result.columns[2],UPPER_TOLERANCE_MOISTURE,LOWER_TOLERANCE_MOISTURE)
    result = accumulate(result, result.columns[2:],result.columns[1], average)
    if len(result.columns) == 3:
        result = remove_redundant_col(result,result.columns[2])
        if len(result.columns) == 3:
            valid_values = result[result.columns[2]].notna()
            some_inside = (result[result.columns[2]][valid_values] < UPPER_TOLERANCE_MOISTURE).any() | (result[result.columns[2]][valid_values] > LOWER_TOLERANCE_MOISTURE).any()
            if not some_inside: 
                result = result.drop(result.columns[2],axis=1)
            else:
                condition = ~result[result.columns[2]].notna() | ~result[result.columns[2]].between(LOWER_TOLERANCE_MOISTURE, UPPER_TOLERANCE_MOISTURE)
                result[result.columns[2]] = np.where(condition, np.nan, result[result.columns[2]])

    return result

def try_convert_and_format(value):
  """
  Attempts to convert a value to integer and formats it as a three-digit string with leading zeros.
  Returns the original value if conversion fails.
  """
  try:
    return f"{int(value):03d}"  # Corrected formatting
  except ValueError:
    return value

def process_three_formats(df,metadata_df,year):
    '''
    Generates and saves three .csv files containing hourly, trihourly and daily averaged data.
    Args:
     df: The pandas dataframe with value and timestamp columns.s
     metadata_df: The slice of pandas dataframe containing supplementary information for file naming.
     year: the particular year pertaining to the data.
    '''
    result_daily = preprocessing(df, average='daily')
    result_hourly = preprocessing(df, average='hourly')
    result_tri_hourly = preprocessing(df, average='3hourly')
    result_thirty_mins = preprocessing(df, average='30minute')
    
    num = try_convert_and_format(metadata_df["Sr No."])
    title = "witsms_gpi="+str(int(year))+num+"_lat="+str(metadata_df["Latitude"])+"_lon="+str(metadata_df["Longitude"])
    path = OUTDIR+"/"

    # Ensure the necessary directories exist
    daily_path = os.path.join(path, "daily")
    hourly_path = os.path.join(path, "hourly")
    tri_hourly_path = os.path.join(path, "tri_hourly")
    thirty_min_path = os.path.join(path, "30_min")
    
    os.makedirs(daily_path, exist_ok=True)
    os.makedirs(hourly_path, exist_ok=True)
    os.makedirs(tri_hourly_path, exist_ok=True)
    os.makedirs(thirty_min_path, exist_ok=True)
    
    # Save the CSV files to the appropriate directories
    result_daily.to_csv(os.path.join(daily_path, title + "_24H.csv"), index=False, header=True)
    result_hourly.to_csv(os.path.join(hourly_path, title + "_1H.csv"), index=False, header=True)
    result_tri_hourly.to_csv(os.path.join(tri_hourly_path, title + "_3H.csv"), index=False, header=True)
    result_thirty_mins.to_csv(os.path.join(thirty_min_path, title + "_30m.csv"), index=False, header=True)
    


def prepare_dataframes(folder_paths):
  """
    Prepares DataFrames from CSV files in specified folder paths.

    Args:
        folder_paths (list): A list of strings representing folder paths containing CSV files.

    Returns:
        list: A list of lists, where each inner list contains DataFrames
              corresponding to CSV files from a single folder path.
  """
  csv_files = [glob.glob(path + "\*.csv") for path in folder_paths]
  
  csv_files = [natural_sort(file_paths) for file_paths in csv_files]
  
  dataframes = [] 
  for i in range(len(csv_files)):
      print("DATAFRAMES PROCESSING...(",i+1,"/",len(csv_files),")")
      dfs=[pd.read_csv(file_path, skiprows=4) for file_path in csv_files[i]]
      dfs = [df[["TimeStamp","VolumetricWaterContent1","VolumetricWaterContent2"]] for df in dfs]
      for df in dfs:
          try:
              df["TimeStamp"] = pd.to_datetime(df["TimeStamp"],format='%m/%d/%Y %I:%M:%S %p')
          except:
              try:
                  df["TimeStamp"] = pd.to_datetime(df["TimeStamp"],format='%m/%d/%Y %H:%M')
              except:
                  for j,row in df.iterrows(): 
                      try:
                          df.loc[j,"TimeStamp"] = pd.to_datetime(df.loc[j,"TimeStamp"],format='%m/%d/%Y %H:%M')
                      except:
                          df.loc[j,"TimeStamp"] = pd.to_datetime(df.loc[j,"TimeStamp"],format='%m/%d/%Y %I:%M:%S %p')
      dfs = [df.sort_values(by='TimeStamp') for df in dfs]
      dfs = [df.reset_index() for df in dfs]
      dataframes.append(dfs)    
  
  return dataframes

def prepare_metadata(metadata_filepath,sheet_names):
    """
    Prepares a list of DataFrames from an Excel file containing metadata.

    Args:
        metadata_filepath (str): The path to the Excel file containing metadata.
        sheet_names (list): A list of strings representing the names of sheets
                            to read from the Excel file.

    Returns:
        list: A list of DataFrames, where each DataFrame corresponds to a sheet
              in the Excel file specified by `sheet_names`.
    """
    metadata = [pd.read_excel(metadata_filepath,sheet_name=str(sheet)) for sheet in sheet_names]
    
    return metadata


def preprocess(metadata_file_path, metadata_file_sheets, data_file_paths):
    """
    Preprocesses and prepares data from multiple CSV and metadata files.

    Args:
        metadata_file_path (str): The path to the Excel file containing metadata.
        metadata_file_sheets (list): A list of strings representing the names of sheets
                                     to read from the Excel file.
        data_file_paths (list): A list of paths to fetch data from.
    Returns:
        Nothing. Processes all the dataframes and saves the averaged processed data in three formats in the relevant folders.
    """
    metadata = prepare_metadata(metadata_file_path,metadata_file_sheets)
    print("METADATA EXTRACTED")
    dataframes = prepare_dataframes(data_file_paths)
    print("DATAFRAMES PROCESSED")
    
    for i,file_list in enumerate(dataframes):
        print("YEARS PROCESSED...(",i+1,"/",len(dataframes),")")
        for j,files in enumerate(file_list):
            process_three_formats(files,metadata[i].iloc[j],metadata_file_sheets[i])

def remove_empty_files(directory):
  """
  Removes empty CSV files (containing only headers) from a directory and its subdirectories.

  Args:
      directory (str): The directory path to search for CSV files.
  """
  for filename in glob.iglob(os.path.join(directory, '**/*.csv'), recursive=True):
    if os.path.getsize(filename) == 0:
      # Empty file, remove it
      os.remove(filename)
      print(f"Removed empty CSV: {filename}")
    else:
      # Check for header only (read first line)
      if has_one_row(filename):
        os.remove(filename)
        print(f"Removed CSV with only header: {filename}")

import csv

def has_one_row(filename):
  """
  Checks if a CSV file contains only one row (including header).

  Args:
      filename (str): The path to the CSV file.

  Returns:
      bool: True if the file has only one row, False otherwise.
  """
  try:
    with open(filename, 'r', encoding='utf-8') as csvfile:
      reader = csv.reader(csvfile)
      # Read the first row
      first_row = next(reader)
      # Check for empty file (no rows)
      if not first_row:
        return False
      # Check for single row (including header)
      try:
        next(reader)
        return False  # More than one row found
      except StopIteration:
        return True  # Only one row (including header)
  except OSError as e:
    print(f"Error opening file {filename}: {e}")
    return False  # Assume not one row on error

if __name__ == "__main__":

    # Define the data file paths using absolute paths
    DATA_FILE_PATHS = []
    for year in METADATA_FILE_SHEETS_YEARS:
       
        DATA_FILE_PATH = os.path.join(INDIR, str(year))
        DATA_FILE_PATHS.append(DATA_FILE_PATH)

    # Call your functions with the absolute paths
    preprocess(METADATA_FILE_PATH, METADATA_FILE_SHEETS_YEARS, DATA_FILE_PATHS)
    remove_empty_files(OUTDIR)