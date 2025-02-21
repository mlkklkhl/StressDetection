import pandas as pd
import os
import neurokit2 as nk
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

def load_and_prepare_data(file_path):
    df = pd.read_csv(file_path)
    # Keep only timestamp and the relevant measurement column (EA or PG)
    value_col = 'EA' if 'EA' in df.columns else 'PG'
    return df[['LocalTimestamp', value_col]]

def prepare_eda_data(eda_df):
    signals, info = nk.eda_process(eda_df['EA'], sampling_rate=15, scr_min_amplitude=0.01)
    nk.eda_plot(signals, info)
    plt.show()

    extracted_df = pd.DataFrame()
    extracted_df['EDA'] = signals['EDA_Clean']
    extracted_df['EDA_Tonic'] = signals['EDA_Tonic']
    extracted_df['EDA_Phasic'] = signals['EDA_Phasic']

    # set the timestamp to the signals
    extracted_df['Timestamp'] = pd.to_datetime(eda_df['LocalTimestamp'], unit='s').dt.tz_localize('UTC').dt.tz_convert(
        'Asia/Bangkok')

    # Convert the timestamp to datetime and set it as index
    extracted_df = extracted_df.set_index('Timestamp')

    # Downsample to 1Hz
    extracted_df = extracted_df.resample("1s").mean()

    return extracted_df

def prepare_ppg_data(ppg_df, window_size, sampling_rate):

    # Calculate window parameters in samples
    window_samples = window_size * sampling_rate

    ppg_df['Timestamp'] = pd.to_datetime(ppg_df['LocalTimestamp'], unit='s').dt.tz_localize('UTC').dt.tz_convert(
        'Asia/Bangkok')

    ppg_df.drop(columns=['LocalTimestamp'], inplace=True)

    print(ppg_df.head().to_string())

    ppg_cleaned = nk.ppg_clean(ppg_df['PG'], sampling_rate=sampling_rate)

    hrv_results = []

    # Slide window over the signal
    for start in range(0, len(ppg_cleaned) - window_samples):
        end = start + window_samples
        window = ppg_cleaned[start:end]

        start_time = ppg_df['Timestamp'].iloc[start]

        print(f"Processing window at {start / sampling_rate}s - {end / sampling_rate}s")

        # Process PPG for this window
        ppg_processed, info = nk.ppg_process(window, sampling_rate=sampling_rate)

        # Extract peaks directly from the processed signal
        signals, info = nk.ppg_peaks(ppg_processed['PPG_Clean'], sampling_rate=sampling_rate)

        # Calculate HRV metrics directly
        hrv_metrics = nk.hrv(signals, sampling_rate=sampling_rate)

        hrv_metrics['Timestamp'] = start_time

        hrv_results.append(hrv_metrics)

    hrv_df = pd.concat(hrv_results, ignore_index=True)

    hrv_df['Timestamp'] = pd.to_datetime(hrv_df['Timestamp'])
    hrv_df = hrv_df.set_index('Timestamp')

    # Downsample to 1Hz
    extracted_df = hrv_df.resample("1s").mean()

    # Create HR column from 60/(HRV_MeanNN/1000)
    extracted_df['HR'] = 60 / (extracted_df['HRV_MeanNN'] / 1000)

    return extracted_df


def process_subject(subject_num, eda_dir, ppg_dir, output_dir):

    # Construct file paths
    eda_file = os.path.join(eda_dir, f'S{subject_num:02d}_eda.csv')
    ppg_file = os.path.join(ppg_dir, f's{subject_num:02d}_pg.csv')

    # Check if both files exist
    if not (os.path.exists(eda_file) and os.path.exists(ppg_file)):
        print(f"Missing files for subject {subject_num}")
        return

    # Load and prepare EDA datasets
    eda_df = load_and_prepare_data(eda_file)
    extracted_eda_df = prepare_eda_data(eda_df)

    # Load and prepare PPG datasets
    ppg_df = load_and_prepare_data(ppg_file)
    extracted_hrv_df = prepare_ppg_data(ppg_df, window_size=300, sampling_rate=100)

    # Merge datasets based on timestamp
    merged_df = pd.merge_asof(
        extracted_hrv_df.sort_values('Timestamp'),
        extracted_eda_df.sort_values('Timestamp'),
        on='Timestamp',
        direction='nearest'
    )

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Save merged data
    output_file = os.path.join(output_dir, f'S{subject_num:02d}_combined.csv')
    merged_df.to_csv(output_file, index=False)
    print(f"Processed subject {subject_num}: {merged_df.shape[0]} rows")


def main():
    # Define directories
    eda_dir = 'data/Raw/eda'
    ppg_dir = 'data/Raw/ppg'
    output_dir = 'data/Combined'

    # If the output directory doesn't exist, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Process all subjects (1 to 25)
    for subject_num in range(1, 26):
        process_subject(subject_num, eda_dir, ppg_dir, output_dir)

if __name__ == "__main__":
    main()


