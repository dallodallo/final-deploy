import base64
import datetime
import io
import plotly.figure_factory as ff
import dash_daq as daq
import dash_auth
import dash  # pip install dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc  # pip install dash-bootstrap-components
import plotly.express as px  # pip install plotly
import plotly.graph_objects as go
import pandas as pd
from datetime import date
import auth
import joblib
from dash.exceptions import PreventUpdate

model = joblib.load("modell")
#  -*- coding: utf-8 -*-
# print(model)

tim = ["Lunch", "Breakfast", "Supper"] 
dt = datetime.datetime.now()
dt = dt.strftime("%B %d,%Y" "|" "%H:%M:%S")
# print(dt)

df = pd.read_csv("test.csv")
# external_stylesheets=[dbc.themes.BOOTSTRAP],
app = dash.Dash(__name__, suppress_callback_exeception=True, meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}] title='Possibility Dash Apps Analytics')

server = app.server

auth = dash_auth.BasicAuth(
    app,
    auth.approve()
)

df['City'] = df['Tax'].apply(lambda x:
                             '⭐⭐⭐' if x > 30 else (
                                 '⭐⭐' if x > 20 else (
                                     '⭐' if x > 10 else ''
                                 )))
df['cogs'] = df['Total'].apply(lambda x: '↗️' if x > 500 else '↘️')


