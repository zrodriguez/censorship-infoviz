import pandas as pd

# Load the dataset
df = pd.read_csv('./datasets/penAmericaIndex2022.csv')

# Fill missing values
df['Author'].fillna('No author', inplace=True)
df['Title'].fillna('No title', inplace=True)
df.loc[df['Date of Challenge/Removal'] == 'AY 2022-2023', 'Date of Challenge/Removal'] = 'December 2022'

# Drop missing and duplicate values
# df.dropna(inplace=True)
# df.drop_duplicates(inplace=True)

# Strip whitespaces from the `date_added` col and convert values to `datetime`
df['Date of Challenge/Removal'] = pd.to_datetime(df['Date of Challenge/Removal'].str.strip())

# Save the cleaned dataset
df.to_csv('./datasets/penAmericaIndex2022.csv', index=False)