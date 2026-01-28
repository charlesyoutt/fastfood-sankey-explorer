"""
File: fastexplorer.py

Description:
This script creates an interactive web application using Panel and FastAPI to explore fast food
nutritional data. Users can filter menu items by restaurant and fat content, visualize relationships
using a Sankey diagram. They then can interact with dynamically generated tables and plots through a dashboard.
"""

import panel as pn
from fast_api import FASTAPI
import sankey2 as sk

pn.extension()

# initialize fastAPI
api = FASTAPI()
api.load_fast("data/fastfood.csv")

# search Widgets
restaurant = pn.widgets.Select(name="Restaurant", options=api.get_restaurants(), value='mcdonalds')
max_fat = pn.widgets.IntSlider(name="Max Fat", start=0, end=150, step=5, value=15)

# plot the widgets
width = pn.widgets.IntSlider(name="Width", start=250, end=2000, step=250, value=1000)
height = pn.widgets.IntSlider(name="Height", start=200, end=2500, step=100, value=1000)

# sankey diagram colors
color_options = {
    "Default (Black)": "black",
    "Vibrant Red": "red",
    "Cool Blue": "blue",
    "Nature Green": "green"
}
color_picker = pn.widgets.Select(name="Sankey Color", options=list(color_options.keys()), value="Default (Black)")

# callback functions
def get_catalog(restaurant, max_fat):
    """
    Creates a table showing food items from a specific restaurant and then
    filters by a maximum fat limit

    :param restaurant: The name of the restaurant to pull data from
    :param max_fat: The highest amount of fat in grams allowed for the food items
    :return: A table displaying the filtered food items
    """
    global local
    local = api.extract_local_network(restaurant, max_fat)
    local = local.reset_index(drop=True)
    table = pn.widgets.Tabulator(local, selectable=False, page_size=100)
    return table

def get_plot(restaurant, max_fat, width, height, color_picker):
    """
    Creates a Sankey diagram to visualize how different restaurants' menu items
    contribute to calorie distribution, based on fat content

    :param restaurant: The restaurant being analyzed
    :param max_fat: The max fat content in grams for food items included in the chart
    :param width: The width of the diagram
    :param height: The height of the diagram
    :param color_picker: The color choice for the Sankey lines
    :return: A Sankey diagram showing calorie flow from restaurant items
    """
    return sk.make_sankey(local, "restaurant", "calories_100", vals="total_fat_10", width=width,
                          height=height, line_color=color_options[color_picker])

# callback bindings
catalog = pn.bind(get_catalog, restaurant, max_fat)
plot = pn.bind(get_plot, restaurant, max_fat, width, height, color_picker)

card_width = 350

# make the search card
search_card = pn.Card(
    pn.Column(
        restaurant,
        max_fat,
    ),
    title="Search", width=card_width, collapsed=False
)

# make the plot card
plot_card = pn.Card(
    pn.Column(
        width,
        height,
        color_picker
    ),
    title="Plot", width=card_width, collapsed=True
)

# make layout
layout = pn.template.FastListTemplate(
    title="Food Explorer",
    sidebar=[
        search_card,
        plot_card,
    ],
    main=[
        pn.Tabs(
            ("Associations", catalog),
            ("Network", plot),
            active=1
        )
    ],
    header_background='#1e3a8a',
    theme='default'
).servable()

layout.show()