def data_bars(df, column):
    n_bins = 100
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    ranges = [
        ((df[column].max() - df[column].min()) * i) + df[column].min()
        for i in bounds
    ]
    styles = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        max_bound_percentage = bounds[i] * 100
        styles.append({
            'if': {
                'filter_query': (
                        '{{{column}}} >= {min_bound}' +
                        (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                'column_id': column
            },
            'background': (
                """
                    linear-gradient(90deg,
                    #0074D9 0%,
                    #0074D9 {max_bound_percentage}%,
                    white {max_bound_percentage}%,
                    white 100%)
                """.format(max_bound_percentage=max_bound_percentage)
            ),
            'paddingBottom': 2,
            'paddingTop': 2
        })

    return styles


def data_bars_diverging(df, column, color_above='#3D9970', color_below='#FF4136'):
    n_bins = 100
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    col_max = df[column].max()
    col_min = df[column].min()
    ranges = [
        ((col_max - col_min) * i) + col_min
        for i in bounds
    ]
    midpoint = (col_max + col_min) / 2.

    styles = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        min_bound_percentage = bounds[i - 1] * 100
        max_bound_percentage = bounds[i] * 100

        style = {
            'if': {
                'filter_query': (
                        '{{{column}}} >= {min_bound}' +
                        (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                'column_id': column
            },
            'paddingBottom': 2,
            'paddingTop': 2
        }
        if max_bound > midpoint:
            background = (
                """
                    linear-gradient(90deg,
                    white 0%,
                    white 50%,
                    {color_above} 50%,
                    {color_above} {max_bound_percentage}%,
                    white {max_bound_percentage}%,
                    white 100%)
                """.format(
                    max_bound_percentage=max_bound_percentage,
                    color_above=color_above
                )
            )
        else:
            background = (
                """
                    linear-gradient(90deg,
                    white 0%,
                    white {min_bound_percentage}%,
                    {color_below} {min_bound_percentage}%,
                    {color_below} 50%,
                    white 50%,
                    white 100%)
                """.format(
                    min_bound_percentage=min_bound_percentage,
                    color_below=color_below
                )
            )
        style['background'] = background
        styles.append(style)

    return styles


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    global df1
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df1 = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df1 = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            id='dt1',
            data=df1.to_dict('records'),
            columns=[{'name': i, 'id': i, "hideable": True} for i in df1.columns],
            page_size=15,
            editable=True,
            virtualization=True,
            row_deletable=True,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            column_selectable="single",
            row_selectable="multi",
            selected_columns=[],
            selected_rows=[],
            page_action="native",
            page_current=0,
            tooltip_delay=0,
            tooltip_duration=None,
            fixed_rows={'headers': True},
            style_table={'height': '400px', 'overflowY': 'auto', 'minWidth': '100%'},
            style_data={'border': '1px solid blue'},
            style_cell={'textAlign': 'left', 'border': '1px solid grey', 'minWidth': '180px', 'width': '180px',
                        'maxWidth': '180px', 'overflow': 'hidden', 'textOverflow': 'ellipsis', 'whiteSpace': 'normal'},
            fixed_columns={'headers': True, 'data': 3},
            style_header={
                'border': '1px solid black',
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            export_format='xlsx',
            export_headers='display',
            merge_duplicate_headers=True,
        ),
        html.Hr()  # horizontal line
    ])


fig = go.Figure()

# Add traces
fig.add_trace(go.Scatter(
    x=["2013-01-15", "2013-01-29", "2013-02-26", "2013-04-19", "2013-07-02",
       "2013-08-27",
       "2013-10-22", "2014-01-20", "2014-05-05", "2014-07-01", "2015-02-09",
       "2015-04-13",
       "2015-05-13", "2015-06-08", "2015-08-05", "2016-02-25"],
    y=["8", "3", "2", "10", "5", "5", "6", "8", "3", "3", "7", "5", "10", "10", "9",
       "14"],
    name="var0",
    text=["8", "3", "2", "10", "5", "5", "6", "8", "3", "3", "7", "5", "10", "10", "9",
          "14"],
    yaxis="y1",
))

fig.add_trace(go.Scatter(
    x=["2015-04-13", "2015-05-13", "2015-06-08", "2015-08-05", "2016-02-25"],
    y=["53.0", "69.0", "89.0", "41.0", "41.0"],
    name="var1",
    text=["53.0", "69.0", "89.0", "41.0", "41.0"],
    yaxis="y2",
))

fig.add_trace(go.Scatter(
    x=["2013-01-29", "2013-02-26", "2013-04-19", "2013-07-02", "2013-08-27",
       "2013-10-22",
       "2014-01-20", "2014-04-09", "2014-05-05", "2014-07-01", "2014-09-30",
       "2015-02-09",
       "2015-04-13", "2015-06-08", "2016-02-25"],
    y=["9.6", "4.6", "2.7", "8.3", "18", "7.3", "3", "7.5", "1.0", "0.5", "2.8", "9.2",
       "13", "5.8", "6.9"],
    name="var2",
    text=["9.6", "4.6", "2.7", "8.3", "18", "7.3", "3", "7.5", "1.0", "0.5", "2.8",
          "9.2",
          "13", "5.8", "6.9"],
    yaxis="y3",
))

fig.add_trace(go.Scatter(
    x=["2013-01-29", "2013-02-26", "2013-04-19", "2013-07-02", "2013-08-27",
       "2013-10-22",
       "2014-01-20", "2014-04-09", "2014-05-05", "2014-07-01", "2014-09-30",
       "2015-02-09",
       "2015-04-13", "2015-06-08", "2016-02-25"],
    y=["6.9", "7.5", "7.3", "7.3", "6.9", "7.1", "8", "7.8", "7.4", "7.9", "7.9", "7.6",
       "7.2", "7.2", "8.0"],
    name="var3",
    text=["6.9", "7.5", "7.3", "7.3", "6.9", "7.1", "8", "7.8", "7.4", "7.9", "7.9",
          "7.6",
          "7.2", "7.2", "8.0"],
    yaxis="y4",
))

fig.add_trace(go.Scatter(
    x=["2013-02-26", "2013-07-02", "2013-09-26", "2013-10-22", "2013-12-04",
       "2014-01-02",
       "2014-01-20", "2014-05-05", "2014-07-01", "2015-02-09", "2015-05-05"],
    y=["290", "1078", "263", "407", "660", "740", "33", "374", "95", "734", "3000"],
    name="var4",
    text=["290", "1078", "263", "407", "660", "740", "33", "374", "95", "734", "3000"],
    yaxis="y5",
))

# style all the traces
fig.update_traces(
    hoverinfo="name+x+text",
    line={"width": 0.5},
    marker={"size": 8},
    mode="lines+markers",
    showlegend=False
)

# Add annotations
fig.update_layout(
    annotations=[
        dict(
            x="2013-06-01",
            y=0,
            arrowcolor="rgba(63, 81, 181, 0.2)",
            arrowsize=0.3,
            ax=0,
            ay=30,
            text="state1",
            xref="x",
            yanchor="bottom",
            yref="y"
        ),
        dict(
            x="2014-09-13",
            y=0,
            arrowcolor="rgba(76, 175, 80, 0.1)",
            arrowsize=0.3,
            ax=0,
            ay=30,
            text="state2",
            xref="x",
            yanchor="bottom",
            yref="y"
        )
    ]
)

# Add shapes
fig.update_layout(
    shapes=[
        dict(
            fillcolor="rgba(63, 81, 181, 0.2)",
            line={"width": 0},
            type="rect",
            x0="2013-01-15",
            x1="2013-10-17",
            xref="x",
            y0=0,
            y1=0.95,
            yref="paper"
        ),
        dict(
            fillcolor="rgba(76, 175, 80, 0.1)",
            line={"width": 0},
            type="rect",
            x0="2013-10-22",
            x1="2015-08-05",
            xref="x",
            y0=0,
            y1=0.95,
            yref="paper"
        )
    ]
)

# Update axes
fig.update_layout(
    xaxis=dict(
        autorange=True,
        range=["2012-10-31 18:36:37.3129", "2016-05-10 05:23:22.6871"],
        rangeslider=dict(
            autorange=True,
            range=["2012-10-31 18:36:37.3129", "2016-05-10 05:23:22.6871"]
        ),
        type="date"
    ),
    yaxis=dict(
        anchor="x",
        autorange=True,
        domain=[0, 0.2],
        linecolor="#673ab7",
        mirror=True,
        range=[-60.0858369099, 28.4406294707],
        showline=True,
        side="right",
        tickfont={"color": "#673ab7"},
        tickmode="auto",
        ticks="",
        titlefont={"color": "#673ab7"},
        type="linear",
        zeroline=False
    ),
    yaxis2=dict(
        anchor="x",
        autorange=True,
        domain=[0.2, 0.4],
        linecolor="#E91E63",
        mirror=True,
        range=[29.3787777032, 100.621222297],
        showline=True,
        side="right",
        tickfont={"color": "#E91E63"},
        tickmode="auto",
        ticks="",
        titlefont={"color": "#E91E63"},
        type="linear",
        zeroline=False
    ),
    yaxis3=dict(
        anchor="x",
        autorange=True,
        domain=[0.4, 0.6],
        linecolor="#795548",
        mirror=True,
        range=[-3.73690396239, 22.2369039624],
        showline=True,
        side="right",
        tickfont={"color": "#795548"},
        tickmode="auto",
        ticks="",
        title="mg/L",
        titlefont={"color": "#795548"},
        type="linear",
        zeroline=False
    ),
    yaxis4=dict(
        anchor="x",
        autorange=True,
        domain=[0.6, 0.8],
        linecolor="#607d8b",
        mirror=True,
        range=[6.63368032236, 8.26631967764],
        showline=True,
        side="right",
        tickfont={"color": "#607d8b"},
        tickmode="auto",
        ticks="",
        title="mmol/L",
        titlefont={"color": "#607d8b"},
        type="linear",
        zeroline=False
    ),
    yaxis5=dict(
        anchor="x",
        autorange=True,
        domain=[0.8, 1],
        linecolor="#2196F3",
        mirror=True,
        range=[-685.336803224, 3718.33680322],
        showline=True,
        side="right",
        tickfont={"color": "#2196F3"},
        tickmode="auto",
        ticks="",
        title="mg/Kg",
        titlefont={"color": "#2196F3"},
        type="linear",
        zeroline=False
    )
)

# Update layout
fig.update_layout(
    dragmode="zoom",
    hovermode="x",
    legend=dict(traceorder="reversed"),
    height=600,
    template="plotly_white",
    margin=dict(
        t=100,
        b=100
    ),
)

fig7 = px.bar(df, x=df.Productline, y=df.Total, hover_data=['Gender', 'City', 'Tax'])

data = [dict(
    x=df['Date'],
    autobinx=False,
    autobiny=True,
    marker=dict(color='rgb(68, 68, 68)'),
    name='date',
    type='histogram',
    xbins=dict(
        end='12/27/2019',
        size='M1',
        start='1/12/2019'
    )
)]

layout = dict(
    paper_bgcolor='rgb(240, 240, 240)',
    plot_bgcolor='rgb(240, 240, 240)',
    title='<b>Stats for cooking</b>',
    xaxis=dict(
        title='Date',
        type='date'
    ),
    yaxis=dict(
        title='Total Sales',
        type='linear'
    ),
    updatemenus=[dict(
        x=0.1,
        y=1.15,
        xref='paper',
        yref='paper',
        yanchor='top',
        active=1,
        showactive=True,
        buttons=[
            dict(
                args=['xbins.size', 'D1'],
                label='Electronic accessories',
                method='restyle',
            ), dict(
                args=['xbins.size', 'D1'],
                label='Food and beverages',
                method='restyle',
            ), dict(
                args=['xbins.size', 'D1'],
                label='Health and beauty',
                method='restyle',
            ), dict(
                args=['xbins.size', 'D1'],
                label='Fashion accessories',
                method='restyle',
            ), dict(
                args=['xbins.size', 'D1'],
                label='Sports and travel',
                method='restyle',
            )]
    )]
)

fig1 = dict(data=data, layout=layout)

# Create figure
fig2 = go.Figure()

# Add traces
fig2.add_trace(
    go.Scatter(
        x=df.Time,
        y=df.Total,
        mode="markers",
        marker=dict(color="DarkOrange")
    )
)

fig2.add_trace(
    go.Scatter(
        x=df.Time,
        y=df.grossincome,
        mode="markers",
        marker=dict(color="Crimson")
    )
)

fig2.add_trace(
    go.Scatter(
        x=df.Time,
        y=df.Rating,
        mode="markers",
        marker=dict(color="RebeccaPurple")
    )
)

# Add buttons that add shapes
cluster0 = [dict(type="circle",
                 xref="x", yref="y",
                 x0=min(df.Time), y0=min(df.Total),
                 x1=max(df.Time), y1=max(df.Total),
                 line=dict(color="DarkOrange"))]
cluster1 = [dict(type="circle",
                 xref="x", yref="y",
                 x0=min(df.Time), y0=min(df.grossincome),
                 x1=max(df.Time), y1=max(df.grossincome),
                 line=dict(color="Crimson"))]
cluster2 = [dict(type="circle",
                 xref="x", yref="y",
                 x0=min(df.Time), y0=min(df.Rating),
                 x1=max(df.Time), y1=max(df.Rating),
                 line=dict(color="RebeccaPurple"))]

fig2.update_layout(
    updatemenus=[
        dict(
            type="buttons",
            buttons=[
                dict(label="None",
                     method="relayout",
                     args=["shapes", []]),
                dict(label="Cluster 0",
                     method="relayout",
                     args=["shapes", cluster0]),
                dict(label="Cluster 1",
                     method="relayout",
                     args=["shapes", cluster1]),
                dict(label="Cluster 2",
                     method="relayout",
                     args=["shapes", cluster2]),
                dict(label="All",
                     method="relayout",
                     args=["shapes", cluster0 + cluster1 + cluster2])
            ],
        )
    ]
)

# Update remaining layout properties
fig2.update_layout(
    title_text="Time series exploration",
    showlegend=True,
)

fig5 = go.Figure()

# Add Traces

fig5.add_trace(
    go.Scatter(x=list(df.Unitprice),
               y=list(df.Quantity),
               name="Comparing Unit price vs Quantity",
               line=dict(color="#33CFA5")))

fig5.add_trace(
    go.Scatter(x=list(df.Unitprice),
               y=[df.Quantity.mean()] * len(df.Unitprice),
               name="Comparing mean vs Unit price",
               visible=False,
               line=dict(color="#33CFA5", dash="dash")))

fig5.add_trace(
    go.Scatter(x=list(df.Branch),
               y=list(df.Total),
               name="Comparing Branch vs Total",
               line=dict(color="#F06A6A")))

fig5.add_trace(
    go.Scatter(x=list(df.Branch),
               y=[df.Total.mean()] * len(df.Branch),
               name="How different branches performed",
               visible=False,
               line=dict(color="#F06A6A", dash="dash")))

# Set title
fig5.update_layout(
    title_text="Pairwise explorative correlations",
)

# Create figure
fig3 = go.Figure()

fig3.add_trace(
    go.Scatter(x=list(df.Date), y=list(df.Total)))

# Set title
fig3.update_layout(
    title_text="Time series with range slider and selectors"
)

# Add range slider
fig3.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1,
                     label="Daily",
                     step="day",
                     stepmode="backward"),
                dict(count=6,
                     label="Monthly",
                     step="month",
                     stepmode="backward"),
                dict(count=1,
                     label="hourly",
                     step="hour",
                     stepmode="todate"),
                dict(count=1,
                     label="Yearly",
                     step="year",
                     stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)

# df5 = px.data.stocks()
fig6 = px.line(df, x=df.Date, y=df.Unitprice,
               hover_data={"Date": "|%B %d, %Y"},
               title='Date Vs Time pairwise correlation')
fig6.update_xaxes(
    dtick="M1",
    tickformat="%b\n%Y")

df2 = px.data.gapminder()
fig4 = px.scatter(df2, x="gdpPercap", y="lifeExp", animation_frame="year", animation_group="country",
                  size="pop", color="continent", hover_name="country",
                  log_x=True, size_max=55, range_x=[100, 100000], range_y=[25, 90])

df4 = px.data.gapminder()
fig21 = px.scatter(df4.query("year==2007"), x="gdpPercap", y="lifeExp", size="pop", color="continent",
                   hover_name="country", log_x=True, size_max=60)

df4 = px.data.gapminder()
fig20 = px.scatter(df4, x="gdpPercap", y="lifeExp", animation_frame="year", animation_group="country",
                   size="pop", color="continent", hover_name="country", facet_col="continent",
                   log_x=True, size_max=45, range_x=[100, 100000], range_y=[25, 90])

df5 = px.data.tips()
fig19 = px.histogram(df5, x="total_bill", y="tip", color="sex", marginal="rug", hover_data=df5.columns)
# print(df5)

df6 = px.data.carshare()
fig9 = px.scatter_mapbox(df6, lat="centroid_lat", lon="centroid_lon", color="peak_hour", size="car_hours",
                         color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10,
                         mapbox_style="carto-positron")

df5 = px.data.tips()
fig10 = px.bar(df5, x="sex", y="total_bill", color="smoker", barmode="group", facet_row="time", facet_col="day",
               category_orders={"day": ["Thur", "Fri", "Sat", "Sun"], "time": ["Lunch", "Dinner"]})

df5 = px.data.tips()
fig11 = px.histogram(df5, x="day", y="total_bill", color="sex",
                     title="Receipts by Payer Gender and Day of Week vs Target",
                     width=600, height=400,
                     labels={"sex": "Payer Gender", "day": "Day of Week", "total_bill": "Receipts"},
                     category_orders={"day": ["Thur", "Fri", "Sat", "Sun"], "sex": ["Male", "Female"]},
                     color_discrete_map={"Male": "RebeccaPurple", "Female": "MediumPurple"},
                     template="simple_white"
                     )

fig11.update_yaxes(  # the y-axis is in dollars
    tickprefix="$", showgrid=True
)

fig11.update_layout(  # customize font and legend orientation & position
    font_family="Rockwell",
    legend=dict(
        title=None, orientation="h", y=1, yanchor="bottom", x=0.5, xanchor="center"
    )
)

fig11.add_shape(  # add a horizontal "target" line
    type="line", line_color="salmon", line_width=3, opacity=1, line_dash="dot",
    x0=0, x1=1, xref="paper", y0=950, y1=950, yref="y"
)

fig11.add_annotation(  # add a text callout with arrow
    text="below target!", x="Fri", y=400, arrowhead=1, showarrow=True
)

fig12 = px.histogram(df, x=df.Branch, y=df.Total, histfunc='avg')

x1 = df.grossincome
x2 = df.Total
x3 = df.Rating

hist_data = [x1, x2, x3]

group_labels = ['Gross Income', 'Total', 'Rating']
colors = ['#835AF1', '#7FA6EE', '#B8F7D4']

# Create distplot with curve_type set to 'normal'
fig15 = ff.create_distplot(hist_data, group_labels, colors=colors, bin_size=.25,
                           show_curve=False)
# Add title
fig15.update_layout(title_text='Hist and Rug Plot for Gross income, Total sales and Rating')

fig30 = px.line_3d(data_frame=df, x='Unitprice', y='Total', color='Quantity', hover_name='Quantity',
                   hover_data=['Quantity', 'City', 'Gender', 'Productline', 'Tax'],
                   title='Pairwise Correlation relationship between UnitPrice And Total', animation_frame='Tax',
                   animation_group='Tax')

fig31 = px.line(data_frame=df, x='Unitprice', y='Total', color='Quantity',
                hover_name='Quantity', hover_data=['Quantity', 'City', 'Gender', 'Productline', 'Tax'],
                title='Pairwise Correlation relationship between UnitPrice And Total', animation_frame='Tax',
                animation_group='Tax')

fig32 = px.scatter(data_frame=df, x='Unitprice', y='Total', color='Quantity', symbol='Rating', size='Rating',
                   hover_name='Quantity', hover_data=['Quantity', 'City', 'Gender', 'Productline', 'Tax'],
                   trendline='ols',
                   title='Pairwise Correlation relationship between UnitPrice And Total', animation_frame='Tax',
                   animation_group='Tax')

fig33 = px.histogram(data_frame=df, x='Unitprice', y='Total', color='Quantity',
                     hover_name='Quantity', hover_data=['Quantity', 'City', 'Gender', 'Productline', 'Tax'],
                     title='Pairwise Correlation relationship between UnitPrice And Total', animation_frame='Tax',
                     animation_group='Tax')

fig34 = px.pie(data_frame=df, names='Tax', values='Total', color='Rating', title='Sector rep of Taxes',
               hover_name='Quantity', hover_data=['Quantity', 'City', 'Gender', 'Productline', 'Tax'],
               width=None, height=None, opacity=0.4, hole=0.2)

fig35 = px.timeline(data_frame=df, x_start='Unitprice', x_end='Rating', y='Total', color='Quantity',
                    hover_name='Quantity', hover_data=['Quantity', 'City', 'Gender', 'Productline', 'Tax'],
                    title='Pairwise Correlation relationship between UnitPrice And Total', animation_frame='Tax',
                    animation_group='Tax')

fig36 = px.scatter_3d(data_frame=df, x='Unitprice', y='Total', z='cogs', color='Quantity', symbol='Rating',
                      size='Rating', hover_name='Quantity', animation_frame='Tax', animation_group='Tax',
                      hover_data=['Quantity', 'City', 'Gender', 'Productline', 'Tax'],
                      title='Pairwise Correlation relationship between UnitPrice And Total')

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dbc.Button("Logout", color="primary", className="logout")
                ], width=3),
                dbc.Col([
                    html.Div(id='live-update-text',
                             style={'font-size': '18px', 'margin': '1px'}),
                    dcc.Interval(id='interval-component')
                ], style={'margin': '1px'})
            ], no_gutters=False),
            dbc.Row([
                dbc.Col([
                    html.P("logo")]),
                dbc.Col([
                    daq.BooleanSwitch(
                        id="boolean",
                        on=False,
                        color="#9B51E0",
                        label="Theme",
                        labelPosition="top",
                        style={'margin': '1px'}
                    )
                ], align="center", width=3)
            ], style={'margin': '3px'}),
            dbc.Row([
                dbc.Col([
                    dcc.Input(id="search", type="search", placeholder=" search statistics...",
                              style={'margin': '0px'})
                ]),
            ])
        ], width=3),
        dbc.Col([
            dbc.Row([
                dcc.Markdown('''
                ###### Upload your Excel or Csv dataset
                ''')
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                        style={
                            'width': '100%',
                            'height': '80px',
                            'lineHeight': '60px',
                            'borderWidth': '3px',
                            'borderStyle': 'dashed',
                            'borderRadius': '2px',
                            'textAlign': 'center',
                            'margin': '3px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=True
                    )
                ])
            ])
        ], width=9)
    ], style={'borderWidth': '1px'}, no_gutters=True),
    html.Div([
        dash_table.DataTable(
            id='dt1',
            columns=[
                {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
            ],
            data=df.to_dict('records'),
            editable=True,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            # tooltip={
            #     c: {'value': markdown_table, 'type': 'markdown'}
            #     for c in ['Rating', 'Total', 'cogs']
            # },
            column_selectable="single",
            row_selectable="multi",
            row_deletable=True,
            selected_columns=[],
            selected_rows=[],
            page_action="native",
            page_current=0,
            page_size=10,
            virtualization=True
        )
    ]),
    html.Hr(),
    html.Br(),
    html.Div(id='output-data-upload'),
    html.Hr(),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardImg(src="/assets/img/bei.jpg", top=True),
                dbc.CardBody(
                    [
                        html.H4("Monday", className="monday"),
                        html.P(
                            "Business statistics for Monday.",
                            className="card-text",
                        ),
                        dcc.Graph(figure=fig30)
                    ]
                )
            ]),
            html.Div(dbc.Button("Full Stats for Monday", href="", color="info"))
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardImg(src="/assets/img/box.jpg", top=True),
                dbc.CardBody(
                    [
                        html.H4("Tuesday", className="tuesday"),
                        html.P(
                            "Business statistics for Tuesday.",
                            className="card-text",
                        ),
                        dcc.Graph(figure=fig31)
                    ]
                )
            ]),
            html.Div(dbc.Button("More Stats", href="", color="primary"))
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardImg(src="/assets/img/bet.jpg", top=True),
                dbc.CardBody(
                    [
                        html.H4("Wednesday", className="wednesday"),
                        html.P(
                            "Business statistics for Wednesday.",
                            className="card-text",
                        ),
                        dcc.Graph(figure=fig32)
                    ]
                )
            ]),
            html.Div(dbc.Button("More Stats", href="", color="primary"))
        ], width=4)
    ], no_gutters=True),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardImg(src="/assets/img/bes.jpg", top=True),
                dbc.CardBody(
                    [
                        html.H4("Thursday", className="thursday"),
                        html.P(
                            "Business statistics for Thursday.",
                            className="card-text",
                        ),
                        dcc.Graph(figure=fig33)
                    ]
                )
            ]),
            html.Div(dbc.Button("More Stats", href="", color="primary"))
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardImg(src="/assets/img/beu.jpg", top=True),
                dbc.CardBody(
                    [
                        html.H4("Friday", className="friday"),
                        html.P(
                            "Business statistics for Friday.",
                            className="card-text",
                        ),
                        dcc.Graph(figure=fig34)
                    ]
                )
            ]),
            html.Div(dbc.Button("More Stats", href="", color="primary"))
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardImg(src="/assets/img/beo.jpg", top=True),
                dbc.CardBody(
                    [
                        html.H4("Saturday", className="saturday"),
                        html.P(
                            "Business statistics for Saturday.",
                            className="card-text",
                        ),
                        dcc.Graph(figure=fig35)
                    ]
                )
            ]),
            html.Div(dbc.Button("More Stats", href="", color="primary"))
        ], width=4)
    ], no_gutters=True),
    dbc.Row([
        dbc.Col([
            dbc.CardImg(src="/assets/img/beh.png", top=True),
            dbc.Card([
                dbc.CardBody(
                    [
                        html.H4("Sunday", className="sunday"),
                        html.P(
                            "Business statistics for Sunday.",
                            className="card-text",
                        ),
                        dcc.Graph(figure=fig36)
                    ]
                )
            ]),
            html.Div(dbc.Button("More Stats", href="", color="primary"))
        ], width=4),
        dbc.Col([
            html.Div(
                dcc.Graph(figure=fig15)
            )
        ], width=8)
    ], className='po', no_gutters=True),
    dbc.Row([
        html.Div([
            dcc.Tabs(id="tabs-styled-with-props", children=[
                dcc.Tab(label='Weekly Statistics', value='tab-1', ),
                dcc.Tab(label='Daily Statistics', value='tab-2', ),
                dcc.Tab(label='Monthly Statistics', value='tab-3', ),
                dcc.Tab(label='Yearly Statistics', value='tab-4', ),
            ], colors={
                "border": "blue",
                "primary": "blue",
                "background": "cornsilk"
            }),
            html.Div(id='tabs-content-props')
        ])
    ], className='iu'),
    dbc.Row([
        dbc.Col([
            html.Div(
                dcc.RangeSlider(
                    id='rng1',
                    min=1,
                    max=10,
                    value=[4, 8],
                    marks={
                        1: {'label': '1 Quantity', 'style': {'color': '#77b0b1'}},
                        3: {'label': '3 Quantity'},
                        7: {'label': '7 Quantity'},
                        10: {'label': '10 Quantity', 'style': {'color': '#f50'}}
                    },
                    # included=False
                )),
            html.Br(),
            html.Hr(),
            html.Div([
                dcc.RangeSlider(
                    id='rng2',
                    min=3.5,
                    max=9.9,
                    value=[4, 8],
                    marks={
                        3.5: {'label': '0 Rating', 'style': {'color': '#77b0b1'}},
                        6.: {'label': '6 Rating'},
                        8: {'label': '8 Rating'},
                        9.9: {'label': '9.9 Rating', 'style': {'color': '#f80'}}
                    }
                )
            ]),
            html.Br(),
            html.Hr(),
            html.Div(
                dcc.Checklist(
                    id='rng3',
                    options=[
                        {'label': 'Ewallet', 'value': 'Ewallet'},
                        {'label': 'Credit card', 'value': 'Credit card'},
                        {'label': 'Cash', 'value': 'Cash'}
                    ],
                    # value=['Cash', 'Ewallet'],
                    labelStyle={'display': 'inline-block'}
                )
            ),
            html.Br(),
            html.Hr(),
            html.Div([
                dcc.RadioItems(
                    id='rng4',
                    options=[
                        {'label': 'Female', 'value': 'Female'},
                        {'label': 'Male', 'value': 'Male'}
                    ],
                    # value='Male',
                    labelStyle={'display': 'inline-block'}
                )
            ])
        ], width=4),
        dbc.Col([
            html.Div([
                dcc.Graph(id='fig14')
            ])
        ], width=8)
    ], no_gutters=True),
    html.Div(id="dt1_output"),
    dbc.Row([
        dbc.Col(
            html.Div(
                dcc.Graph(figure=fig))
            , width=6),
        dbc.Col(
            html.Div(
                dcc.Graph(figure=fig1))
            , width=6)
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(
                dcc.Graph(figure=fig3)
            )
        ], width=6),
        dbc.Col([
            html.Div(
                dcc.Graph(figure=fig4)
            )
        ], width=6)
    ], no_gutters=True),
    dbc.Row([
        dbc.Col([
            html.Div(
                dcc.Graph(figure=fig5)
            )
        ], width=4),
        dbc.Col([
            html.Div(
                dcc.Graph(figure=fig6)
            )
        ], width=4),
        dbc.Col([
            html.Div(
                dcc.Graph(figure=fig7)
            )
        ], width=4)
    ], className='uy', no_gutters=True, ),
    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Graph(figure=fig12)
            ])
        ], width=6),
        dbc.Col([
            html.Div(
                dcc.Graph(figure=fig2)
            )
        ], width=6)
    ], className='qwe', no_gutters=True),
    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Graph()
            ])
        ], width=4),
        dbc.Col([
            html.Div([
                dcc.Graph(figure=fig11)
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='wordcloud', figure={}, config={'displayModeBar': False}),
                ])
            ]),
        ], width=4),
    ], className='mb-2', no_gutters=True),
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Button("Download Excel", id="btn_xlsx"),
                dcc.Download(id="download-dataframe-xlsx")
            ])
        ])
    ], no_gutters=True),
    html.Br(),
    html.Div([
        dcc.Tabs(id="tabs-style", children=[
            dcc.Tab(label='Breakfast Analytics', value='tab-1', ),
            dcc.Tab(label='Lunch Analytics', value='tab-2', ),
            dcc.Tab(label='Dinner Analytics', value='tab-3', )
        ], colors={
            "border": "blue",
            "primary": "blue",
            "background": "cornsilk"
        }),
        html.Div(id='tabs-content')
    ]),
    dbc.Row([
        dbc.Col([
            html.Label(html.B(html.Blockquote("Posssibility Dash Apps PREDICTIVE MODEL"))),
            html.Div([
                dbc.Col([
                    html.Legend("What is the Gender?"),
                    html.Hr(),
                    dcc.RadioItems(
                        id="rd1",
                        options=[
                            {'label': 'Male', 'value': 'Male'},
                            {'label': 'Female', 'value': 'Female'}
                        ],
                        value="Female",
                        labelClassName="Gender:",
                    ),
                    html.Legend("What type of Drinks do you Prefer?"),
                    html.Hr(),
                    dcc.RadioItems(
                        id="rd2",
                        value="Carbonated drinks",
                        options=[
                            {'label': 'Fresh Juice', 'value': 'Fresh Juice'},
                            {'label': 'Carbonated drinks', 'value': 'Carbonated drinks'}
                        ],
                        labelClassName="Drinks:"
                    ),
                    html.Legend("What is your Nationality?"),
                    html.Hr(),
                    dcc.Dropdown(
                        clearable=True,
                        id="rd3",
                        value="Mauritian",
                        options=[
                            {'label': 'Mauritian', 'value': 'Mauritian'},
                            {'label': 'Yemen', 'value': 'Yemen'},
                            {'label': 'China', 'value': 'China'},
                            {'label': 'Japan', 'value': 'Japan'},
                            {'label': 'Malaysia', 'value': 'Malaysia'},
                            {'label': 'Indonesian', 'value': 'Indonesian'},
                            {'label': 'Korean', 'value': 'Korean'},
                            {'label': 'Algerian', 'value': 'Algerian'},
                            {'label': 'Nigerian', 'value': 'Nigerian'},
                            {'label': 'Canadian', 'value': 'Canadian'},
                            {'label': 'Pakistani', 'value': 'Pakistani'},
                            {'label': 'Malaysia', 'value': 'Malaysia'},
                            {'label': 'Maldivian', 'value': 'Maldivian'},
                            {'label': 'Montreal', 'value': 'Montreal'},
                            {'label': 'Muslim', 'value': 'Muslim'},
                            {'label': 'Pakistan', 'value': 'Pakistan'},
                            {'label': 'MY', 'value': 'MY'},
                            {'label': 'Indian', 'value': 'Indian'},
                            {'label': 'Tanzanian', 'value': 'Tanzanian'}
                        ],
                        placeholder="Nationality",
                    ),
                    html.Legend("How old are you?"),
                    html.Hr(),
                    dcc.Dropdown(
                        clearable=True,
                        id="rd4",
                        value="68",
                        options=[
                            {'label': '50', 'value': '50'},
                            {'label': '22', 'value': '22'},
                            {'label': '54', 'value': '54'},
                            {'label': '25', 'value': '25'},
                            {'label': '27', 'value': '27'},
                            {'label': '68', 'value': '68'},
                            {'label': '30', 'value': '30'},
                            {'label': '32', 'value': '32'},
                            {'label': '63', 'value': '63'},
                            {'label': '34', 'value': '34'},
                            {'label': '75', 'value': '75'},
                            {'label': '36', 'value': '36'},
                            {'label': '37', 'value': '37'},
                            {'label': '42', 'value': '42'},
                            {'label': '45', 'value': '45'},
                            {'label': '49', 'value': '49'},
                            {'label': '57', 'value': '57'},
                            {'label': '54', 'value': '54'},
                            {'label': '52', 'value': '52'}
                        ],
                        placeholder="Age"
                    ),
                    html.Legend("Do you prefer a Desert?"),
                    html.Hr(),
                    dcc.RadioItems(
                        id="rd5",
                        value="Maybe",
                        options=[
                            {'label': 'Yes', 'value': 'Yes'},
                            {'label': 'No', 'value': 'No'},
                            {'label': 'Maybe', 'value': 'Maybe'}
                        ],
                        labelClassName="Dessert:",
                    )
                ])
            ]),
            html.Div(dbc.Button("Prediction", color="primary", block=True, id="btnP")),
            html.Hr(),
            html.Div(html.P(id="pred", contentEditable='True', draggable='True'))
        ], className="label", width=6),
        dbc.Col([
            html.Label(html.B(html.Blockquote("TIME SERIES ANALYSIS MODEL"))),
            html.Div([
                dcc.DatePickerSingle(
                    id='my-date-picker-single',
                    clearable=False,
                    is_RTL=True,
                    with_full_screen_portal=True,
                    calendar_orientation='vertical',
                    placeholder='Select a date',
                    with_portal=True,
                    month_format="MMMM, YYYY",
                    # display_format="M, D, YYYY",
                    min_date_allowed=date(1995, 8, 5),
                    max_date_allowed=date(2023, 12, 16),
                    initial_visible_month=date(2021, 8, 5),
                    date=date(2021, 8, 25)
                ),
                html.Div(id='output-container-date-picker-single')
            ])
        ], width=6)
    ], style={'textAlign': 'center', 'textColor': 'info'}),
    dbc.Row([
        dbc.Col([
            html.Footer(
                'Posssibility Dash Apps Enterprise @ copyright'
            )
        ], style={'textAlign': 'center', 'textColor': 'info'})
    ])
], fluid=True, id='container')


