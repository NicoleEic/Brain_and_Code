import os
import sys
import pandas as pd
import numpy as np
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
import plotly.express as px
from ipywidgets import widgets
import plotly.io as pio
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
pio.renderers.default = "browser"
pd.set_option('mode.chained_assignment', None)

my_min = -3000
my_max = 2000

# load total data file
#df = prep_data()
#set_ypos()

# or load
df = pd.read_csv(os.path.join(os.path.dirname(sys.argv[0]), 'timeline_prep.csv'))


def prep_data():
    df = pd.read_csv(os.path.join(os.path.dirname(sys.argv[0]), 'timeline.csv'))
    df_cat = pd.read_csv(os.path.join(os.path.dirname(sys.argv[0]), 'timeline_types.csv'))
    # replace missing date_to by date_from
    df['date_to'] = np.where(np.isnan(df['date_to']), df['date_from'], df['date_to'])
    df['date_from'] = df['date_from'].astype(pd.Int64Dtype())
    df['date_to'] = df['date_to'].astype(pd.Int64Dtype())
    df = df.loc[(df['date_from'] >= my_min) & (df['date_to'] + 1 < my_max)]
    # add column for duration of event (min 1 year)
    df['duration'] = df['date_to'] - df['date_from']
    df['duration'] = np.where(df.duration < 1, 1, df['duration'])
    # map category
    di = df_cat.set_index('timeline_type_id')['timeline_type_name'].to_dict()
    df['timeline_type_name'] = df['timeline_type_id'].map(di)
    df = df.sort_values(['timeline_type_id', 'date_from'])
    df.index = pd.RangeIndex(len(df.index))
    return df

def set_ypos():
    # initialize parameters
    ypos_arr = np.array([0])
    ypos_group = 0
    ymax = 0
    # loop over categories
    for cat in np.unique(df['timeline_type_id'].values):
        print(cat)
        group = df[df.timeline_type_id == cat]
        filled = pd.DataFrame(columns=['ypos', 'on', 'off'])
        # draw event as rectangle
        for ind, row in group.iterrows():
            # draw the event in the next free row
            ypos = ypos_group + 1
            while any((filled['ypos'] == ypos) & (((filled['on'] < (row['date_from'] - 1)) & ((row['date_from'] - 1) < filled['off'])) | ((filled['on'] < (row['date_to'] - 1)) & ((row['date_from'] + row['duration'] + 1) < filled['off'])))):
                ypos += 1
            if ypos > ymax:
                ymax = ypos
            filled = filled.append({'ypos': ypos, 'on': row['date_from'], 'off': row['date_from'] + row['duration']}, ignore_index=True)
            ypos_arr = np.append(ypos_arr, ypos)
        # start a new cateory in a new row
        ypos_group = ymax
    ypos_arr = np.delete(ypos_arr, 0)
    df['ypos'] = ypos_arr
    df.to_csv(os.path.join(os.path.dirname(sys.argv[0]), 'timeline_prep.csv'))


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Graph(id='my_plot'),
    html.H6("Search:"),
    html.Div([dcc.Input(id='my-input', value='Rome', type='text')]),
    html.Br(),
])

@app.callback(
    Output(component_id='my_plot', component_property='figure'),
    Input(component_id='my-input', component_property='value')
)
def update_my_plot(search_string):
    hits = df[df['text_raw'].str.contains(search_string)]
    if len(hits) > 0:
        output = hits.iloc[0]['text_raw']
        df.at[0:200, 'category'] = 'selected'

    df['category'] = df['timeline_type_name']
    df.at[0:len(search_string), 'category'] = 'selected'
    fig = px.timeline(df, x_start="date_from", x_end="date_to", y="ypos", hover_name="text_raw",
                      hover_data=["date_from", "date_to"], color='category', height=600)
    fig.layout.xaxis.type = 'linear'
    for i_d, dat in enumerate(fig.data):
        fig.data[i_d].x = df[df['category'] == dat.name].duration.tolist()
    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="linear"))
    fig.layout.yaxis.autorange = "reversed"
    fig.layout.yaxis.visible = False
    fig.update_layout(title_text="Interactive timeline")
    # fig.show()
    # fig.write_html(os.path.join(os.path.dirname(sys.argv[0]), "my.html"))
    return fig


app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter