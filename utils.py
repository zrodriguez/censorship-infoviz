import us
import gmaps
import pandas as pd
import base64
from io import BytesIO


def import_df(filename):
    df = pd.read_csv(filename)
    return df


def top_var(index, var):
  states = list(index['State'].unique())
  top_var = []
  for state in states:
    state_data = index[index['State'] == state]
    state_data = state_data.groupby([var]).size().reset_index(name='Challenges')
    state_data = state_data.iloc[:1]
    # print(state_data[var][0])
    top_var.append(state_data[var][0])
  return top_var


def get_state_abb(index):
  states = list(index['State'].unique())
  states_coded = []
  for state in states:
    states_coded.append(us.states.lookup(state).abbr)
  return states_coded


def format_name(index, var):
  index[['LastName', 'FirstName']] = index[var].str.split(',', expand=True)

  index['FirstName'] = index['FirstName'].str.strip()
  index['LastName'] = index['LastName'].str.strip()

  index[var] = index['FirstName'] + " " + index['LastName']

  index = index.drop(columns=['LastName', 'FirstName'])
  # print(index)
  return index


def get_unqiue_title_count(sources, index):
  sources = list(index['Source'].unique())
  unqiue_title_counts = []
  for source in sources:
    unique_count = index.loc[index['Source']==source,'Title'].agg(['nunique'])[0]
    # print(unique_count)
    unqiue_title_counts.append(unique_count)
  return unqiue_title_counts


def make_image(index):
    img = BytesIO()
    #title_word_cloud(index).save(img, format='PNG')
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())