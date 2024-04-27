from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go

import gmaps
import pandas as pd
from dash import dcc, html

from wordcloud import WordCloud, STOPWORDS

from PIL import Image
from IPython.core.display import HTML

from utils import *


def heat_map(index):
  state_info = index.groupby(['State']).size().reset_index(name='Challenges')

  state_info['State code'] = get_state_abb(state_info)
  state_info['Most Banned Author'] = top_var(index, 'Author')
  state_info['Most Banned Title'] = top_var(index, 'Title')

  state_info = format_name(state_info, 'Most Banned Author')

  # print(state_info)

  fig = go.Figure(data=go.Choropleth(
    locations = state_info['State code'],
    z = state_info['Challenges'].astype(float),
    locationmode = 'USA-states',
    colorscale = 'Reds',
    colorbar_title = 'Challenges',
    text = state_info['State'] + "<br>Most challenged author: " + state_info['Most Banned Author'] 
              + "<br>Most challenged title: " + state_info['Most Banned Title']
  ))

  fig.update_layout(
    width=1280, height=720, title_x=0.5,
    title_text = 'Book Bans and Challeneges by state<br>(Hover over the states for details)',
    geo_scope='usa',
  )

  return fig


def stacked_barchart(index):
  total_counts = index.groupby(['Source']).size().reset_index(name='Total Challenges')
  total_counts['Unique Title Challenges'] = get_unqiue_title_count(total_counts, index)

  fig = px.bar(total_counts, x=['Total Challenges','Unique Title Challenges'], y='Source', 
               orientation='h', barmode='group',
               color_discrete_map={'Total Challenges': '#5A0001','Unique Title Challenges': '#F13030'})

  fig.update_layout(
    width=1280, height=540, title_x=0.5,
    title_text = "Total and Unique Title Challenges")

  return fig


def author_bargraph(index):
  author_counts = index.groupby(['Author']).size().reset_index(name='Challenges')
  author_counts = (author_counts.sort_values(by=['Challenges'], ascending=False)).iloc[:15]
  # print(author_counts)

  author_counts = format_name(author_counts, 'Author')

  fig = px.bar(author_counts, x='Author', y='Challenges',
               color_discrete_sequence=px.colors.sequential.Inferno)
  fig.update_layout(
    width=640, height=540, title_x=0.5,
    title_text = "Most Challenged Authors")

  return fig


def title_bargraph(index):
  title_counts = index.groupby(['Title', 'Author']).size().reset_index(name='Challenges')
  title_counts = (title_counts.sort_values(by=['Challenges'], ascending=False)).iloc[:15]
  # print(title_counts)

  title_counts = format_name(title_counts, 'Author')

  fig = px.bar(title_counts, x='Title', y='Challenges', hover_data='Author',
               color_discrete_sequence=px.colors.sequential.Inferno)
  fig.update_layout(
    width=640, height=540, title_x=0.5,
    title_text = "Most Challenged Titles")

  return fig


def title_wordcloud(index, unique):
  titles = list(index['Title'])

  if unique:
    titles = list(index['Title'].unique())

  text = " ".join(str(title) for title in titles)

  stopwords = set(STOPWORDS)
  stopwords.update(["Series", "Book", "Memoir", "Story", "Vol", "Novel", "Graphic Novel"])
  wordcloud = WordCloud(stopwords=stopwords, 
                        background_color="white", colormap="inferno", 
                        width=1280, height=540).generate(text)

  # fig = wordcloud.to_image()
  fig = px.imshow(wordcloud)
  fig.update_layout(
    width=1280, height=540,
    showlegend=False,
    title_text = "Common Words in Challenged Titles")
  
  return fig


