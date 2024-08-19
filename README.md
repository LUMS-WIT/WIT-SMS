# WIT-SMS
The Center for Water Informatics & Technology (WIT) hosts an IoT-based soil moisture network consisting of more than 200
soil moisture nodes installed throughout the Indus Basin. The purpose of this repository is pre-processing and visualization WITSMS-Network soil moisture data which can then be used for downstream tasks.

## Data Accesse
In order to access the data, please contact WIT's Business Development Manager [email](mailto:a.abbas@lums.edu.pk) or at [LinkedIn](https://www.linkedin.com/in/ali-akbar-ab924860/). 

## Environment Setup

During development we used `Python`'s (verion 3.8 or higer) [`miniconda`](https://docs.conda.io/en/latest/miniconda.html) This is recommended as it can help control dependencies and the version of those dependencies are imported easily without breaking your existing repositories. 

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

The processed folder contains the output of the processing. Currently the code supports 30 mins, hourly, tri-hourly and daily averages.

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
todo: Steps to run the code and any relevant script

## Contributing

todo: Guidelines for how others can contribute to the project

## Citation 

todo: guide to how to cite this work