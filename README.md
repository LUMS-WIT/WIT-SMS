# WIT-SMS
The Center for Water Informatics & Technology (WIT) hosts an IoT-based soil moisture network consisting of more than 200
soil moisture nodes installed throughout the Indus Basin. The purpose of this repository is pre-processing and visualization WITSMS-Network soil moisture data which can then be used for downstream tasks.

## Data Access
In order to access the data, please contact WIT's Business Development Manager [email](mailto:a.abbas@lums.edu.pk) or at [LinkedIn](https://www.linkedin.com/in/ali-akbar-ab924860/). 

## Environment Setup

During development we used `Python`'s (version 3.8 or higer) [`miniconda`](https://docs.conda.io/en/latest/miniconda.html) This is recommended as it can help control dependencies and the version of those dependencies are imported easily without breaking your existing repositories. 

```bash
conda create --name witsms matplotlib pandas numpy openpyxl
conda activate witsms
```

In order to clone the repository. Use the following code.
```bash
git clone https://github.com/LUMS-WIT/WIT-SMS.git
cd WIT-SMS
```
The structure of cloned repository should be as following:
```
WIT-SMS 
 ├── test_data
 │      ├── processed 
 │      │      └── 30_min
 │      │      └── ...
 │      ├── raw
 │      │      └── 2021
 │      │      └── ...
 │      ├── metadata.xlsx 
 └── *.py
```
The metadata file contains the information about soil moisture data files segregated into separate sheets. Each sheet is named for the year of installation of probe. You can enter all relevent information about the sensor installation in the corresponding sheet. 

The data to be processed has be to placed inside the corresponding year folder in raw folder. Please follow the data format as given in the examples files. Presently two different files have been placed inside raw folder which can be used as the reference. 

The processed folder contains the output of the processing. Currently the code supports **half-hourly**, **hourly**, **tri-hourly** and **daily** aggregates.

> [!NOTE]
> The format for the TimeStamp column of data file needs to be mm/dd/yyyy h:mm:ss am/pm. You can copy this to format the same column in MS excel file.

## Usage

### Processing Raw Data
First you need to setup the global variables inside the [config.py](config.py) python file. These include the paths and tolerance values for pre-processing the soil moisture data. Once done, execute the [witsms_processing.py](witsms_processing.py) as following:

```bash
python witsms_processing.py
```
If successfully executed, the outputs would be generated inside the processed folder.

### Visualization of Processed Data
The processed soil moisture data can be visualized using the provided Python scripts. The main script for visualization is [witsms_reader.py](witsms_reader.py), which allows you to print metadata, save metadata to a CSV file, and plot soil moisture data for specific GPIs or all GPIs.

Please setup the path for the desired processed data folder inside *config.py* file before proceeding.

#### Command-Line Arguments for Visualization

- `--print-metadata`: Prints the metadata of the processed files in CSV format.
- `--save-metadata`: Saves the metadata of the processed files.
- `--plot-gpi [GPI]`: Plots soil moisture data for the specified SMS ID refered as GPI.

#### Example Usages

1. **Print Metadata to Console**
    ```bash
    python witsms_reader.py --print-metadata
    ```
    This command will read the data and print the metadata to the console in CSV format.

2. **Save Metadata to a CSV File**
    ```bash
    python witsms_reader.py --save-metadata
    ```
    This command will read the data and save the metadata to a file named `metadata.csv`.

3. **Plot Data for a Specific GPI**
    ```bash
    python witsms_reader.py --plot-gpi 2023110
    ```
    This command will plot soil moisture data for the GPI `2023110`.

4. **Plot Data for All GPIs**
    ```bash
    python witsms_reader.py --plot-gpi
    ```
    This command will plot soil moisture data for all available GPIs.

5. **Combine Multiple Arguments**
    ```bash
    python witsms_reader.py --print-metadata --save-metadata --plot-gpi 2023110
    ```
    This command will print metadata to the console, save it to `metadata.csv`, and plot soil moisture data for the GPI `2023110`.

> [!NOTE]
> If `--plot-gpi` is provided without a specific GPI, the script will plot data for all available GPIs.

## Contributing

todo: Guidelines for how others can contribute to the project

## Citation 

todo: guide to how to cite this work