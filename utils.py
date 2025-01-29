import pandas as pd
import os

def load_csv_files_from_folder(folder_path):


    files = os.listdir(folder_path)


    csv_files = [f for f in files if f.endswith('.csv')]

    

    # Initialize a list to hold the dataframes

    dataframes = []

    

    # Read each CSV file into a DataFrame and append to the list

    for csv_file in csv_files:

        file_path = os.path.join(folder_path, csv_file)

        df = pd.read_csv(file_path)
        
        df['deck_id'] = csv_file

        dataframes.append(df)
        
    return dataframes