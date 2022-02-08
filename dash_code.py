import dash
import dash_html_components as html
import pandas as pd




def generate_table(dataframe):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(len(dataframe))
        ])
    ])


def visualize(csv):
    df = pd.read_csv(csv)
    app = dash.Dash(__name__)

    app.layout = html.Div([
    html.H4(children='US Agriculture Exports (2011)'),
    generate_table(df)
    ])

    app.run_server(debug=True, use_reloader=False)