@app.callback(
    Output(component_id='fig14', component_property='figure'),
    [Input(component_id='rng1', component_property='value'),
     Input(component_id='rng2', component_property='value')])
def controls(rng1, rng2):
    dff = df
    # dff = dff[(dff['Quantity'].between(rng1[0], rng1[1])]
    # dff = dff[(dff['Rating'].between(rng2[0], rng2[1])]
    dff = dff[(dff['Quantity'] >= rng1[0]) & (dff['Quantity'] <= rng1[1])]
    dff = dff[(dff["Rating"] >= rng2[0]) & (dff["Rating"] <= rng2[1])]
    # # dff2 = dff1[dff1["Payment"] == rng3]
    # dff3 = dff2[dff2["Gender"] == rng4]
    # print(dff)
    x1 = dff.grossincome
    x2 = dff.Tax

    group_labels = ['gross income', 'Tax']

    rug_text_one = ['test1']

    rug_text_two = ['test2']

    rug_text = [rug_text_one, rug_text_two]  # for hover in rug plot
    colors = ['rgb(0, 0, 100)', 'rgb(0, 200, 200)']
    # Create distplot with custom bin_size

    fig = ff.create_distplot(
        [x1, x2], group_labels, bin_size=.25,
        rug_text=rug_text, colors=colors)

    fig.update_layout(title_text='Customized Distplots for Grossincome Vs Tax')

    return fig


