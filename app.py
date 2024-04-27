from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from components import (
    content
)
import pandas as pd
from utils import import_df


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    [
        dcc.Store(id='store'),
        html.H1('Literary Censorship in the United States'),
        html.Hr(),
        dbc.Tabs(
            [
                dbc.Tab(label='All', tab_id='tab1'),
                dbc.Tab(label='2021-2022', tab_id='tab2'),
                dbc.Tab(label='2022-2023', tab_id='tab3'),
                # TODO: wait for PEN America published index
                dbc.Tab(label='2023-2024', tab_id='tab4'),
            ],
            id='tabs',
            active_tab='tab1',
        ),
        html.Div(id='tab-content', className='p-4'),
    ]
)

# Datasets
index2022 = import_df("./datasets/penAmericaIndex2022.csv")
index2022['Source'] = '2021-2022'

index2023 = import_df("./datasets/penAmericaIndex2023.csv")
index2023['Source'] = '2022-2023'

index = pd.concat([index2022, index2023])


@app.callback(Output('tab-content', 'children'), [Input('tabs', 'active_tab')])
def switch_tab(at):
    if at == 'tab1':
        return content.main(index)
    elif at == 'tab2':
        return content.main(index2022)
    elif at == 'tab3':
        return content.main(index2023)


if __name__ == '__main__':
    app.run(debug=True)
