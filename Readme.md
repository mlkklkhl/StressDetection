# StressDetection Project

This project is developed by COEAI, Walailak University. The goal of this project is to detect stress levels using physiological data such as Electrodermal Activity (EDA) and Photoplethysmogram (PPG).

## Dependencies

To run this project, you need the following dependencies:

- Python 3.8+
- pandas
- neurokit2
- numpy
- os
- datetime

You can install the required Python packages using the following command:

```bash
pip install pandas neurokit2 numpy
```

## Project Structure

- `combine_raw_data.py`: Main script to process and combine raw EDA and PPG data.
- `data/Raw/eda`: Directory containing raw EDA data files.
- `data/Raw/ppg`: Directory containing raw PPG data files.
- `data/Combined`: Directory where the combined data files will be saved.

## Usage

To process the data for all subjects, run the following command:

```bash
python combine_raw_data.py
```

This will process the data for subjects 1 to 25 and save the combined data files in the `data/Combined` directory.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
