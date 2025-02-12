import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Launch sites options for the dropdown menu
launch_sites = spacex_df['Launch Site'].unique()
Options = [
    {'label': 'All Sites', 'value': 'All'}  # Include the 'All' option
] + [
    {'label': site, 'value': site} for site in launch_sites
]

# Create the layout of the app
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown to select the launch site
    dcc.Dropdown(id='site-dropdown',
                 options=Options,
                 value='All',
                 placeholder='Select a Launch Site here',
                 searchable=True,
                 style={'width': '80%', 'padding': '3px', 'font-size': '20px', 'text-align': 'center'}),
    
    # Line break
    html.Br(),
    
    # Pie chart for launch success/failure
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    # Payload range slider
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(id='payload-slider',
                    min=min_payload, max=max_payload, step=1000,
                    marks={min_payload: f'{min_payload}', max_payload: f'{max_payload}'}, 
                    value=[min_payload, max_payload]),
    html.Br(),
    
    # Scatter plot for success vs payload mass
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# Callback to update the pie chart based on the selected launch site
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'All':
        fig = px.pie(spacex_df, values='class', 
                     names='Launch Site', 
                     title='Total Success Launches by Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(filtered_df, 
                     names='class',  # 'class' will represent success (1) vs failure (0)
                     title=f'Success vs Failure Launches from {entered_site}',
                     color='class',  # Color the chart by 'class' (success or failure)
                     color_discrete_map={0: 'red', 1: 'green'})  # Optional: Set colors (red for failure, green for success)
    return fig

# Callback to update the scatter plot based on site and payload range
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter(entered_site, payload_range):
    low, high = payload_range
    
    # Filter the dataframe based on payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) & 
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    
    # If a specific launch site is selected, filter further by site
    if entered_site != 'All':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    
    # Create the scatter plot with payload vs success (class) and color by booster version
    fig = px.scatter(
        filtered_df, 
        x='Payload Mass (kg)', 
        y='class', 
        color='Booster Version Category',  # Color by Booster Version
        title=f'Success vs. Payload Mass for {entered_site}' if entered_site != 'All' else 'Success vs. Payload Mass for All Sites'
    )
    
    # Return the figure to update the chart
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
