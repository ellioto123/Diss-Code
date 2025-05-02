import pandas as pd
import numpy as np
import re

df= pd.read_csv('raw_battlelogs.csv')
# remove duplicates
df= df.drop_duplicates()
df= df.reset_index(drop=True)
# extract relevant columns
columnsToExtract= ['event_mode', 'event_map', 'battle_mode', 'battle_type', 'battle_result', 'battle_teams']
extractedData= df[columnsToExtract]
# filter friendlies and games that end in draws
filteredData= extractedData[(extractedData['battle_type']!='friendly') &(extractedData['battle_result']!='draw')]
# consolidate event_mode and battle_mode 
filteredData['mode']= filteredData.apply(lambda row:row['event_mode'] if pd.notna(row['event_mode']) else row['battle_mode'] , axis=1)
# omit rows where both 'event_mode' and 'battle_mode' are empty
filteredData= filteredData.dropna(subset = ['mode'])
# remove rows with non comp modes
modesToRemove= ['bigGame', 'bossFight', 'roboRumble', 'lastStand', 'soloShowdown', 'duoShowdown']
filteredData= filteredData[ ~filteredData[ 'mode'].isin(modesToRemove )]

# remove the original 'event_mode' and 'battle_mode' as we have alr created 'mode'
filteredData= filteredData.drop( columns=['event_mode' , 'battle_mode'], errors ='ignore')


#function - extract brawler data using regex 
def extractBrawlerData(battleTeams):
    if pd.isna( battleTeams ):
        return  []
    pat = r"'brawler': \{[^}]+\}"
    matches = re.findall(pat, battleTeams)
    brawlers = []
    for match in matches:
        brawlerInfo = eval(match.split(": ",  1)[1 ])
        brawlers.append(brawlerInfo[ 'name'])
        brawlers.append(brawlerInfo[ 'power'])
        brawlers.append(brawlerInfo[ 'trophies'])
    return brawlers

# use func to extract brawler data
filteredData['brawler_data']= filteredData['battle_teams'].apply( extractBrawlerData)

# create new columns for each brawlers stats
newColumns =  []
for team in range(1, 3):
    for brawler in range(1, 4):
        newColumns.append(f'team {team} brawler {brawler}')
        newColumns.append(f'team {team} brawler {brawler} power')
        newColumns.append(f'team {team} brawler {brawler} trophies')

# create a df with the brawler stat columns
brawlerDf = pd.DataFrame(filteredData['brawler_data'].tolist(),columns= newColumns )

#drop the 'battle_teams' and 'brawler_data' columns as they are no longer needed
filteredData = filteredData.drop( columns=['battle_teams','brawler_data'])

# concat the new columns with the filtered data df
final_data = pd.concat( [filteredData, brawlerDf] , axis=1)
final_data = final_data.dropna()

# separate 'battle_result' into its own list as this will be y values
battle_result = final_data['battle_result']
battleResultList = battle_result.tolist()

# remove 'battle_result' from final data
final_data = final_data.drop(columns=['battle_result'])



#save to CSV files
final_data.to_csv('final_data.csv', index=False)

battle_result.to_csv('battle_result.csv', index=False)