@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_date(n):
    global dt
    return [html.P(dt)]


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@app.callback(
    Output("download-dataframe-xlsx", "data"),
    Input("btn_xlsx", "n_clicks"),
    prevent_initial_call=True)
def func(n_clicks):
    pass


@app.callback(Output('tabs-content-props', 'children'),
              Input('tabs-styled-with-props', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3('Tab content 1')
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Tab content 2')
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Tab content 3')
        ])
    elif tab == 'tab-4':
        return html.Div([
            html.H3('Tab content 4')
        ])


@app.callback(
    Output('dt1', 'style_data_conditional'),
    Input('dt1', 'selected_columns'))
def update_styles(selected_columns):
    return [{
        'if': {'column_id': i},
        'background_color': '#D2F3FF'
    } for i in selected_columns]


@app.callback(
    dash.dependencies.Output('container', 'style'),
    [dash.dependencies.Input('boolean', 'on')])
def update_output(on):
    if on:
        return {'backgroundColor': '#fff'}
    else:
        return {'backgroundColor': '#0000ff'}


@app.callback(
    Output(component_id='pred', component_property='children'),
    Input(component_id='btnP', component_property='n_clicks'),
    [State(component_id='rd1', component_property='value'),
     State(component_id='rd3', component_property='value'),
     State(component_id='rd5', component_property='value'),
     State(component_id='rd2', component_property='value'),
     State(component_id='rd4', component_property='value')],
    prevent_initial_call=True)