def get_breakdown(index):
  # index = index.dropna(subset=['Author'], inplace=True)
  # print(index)
  index = index.explode('Title')

  index_counts = index.groupby(['Author', 'Title']).size().reset_index(name='Challenges')
  index_counts = (index_counts.sort_values(by=['Challenges'], ascending=False)).iloc[:200]

  index_counts = format_name(index_counts, 'Author')

  fig = px.treemap(index_counts, path=['Author', 'Title'], values='Challenges', color='Challenges',
                  color_continuous_scale='YlOrRd', title='Top 200 Banned Books by Author and Title')

  fig.update_layout(width=1280, height=960, title_x=0.5)
  # fig.update_traces(textinfo='label+percent entry', textfont_size=14)

  return fig


def timeline(index):
  # TODO: drop non dates from column
  # index = index.drop(index.index[index['Date of Challenge/Removal'] == "AY 2022-2023"], inplace = True)
  # index = index.drop(index.loc[index['Date of Challenge/Removal'] == "AY 2022-2023"].index, inplace=True)
  index['Date'] = pd.to_datetime(index['Date of Challenge/Removal'], format='%B %Y')
  monthly_challenges = (index['Date'].value_counts())
  index = index.sort_values(by='Date')
  fig = monthly_challenges.plot(kind='line')
  return fig


def get_cover(path):
  pil_image = Image.open(path)
  return html.Img(src=pil_image)


def b64_image(image_filename):
    with open(image_filename, 'rb') as f:
        image = f.read()
    return 'data:image/png;base64,' + base64.b64encode(image).decode('utf-8')


def about_bans(index):
  covers = import_df('./datasets/bannedBookLinks.csv')
  titles = index.groupby(['Title', 'Author']).size().reset_index(name='Challenges')
  titles = (titles.sort_values(by=['Challenges'], ascending=False)).iloc[:10]
  
  titles = pd.merge(titles, covers, on=['Title', 'Author'])

  titles = format_name(titles, 'Author')
  titles['Title and Author'] = titles['Title'] + ' by ' + titles['Author']
  # print(titles.columns)
  # titles['Image'] = titles.apply(lambda titles: b64_image(titles['Image']), axis=1)

  table = titles.drop(columns=['Image', 'Website', 'Challenges', 'Title', 'Author'])

  fig = go.Figure(data=[go.Table(
    # header=dict(values=list(table.columns),
    #             line_color='white', fill_color='white', align='left'),
    cells=dict(values=table.transpose().values.tolist(), height=50,
               line_color='white',fill_color='white', align=['left', 'right'], font_size=14))
  ])
  fig.for_each_trace(lambda t: t.update(header_fill_color = 'rgba(0,0,0,0)'))

  # for png in table['Image']:
  #   fig.add_layout_image(
  #       source=Image.open(png),
  #       sizex=0.5,
  #       sizey=0.5,
  #       xanchor="center",
  #       yanchor="middle",
  #   )

  fig.update_layout(
    width=1280, height=960, title_x=0.5,
    title='Their Words',
  )
  
  return fig


def main(index):
  heap_map = heat_map(index)
  author_bar = author_bargraph(index)
  title_bar = title_bargraph(index)
  breakdown = get_breakdown(index)
  stacked = stacked_barchart(index)
  about_sec = about_bans(index)
  
  bar_graphs = make_subplots(rows=1, cols=2)
  bar_graphs.add_trace(author_bar.data[0], row=1, col=1,)
  bar_graphs.add_trace(title_bar.data[0], row=1, col=2,)
  bar_graphs.update_layout(width=1280, height=540, title_x=0.5, 
                           title_text = 'Most Challenged Authors and Titles')

  # word_cloud = title_wordcloud(index, True)

  layout = html.Div([
    dcc.Graph(figure=heap_map),
    html.Hr(),
    dcc.Graph(figure=stacked),
    dcc.Graph(figure=bar_graphs),
    html.Hr(),
    dcc.Graph(figure=breakdown),
    html.Hr(),
    dcc.Graph(figure=about_sec),
    # html.Hr(),
    # dcc.Graph(figure=word_cloud),
  ])
  
  return layout
