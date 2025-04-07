import pandas as pd
import numpy as np
import re

# Read the CSV file
df = pd.read_csv('raw_battlelogs.csv')
# Remove duplicate rows from the DataFrame
df = df.drop_duplicates()
df = df.reset_index(drop=True)
# Extract the specified columns
columns_to_extract = ['event_mode', 'event_map', 'battle_mode', 'battle_type', 'battle_result', 'battle_teams']
extracted_data = df[columns_to_extract]

# Filter out friendly games and draws
filtered_data = extracted_data[(extracted_data['battle_type'] != 'friendly') & (extracted_data['battle_result'] != 'draw')]

# Consolidate 'event_mode' and 'battle_mode' into one column
filtered_data['mode'] = filtered_data.apply(
    lambda row: row['event_mode'] if pd.notna(row['event_mode']) else row['battle_mode'], axis=1
)

# Remove rows where both 'event_mode' and 'battle_mode' are empty
filtered_data = filtered_data.dropna(subset=['mode'])

# Remove rows with specific modes
modes_to_remove = ['bigGame', 'bossFight', 'roboRumble', 'lastStand', 'soloShowdown', 'duoShowdown']
filtered_data = filtered_data[~filtered_data['mode'].isin(modes_to_remove)]

# Drop the original 'event_mode' and 'battle_mode' columns
filtered_data = filtered_data.drop(columns=['event_mode', 'battle_mode'], errors='ignore')


# Function to extract brawler data using regular expressions
def extract_brawler_data(battle_teams):
    if pd.isna(battle_teams):
        return []
    pattern = r"'brawler': \{[^}]+\}"
    matches = re.findall(pattern, battle_teams)
    brawlers = []
    for match in matches:
        brawler_info = eval(match.split(": ", 1)[1])
        brawlers.append(brawler_info['name'])
        brawlers.append(brawler_info['power'])
        brawlers.append(brawler_info['trophies'])
    return brawlers

# Apply the function to extract brawler data
filtered_data['brawler_data'] = filtered_data['battle_teams'].apply(extract_brawler_data)

# Create new column names
new_columns = []
for team in range(1, 3):
    for brawler in range(1, 4):
        new_columns.append(f'team {team} brawler {brawler}')
        new_columns.append(f'team {team} brawler {brawler} power')
        new_columns.append(f'team {team} brawler {brawler} trophies')

# Create a DataFrame with the new columns
brawler_df = pd.DataFrame(filtered_data['brawler_data'].tolist(), columns=new_columns)

# Drop the original 'battle_teams' and 'brawler_data' columns
filtered_data = filtered_data.drop(columns=['battle_teams', 'brawler_data'])

# Concatenate the new columns with the filtered_data DataFrame
final_data = pd.concat([filtered_data, brawler_df], axis=1)
final_data = final_data.dropna()

# Separate 'battle_result' into its own list
battle_result = final_data['battle_result']
battleResultList = battle_result.tolist()

# Remove 'battle_result' from the filtered data
final_data = final_data.drop(columns=['battle_result'])

# Convert the final DataFrame to a NumPy matrix
numpy_matrix = final_data.to_numpy()

# Print the results
print("Final NumPy Matrix:")
print(numpy_matrix)
print("\nBattle Result List:")
print(battle_result)
print(len(battle_result))
# Save final_data to a CSV file
final_data.to_csv('final_data.csv', index=False)

# Save battle_result to a CSV file
battle_result.to_csv('battle_result.csv', index=False)