def update_years_of_experience_input(rd1, rd3, rd5, rd2, rd4, n):
    """
    model accepting inputs for prediction
    and n_clicks >= 1
    """
    if n is None:
        raise PreventUpdate
    else:
        if rd1 == 0 or None and rd3 == 0 or None and rd5 == 0 or None and rd2 == 0 or None \
                and rd4 == 0 or None:
            exit()
        else:
            try:
                dic = {"Gender": rd1, "Nationality": rd3, "Age": rd4, "Juice": rd2, "Dessert": rd5}
                test = pd.DataFrame(dic, index=[1000])
                # print(rd4)
                # print(dic)
                # dic = float(dic)
                # print(dic)
                pred = model.predict(test)
                for pre in pred:  # comparing predicted value to the value of the transformed labels
                    # if pre != 0:
                    if 4 <= pre <= 4.9:
                        pr = "Traditional Food"
                    elif 5 <= pre <= 5.9:
                        pr = "Western Food"
                    elif 0 <= pre <= 0.9:
                        pr = "African Food"
                    elif 3 <= pre <= 3.9:
                        pr = "European Food"
                    elif 2 <= pre <= 2.9:
                        pr = "Asian Food"
                    else:
                        pr = "Sea Food"
                    return "They will most likely order : {}".format(pr)
            except ValueError:
                return "Invalid Input!!"
        # print(pre)
        # print(pred)


