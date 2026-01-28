"""
File: fast_api.py

Description:
Provides an API to process and visualize fast food nutritional data.
It allows users to filter menu items based on restaurant selection and fat content
and then generates a Sankey diagram to visualize food item distributions
"""

import panel as pn
import pandas as pd
import sankey2 as sk


class FASTAPI:
    """
    An API to load, process, and filter fast food data
    """

    def load_fast(self, filename):
        """
        Loads fast food data from a CSV file

        :param filename: The name of the CSV file containing fast food data
        :return: None
        """
        self.fast = pd.read_csv(filename)

    def get_restaurants(self):
        """
        Gets a list of unique restaurants from the dataset

        :return: A list of restaurant names in lowercase.
        """
        fastfood = self.fast

        # convert all restaurant names to lowercase
        fastfood['restaurant'] = fastfood['restaurant'].str.lower()

        # get the unique restaurant names and return as a list
        fastfood_restaurants = fastfood['restaurant'].unique().tolist()
        return fastfood_restaurants

    def extract_local_network(self, restaurant, max_fat):
        """
        Filters fast food items based on the restaurant selection and fat content

        :param restaurant: The restaurant name
        :param max_fat: The maximum fat content allowed
        :return: A filtered DataFrame containing relevant fast food data
        """

        fast = pd.read_csv('data/fastfood.csv').copy()

        # round calories and fat content into bins
        fast['calories_100'] = fast['calories'] // 100 * 100
        fast['total_fat_10'] = fast['total_fat'] // 5 * 5

        # filter columns
        fast_filter = fast[['restaurant', 'calories_100', 'total_fat_10']].copy()
        fast_filter['restaurant'] = fast_filter['restaurant'].str.lower()

        # make sure max_fat is correctly interpreted
        max_fat_value = max_fat.value if isinstance(max_fat, pn.widgets.IntSlider) else max_fat

        # filter to include only items with total fat within the allowed limit
        fast_filter = fast_filter[fast_filter['total_fat_10'] <= max_fat_value]

        # aggregate the number of food items per restaurant and calorie range
        fast_filter = fast_filter.groupby(['restaurant', 'calories_100']).size().reset_index(name="num_foods")

        # sort the data to show most common food categories first
        fast_filter.sort_values('num_foods', ascending=False, inplace=True)

        # get the data specific to the selected restaurant
        fast_rest = fast_filter[fast_filter.restaurant == restaurant]

        # get only items that match the calorie bins of the selected restaurant and convert calories column to strings
        local = fast[fast.calories_100.isin(fast_rest.calories_100)].copy()
        local['calories_100'] = local['calories_100'].astype(str)

        return local


def main():

    # initialize the API
    fastapi = FASTAPI()
    fastapi.load_fast('data/fastfood.csv')

    # search parameters
    restaurant = 'mcdonalds'
    max_fat = 30

    # filter fast data to build the dataframe for sankey visualization
    local = fastapi.extract_local_network(restaurant, max_fat)

    # generate sankey diagram
    sk.show_sankey(local, 'restaurant', 'calories_100', vals='total_fat_10')

if __name__ == '__main__':
    main()