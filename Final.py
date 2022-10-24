# Import Required Libraries
import sys
import time
import json
import requests
import pandas as pd
from pandas import DataFrame
from bs4 import BeautifulSoup


# Set up DataFrame display format for better view
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 20)
pd.set_option('display.width', 5000)


# Create a class called scraping
class scraping:
    # Init class
    def __init__(self):
        # Set up static urls will be used in this project
        self.top_cities_url = "https://www.maigoo.com/goomai/173274.html"
        self.covid_cases_url = "https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5"
        self.weather_base_url = "https://way.jd.com/he/freeweather"
        self.weather_key = "75e6937a5e116e06c6b6c7cd1980dce0"

        # Create empty objects for later use
        self.covid_df = None
        self.weather_df = None
        self.city_df = None
        self.summary_df = None

    # Scrape top cities from website (html format)
    # This will use bs4 and pd to parse and organize to a DataFrame called city_df
    def top_cities(self):
        print("Getting Cities")
        content = requests.get(self.top_cities_url)
        soup = BeautifulSoup(content.content, 'html.parser')
        result = {'Area': []}
        tags = soup('h2')
        for tag in tags:
            result['Area'].append(tag.string.strip().split('\u5e02')[0])
        self.city_df = DataFrame(result)

    # Get all areas covid status, this will be use json to handle,
    # but because of the type of the api, this will always get all areas info (no matter the mode)
    def covid_cases(self):
        print("Getting Covid Cases")
        content = requests.get(self.covid_cases_url)
        content_json = content.json()
        dict_content = json.loads(content_json['data'])
        result = []
        for province in (dict_content['areaTree'][0]['children']):
            sub_result = [province['name'], province['today']['isUpdated'],
                          province['total']['nowConfirm'], province['total']['suspect']]
            # Some areas will not have Grade, this will catch and mark that area
            try:
                sub_result.append(province['total']['grade'])
            except KeyError:
                sub_result.append("Not_Available")
            result.append(sub_result)
            for city_area in province['children']:
                sub_result = [city_area['name'], city_area['today']['isUpdated'],
                              city_area['total']['nowConfirm'], city_area['total']['suspect']]
                # Some areas will not have Grade, this will catch and mark that area
                try:
                    sub_result.append(city_area['total']['grade'])
                except KeyError:
                    sub_result.append("Not_Available")
                result.append(sub_result)
        self.covid_df = DataFrame(result, columns=['Area', 'Updated_Today', 'Now_Confirmed', 'Suspect', 'Grade'])

    # Get specific areas weather, this will be use json to handle,
    # but because of the type of the api, this will always get specific areas info
    # Reason: This api limit the visit times and visit times in a short period,
    # so only specific areas weather will be collected.
    def weather(self):
        print("Getting Weathers")
        areas = self.city_df.to_dict(orient='list')['Area']
        result = []
        for area in areas:
            print("Getting: " + area)
            request_url = "{}?city={}&appkey={}".format(self.weather_base_url, area, self.weather_key)
            content = requests.get(request_url)
            content_dict = content.json()
            # This will catch error if unknown places entered
            try:
                sub_result = [area,
                              content_dict['result']['HeWeather5'][0]['daily_forecast'][0]['cond']['txt_d'],
                              content_dict['result']['HeWeather5'][0]['daily_forecast'][0]['cond']['txt_n'],
                              content_dict['result']['HeWeather5'][0]['daily_forecast'][0]['tmp']['max'],
                              content_dict['result']['HeWeather5'][0]['daily_forecast'][0]['tmp']['min'],
                              content_dict['result']['HeWeather5'][0]['daily_forecast'][0]['date']]
            except KeyError:
                sub_result = [area, "Not_Available", "Not_Available",
                              "Not_Available", "Not_Available", "Not_Available"]
            result.append(sub_result)
            # Sleep 1 sec to visit api gently
            time.sleep(1)
        self.weather_df = DataFrame(result, columns=['Area', 'Day_Weather', 'Night_Weather',
                                                     'Max_tmp', 'Min_tmp', 'Date'])

    # This will merge three tables together and return a summary_df
    # length will depends on how many cities got.
    def merge(self):
        self.summary_df = pd.merge(self.covid_df, self.city_df, on='Area')
        self.summary_df = pd.merge(self.summary_df, self.weather_df, on='Area')

    # This is a one time function, used to output csv files for static mode use
    # This may be modified to save db files later
    def out_csv(self):
        self.city_df.to_csv('data/city.csv', sep=',', index=False, header=True)
        self.covid_df.to_csv('data/covid.csv', sep=',', index=False, header=True)
        self.weather_df.to_csv('data/weather.csv', sep=',', index=False, header=True)
        self.summary_df.to_csv('data/summary.csv', sep=',', index=False, header=True)

    # This is the main function (both execution and print) for static mode
    def read_local(self):
        self.city_df = pd.read_csv('data/city.csv')
        self.covid_df = pd.read_csv('data/covid.csv')
        self.weather_df = pd.read_csv('data/weather.csv')
        self.summary_df = pd.read_csv('data/summary.csv')

    # This is the function for printing DataFrame for Full and Scrape mode
    def show(self):
        print("\n-----City Info-----")
        print(self.city_df)
        print("\n-----Covid Info-----")
        print(self.covid_df)
        print("\n-----Weather Info-----")
        print(self.weather_df)
        print("\n-----Info Summary-----")
        print(self.summary_df)

    # Limit the data got to 5 pieces
    def scrape(self):
        self.city_df = self.city_df.head(5)


# Main execution part
if __name__ == "__main__":
    # Full Mode
    if len(sys.argv) == 1:
        print("Start Running Full Mode")
        data = scraping()
        data.top_cities()
        data.covid_cases()
        data.weather()
        data.merge()
        data.show()
        print("Saving to 'data' folder")
        data.out_csv()
        print("Save Complete")

    # Static Mode
    elif sys.argv[1] == '--static':
        print("Start Running Static Mode")
        data = scraping()
        data.read_local()
        data.show()