@app.callback(
    Output('output-container-date-picker-single', 'children'),
    Input('my-date-picker-single', 'date'))
def update_output(date_value):
    string_prefix = 'You have selected: '
    if date_value is not None:
        date_object = date.fromisoformat(date_value)
        date_string = date_object.strftime('%B %d, %Y')
        return string_prefix + date_string


@app.callback(
    Output('dt1_output', "children"),
    Input('dt1', "derived_virtual_data"),
    Input('dt1', "derived_virtual_selected_rows"))
def update_graphs(rows, derived_virtual_selected_rows):
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = df if rows is None else pd.DataFrame(rows)

    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9'
              for i in range(len(dff))]

    return [
        dcc.Graph(
            id=column,
            figure={
                "data": [
                    {
                        "x": dff["Rating"],
                        "y": dff[column],
                        "type": "bar",
                        "marker": {"color": colors},
                    }
                ],
                "layout": {
                    "xaxis": {"automargin": True},
                    "yaxis": {
                        "automargin": True,
                        "title": {"text": column}
                    },
                    "height": 250,
                    "margin": {"t": 10, "l": 10, "r": 10},
                },
            },
        )
        # check if column exists - user may have deleted it
        # If `column.deletable=False`, then you don't
        # need to do this check.
        for column in ["Total", "cogs", "gross income"] if column in dff
    ]


if __name__ == '__main__':
    app.run_server(debug=False)
