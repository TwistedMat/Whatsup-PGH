# -*- coding: utf-8 -*-
"""hood_event_scrape_module

Authors:
Allison Michalowski amichalo@andrew.cmu.edu
Eshan Mehotra emehotr@andrew.cmu.edu
Sowjanya Manipal smanipal@andrew.cmu.edu

Imports to:
    WhatsUp_main_gui.py
"""

# !pip install rtree
# !pip install geopandas
# !pip install beautifulsoup4
# !pip install censusgeocode

# Import libraries
import rtree
import geopandas as gp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
import zipfile
import io
from shapely.geometry import Point, Polygon
from bs4 import BeautifulSoup
import re
import unicodedata
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
from geopandas import GeoDataFrame
import censusgeocode as cg
import time

# %% Useful functions and constants

# clean_neighborhood_info function for making neighborhood names congruent among multiple data sets
def clean_neighborhood_info(x):
  """This function should be applied to a neighborhood name column via a lambda function to return edited column values
  Several neighborhoods in Pittsburgh have multiple column aliases. The function checks a column for these aliases and
  replaces them with the neighborhood name contained in the City of Pittsburgh's official data'"""
  if x == 'Arlington/Arlington Heights':
    return 'Arlington Heights'
  if x == 'Crafton':
    return 'Crafton Heights'
  if x == 'Downtown':
    return 'Central Business District'
  if x == 'East Allegheny - Deutschtown':
    return 'East Allegheny'
  if x == 'Hays or Hays Woods':
    return 'Hays'
  if x == 'Mt. Washington':
    return 'Mount Washington'
  if x == 'Sprint Hill':
    return 'Spring Hill - City View'
  if x == 'The Hill District':
    return 'Hill District'
  if x == 'The Strip District':
    return 'Strip District'
  if x == 'West End Village':
    return 'West End'
  else:
    return x

# fix_neighborhood_info ensures that scraped data that applies to multiple neighborhoods that are sometimes referred to
# under the alias of a single neighborhood are assigned to each of those neighborhoods
def fix_neighbor_info(my_df):
    """This function takes in a dataframe containing neighborhood aliases that refer to multiple Pittsburgh Neighborhoods
    and returns a dataframe with duplicated neighborhood info assigned to each specific neighborhood.
    i.e. df values for Oakland -> df values for North Oakland, South Oakland, and West Oakland"""
    multi_desc = pd.DataFrame()
    for i in range(len(my_df)):
      if my_df.loc[i]['Neighborhood'] == 'Lawrenceville':
        copy_1 = my_df.loc[i].copy()
        copy_1['Neighborhood'] = 'Upper Lawrenceville'
        multi_desc=multi_desc.append(copy_1)
        copy_2 = my_df.loc[i].copy()
        copy_2['Neighborhood'] = 'Lower Lawrenceville'
        multi_desc=multi_desc.append(copy_2)
      if my_df.loc[i]['Neighborhood'] == 'Oakland':
        copy_1 = my_df.loc[i].copy()
        copy_1['Neighborhood'] = 'West Oakland'
        multi_desc=multi_desc.append(copy_1)
        copy_2 = my_df.loc[i].copy()
        copy_2['Neighborhood'] = 'North Oakland'
        multi_desc=multi_desc.append(copy_2)
        copy_3 = my_df.loc[i].copy()
        copy_3['Neighborhood'] = 'South Oakland'
        multi_desc=multi_desc.append(copy_3)
      if my_df.loc[i]['Neighborhood'] == 'Squirrel Hill':
        copy_1 = my_df.loc[i].copy()
        copy_1['Neighborhood'] = 'Squirrel Hill North'
        multi_desc=multi_desc.append(copy_1)
        copy_2 = my_df.loc[i].copy()
        copy_2['Neighborhood'] = 'Squirrel Hill South'
        multi_desc=multi_desc.append(copy_2)
      if my_df.loc[i]['Neighborhood'] == 'South Side':
        copy_1 = my_df.loc[i].copy()
        copy_1['Neighborhood'] = 'South Side Slopes'
        copy_2 = my_df.loc[i].copy()
        copy_2['Neighborhood'] = 'South Side Flats'
      if my_df.loc[i]['Neighborhood'] == 'The South Side':
        copy_3 = my_df.loc[i].copy()
        copy_1['description'] = copy_3['description']
        multi_desc=multi_desc.append(copy_1)
        copy_4 = my_df.loc[i].copy()
        copy_2['description'] = copy_4['description']
        multi_desc=multi_desc.append(copy_2)
    return multi_desc

# flatten function works with data produced by fix_neighbor_info function to compact multiple rows with the same 
# neighborhood into one by empty columns with values from other rows of the same neighborhood
def flatten(g):
    return g.fillna(method='bfill').iloc[0]

# get_address_nm geocodes data with nominatim geocoder
def get_address_nm(my_address):
    """This function should be applied to the address column of a dataframe to geocode the addresses, and
    the function returns either a np.nan value for addresses that could not be geocoded or a POINT object 
    corresponding with the EPSG:4326 projection"""
    try:
      #time.sleep(1)
      locator = Nominatim(user_agent="myGeocoder", timeout=10)
      geocode = RateLimiter(locator.geocode, min_delay_seconds=1)
      my_loc = geocode(my_address).point
      my_loc_list = []
      lat = my_loc[0]
      long=my_loc[1]
      my_point = Point(long, lat)
      return my_point
    except:
      return np.nan

# Set header constant for use in scraping from Beautiful Pittsburgh because the website is sensitive to scraping without
# a user agend and to multiple calls
header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10136',
          "Accept-Encoding": "*",
          "Connection": "keep-alive"}

# %% Scrape GeoData

#### Downloading and processing inital pgh neighborhoods shapefile 
# Download and get shapefile for pgh neighborhoods
url = 'https://pghgishub-pittsburghpa.opendata.arcgis.com/datasets/dbd133a206cc4a3aa915cb28baa60fd4_0.zip?outSR=%7B%22latestWkid%22%3A2272%2C%22wkid%22%3A102729%7D'
local_path = 'tmp/'
r = requests.get(url)
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall(path=local_path)
z.extractall(path=local_path)
filenames = [y for y in sorted(z.namelist()) for ending in ['dbf', 'prj', 'shp', 'shx'] if y.endswith(ending)] 
# Read in with geopandas
thehoods=gp.read_file(local_path+'Neighborhoods_.shp')
# Make geodataframe keeping only potentially useful info from neighborhoods data
thehoods_clean=thehoods[['objectid', 'geoid10', 'sqmiles', 'hood', 'hood_no', 'unique_id', 'geometry']].copy()

#### Downloading and processing csv of public art recorded by the city
# Get data on public art in pittsburgh neighborhoods from western PA regional data center via download
art_url = 'https://data.wprdc.org/datastore/dump/00d74e83-8a23-486e-841b-286e1332a151'
# Read data into normal dataframe
public_art = pd.read_csv(art_url)
# Clean and extract useful information
public_art_clean = public_art[['id', 'title', 'neighborhood', 'latitude', 'longitude']].copy().dropna().reset_index(drop=True)
# public_art_clean dataframe
public_art_clean.head(10)
# Count by number of city recorded public art works in each neighborhood
public_art_counting = public_art_clean.copy()
public_art_counting["art_count"] = 1
public_art_count = public_art_counting.groupby("neighborhood")[["art_count"]].sum().reset_index()
# Note that only 55 neighborhoods have art

#### Downloading and processing csv of playgrounds in the city
playgrounds_url = 'https://data.wprdc.org/datastore/dump/47350364-44a8-4d15-b6e0-5f79ddff9367'
# Read data into normal dataframe
playgrounds = pd.read_csv(playgrounds_url)
# Clean and extract useful information
playgrounds_clean = playgrounds[['id', 'name', 'neighborhood', 'latitude', 'longitude']].copy().dropna().reset_index(drop=True)
# playgrounds_clean dataframe
playgrounds_clean.head(10)
# Count by number of city recorded playgrounds in each neighborhood
playgrounds_counting = playgrounds_clean.copy()
playgrounds_counting["playground_count"] = 1
playgrounds_count = playgrounds_counting.groupby("neighborhood")[["playground_count"]].sum().reset_index()
# Note that there are only 68 neighborhoods with playgrounds

# %% Scrape Walkscore Information"""

### Scrape table of walkscore, bikescore, transitscore, population for pgh neighborhoods from walkscore.com
# Get html for each line of table
walkscore_data = pd.DataFrame()
walkscore_url = 'https://www.walkscore.com/PA/Pittsburgh'
walkscore_page = requests.get(walkscore_url)
walkscore_content = BeautifulSoup(walkscore_page.content, "html.parser")
walk_results = walkscore_content.find(id="hoods-list-table")
walk_elements = walk_results.find_all(class_="hoods-list-item")
# For each line of table, append neighborhood, walkscore, bikescore, transitscore, population, and append each list to [[]]
walkscore_list = []
for place in walk_elements:
  hood = []
  neighborhood = place.find("td", class_="name")
  walkscore = place.find("td", class_="walkscore")
  transitscore = place.find("td", class_="transitscore")
  bikescore = place.find("td", class_="bikescore")
  population = place.find("td", class_="population")
  hood.extend([neighborhood.text.strip(), walkscore.text.strip(), transitscore.text.strip(), bikescore.text.strip(), population.text.strip()])
  walkscore_list.append(hood)
# Make walkscore_list into dataframe
walkscore_data = pd.DataFrame(walkscore_list, columns = ["Neighborhood", "walkscore", "transitscore", "bikescore", "population"])

# Correct differences in alternative neighborhood names to match formatting of thehoods_clean dataset
# Website had specific alternative aliases that differed from the other scraping websites including misspellings,
# so clean_neighborhood_info was not used as these aliases didn't generalize and in some cases such as two instances of
# South Side, the correct label needed to be determined from the website UI and then applied using a loc since they 
# had the same scraped neighborhood name
walkscore_data.loc[55, 'Neighborhood'] ='Spring Hill-City View'
walkscore_data.loc[13, 'Neighborhood'] ='Crawford-Roberts'
walkscore_data.loc[6, 'Neighborhood'] ='South Side Flats'
walkscore_data.loc[28, 'Neighborhood'] ='South Side Slopes'
walkscore_data.loc[49, 'Neighborhood'] ='Beechview'
walkscore_data.loc[59, 'Neighborhood'] ='Elliott'
walkscore_data.loc[65, 'Neighborhood'] ='Ridgemont'
walkscore_data.loc[0, 'Neighborhood'] ='Central Business District'

# %% Scraping Neighborhood Description Data Next Pittsburgh

### Scrape text about neighborhoods to inform wordcloud and provide insight into neighborhood characteristics
# Begin with url to page containing links to other pages for each neighborhood
nextpgh_url = 'https://nextpittsburgh.com/pittsburgh-neighborhoods-map-and-guides/'
nextpgh_page = requests.get(nextpgh_url)
nextpgh_content = BeautifulSoup(nextpgh_page.content, 'lxml')
nextpgh_cols = nextpgh_content.find_all('div', class_='threecol')
# Lists to store links to additional pages
each_new_page = []
each_link = []
# Lists to store scraped data about neighborhoods
nextpgh_names = []
hood_paras = []
hood_desc = []
hood_desc_cloud = []
for div in nextpgh_cols:
  each_new_page.extend(div.find_all('a'))
  a_link = div.find_all('a')
  # Get link to pages for each neighborhood
  for link in a_link:
    each_link.append(str((link['href'])))
  pat = r'(>.*</a>$)'
  # Get name of neighborhood associated with link and use try except to assign nans to links that don't fit pattern (means they are link to something else)
  for link in a_link:
    neighborhood_group = re.search(pat, str(link))
    try:
      name = neighborhood_group.group(0).replace('>','').replace('</a','')
      if name!='':
        nextpgh_names.append(name)
      else:
        nextpgh_names.append(np.nan)
    except:
      nextpgh_names.append(np.nan)
for link in each_link:
    # scrape info on neighborhoods from each link where opened page contains desired info, else return nan due to missing info
    try:
      url=link
      hood_page=requests.get(url)
      hood_content=BeautifulSoup(hood_page.text, 'lxml')
      # Get text from paragraphs in the main body
      my_text = (hood_content.find(class_='entry-content clearfix'))
      my_paras = []
      # Add paragraphs of text to list
      my_paras.extend(my_text.find_all('p'))
      my_hood_paras = [str(para.get_text()) for para in my_paras]
      # my_hood_paras = [unicodedata.normalize("NFKD", para) for para in my_hood_paras]
      hood_paras.append(my_hood_paras)
      # Join paragraphs to one long string 
      desc=' '.join(my_hood_paras)
      hood_desc.append(desc)
    except:
      hood_paras.append(np.nan)
      hood_desc.append(np.nan)
nextpgh_dict = {}
nextpgh_dict = {'Neighborhood':nextpgh_names, 'link':each_link, 'paragraphs':hood_paras, 'description':hood_desc}
# Dataframe of info from Next Pittsburgh - neigborhood name, description, etc
nextpgh_hoods = pd.DataFrame(nextpgh_dict).dropna().reset_index(drop=True)
nextpgh_hoods

# %% Scraping Pittsburgh Beautiful website for more text description of neighborhoods

### Scrape text about neighborhoods to inform wordcloud and provide insight into neighborhood characteristics
# Warning try except statements used because website occasionally blocks scrapers entirely when it has been scraped too frequently
pghbeauty_url = 'https://www.pittsburghbeautiful.com/pittsburgh-neighborhoods/'
   
# Lists to store links to additional pages
beauty_each_new_page = []
beauty_each_link = []
# Lists to store scraped data about neighborhoods
pgh_beauty_names = []
beauty_hood_paras = []
beauty_hood_desc = []

try:
    pghbeauty_page = requests.get(pghbeauty_url, headers=header)
    pghbeauty_content = BeautifulSoup(pghbeauty_page.content, 'html.parser')

    mbp = pghbeauty_content.find('div', class_='et_pb_row et_pb_row_1').find_all('div', class_='et_pb_text_inner')
    # Skip irrelevant headers listed in matches
    matches = ['>North<', '>South<', '>East<', '>West<']
    for page in mbp:
      if not any(x in str(page) for x in matches):
        beauty_each_new_page.append(page)
    beauty_a_link = [x.find('a') for x in beauty_each_new_page]
    # Get links for pages to each neighborhood
    for link in beauty_a_link:
      beauty_each_link.append(str(link['href']))
      pat = r'(>.*</a>$)'
      neighborhood_group = re.search(pat, str(link))
        # Get name of neighborhood associated with link and use try except to assign nans to links that don't fit pattern (means they are link to something else)
      try:
        name = neighborhood_group.group(0).replace('>','').replace('</a','')
        if name!='':
          pgh_beauty_names.append(name)
        else:
          pgh_beauty_names.append(np.nan)
      except:
        pgh_beauty_names.append(np.nan)
    for link in beauty_each_link:
      try:
        url=link
        hood_page=requests.get(url, headers=header)
        hood_content=BeautifulSoup(hood_page.text, 'lxml')
        my_text = (hood_content.find(class_='entry-content'))
        my_paras = []
        # Find all paragraphs on page and append to list
        my_paras.extend(my_text.find_all('p'))
        my_hood_paras = [str(para.get_text()) for para in my_paras]
        beauty_hood_paras.append(my_hood_paras)
        # Join all paragraphs into a single string
        desc=' '.join(my_hood_paras)
        desc_clean = desc.replace(r'(adsbygoogle = window.adsbygoogle || []).push({});','').lower()
        beauty_hood_desc.append(desc_clean)
      except:
        beauty_hood_paras.append(np.nan)
        beauty_hood_desc.append(np.nan)
except:
    pass
pghbeauty_dict = {}
pghbeauty_dict = {'Neighborhood':pgh_beauty_names, 'link':beauty_each_link, 'paragraphs':beauty_hood_paras, 'description_b':beauty_hood_desc}
pghbeauty_hoods = pd.DataFrame(pghbeauty_dict).dropna().reset_index(drop=True)

# %% Combine Neighborhood Detail Scrapes

### Align text data from Next Pittsburgh with data from Pittsburgh Beautiful if able to scrape Pittsburgh Beautiful
# Prepare next pittsburgh data for merge and make sure neighborhood names match official Pittsburgh formats
nextpgh_hoods_merge = nextpgh_hoods[['Neighborhood', 'description']].copy()
nextpgh_hoods_merge['Neighborhood'] = nextpgh_hoods_merge['Neighborhood'].apply(clean_neighborhood_info)
# Prepare walkscore for merging
walk_merge = walkscore_data.copy()

# Processing if able to scrape Pittsburgh beautiful or not
#if pghbeauty_hoods.loc[0, 'Neighborhood'] == 'Allegheny Center':
if pghbeauty_hoods.empty == False:   
    pghbeauty_hoods_merge = pghbeauty_hoods[['Neighborhood', 'description_b']].copy()
    # Ensure neighborhood names match official Pittsburgh format
    pghbeauty_hoods_merge['Neighborhood'] = pghbeauty_hoods_merge['Neighborhood'].apply(clean_neighborhood_info)
    # merge next pgh and Pittsburgh beautiful
    text_neighborhoods = pghbeauty_hoods_merge.merge(nextpgh_hoods_merge, left_on='Neighborhood', right_on='Neighborhood', how='outer')
    text_neighborhoods = text_neighborhoods.merge(walk_merge, left_on='Neighborhood', right_on='Neighborhood', how='outer')
    # Account for descriptions that apply to multiple neighborhoods
    multi_hood_df = fix_neighbor_info(text_neighborhoods)
    text_neighborhoods = text_neighborhoods.append(multi_hood_df)
    # Make sure there is only one row per neighborhood
    my_hood_test = thehoods_clean[['hood']].copy()
    text_neighborhoods_free = my_hood_test.merge(text_neighborhoods, left_on='hood', right_on='Neighborhood', how='left')
    text_neighborhoods_free = text_neighborhoods_free.groupby('hood').apply(flatten).reset_index(drop=True)
    text_neighborhoods_free['desc_all'] = text_neighborhoods_free.copy().description.str.cat(text_neighborhoods_free['description_b'], sep=' ', na_rep='')
else:
    text_neighborhoods = nextpgh_hoods_merge.merge(walk_merge, left_on='Neighborhood', right_on='Neighborhood', how='outer')
    # Account for descriptions that apply to multiple neighborhoods
    multi_hood_df = fix_neighbor_info(text_neighborhoods)
    text_neighborhoods = text_neighborhoods.append(multi_hood_df)
    # Make sure there is only one row per neighborhood
    my_hood_test = thehoods_clean[['hood']].copy()
    text_neighborhoods_free = my_hood_test.merge(text_neighborhoods, left_on='hood', right_on='Neighborhood', how='left')
    text_neighborhoods_free = text_neighborhoods_free.groupby('hood').apply(flatten).reset_index(drop=True)
    text_neighborhoods_free['desc_all'] = text_neighborhoods_free['description']

# %% Merge neighborhood descriptors onto main neighborhood shapefile

### Create dataframe of neighborhoods with details for each neighborhood
# Merge data about each neighborhood onto geodataframe including neighborhood details
pgh_neighbor_merge = thehoods_clean.copy()

# Merge on public_art_count
pgh_neighbor_merge = pgh_neighbor_merge.merge(public_art_count, left_on='hood', right_on='neighborhood', how='left')
pgh_neighbor_merge["art_count"].fillna(0, inplace=True)
pgh_neighbor_merge = pgh_neighbor_merge.drop('neighborhood', axis=1)

# Merge on playground_count
pgh_neighbor_merge = pgh_neighbor_merge.merge(playgrounds_count, left_on='hood', right_on='neighborhood', how='left')
pgh_neighbor_merge["playground_count"].fillna(0, inplace=True)
pgh_neighbor_merge = pgh_neighbor_merge.drop('neighborhood', axis=1)

pgh_neighbor_merge = pgh_neighbor_merge = pgh_neighbor_merge.merge(text_neighborhoods_free, left_on='hood', right_on='hood', how='left')
pgh_neighbor_merge = pgh_neighbor_merge.drop(['Neighborhood'], axis=1)



# %% Scraping Visit Pittsburgh

# Make list of urls to scrape from VisitPittsburgh
URLs = []
for i in range(1,15):
    URLs.append(("https://www.visitpittsburgh.com/directories/events/?page=") + str(i))

# Set empty dataframe to add scraped events to
df_visit_events = pd.DataFrame()
j = 0

# Scrape for existing webpages (try statement account for less than 15 pages or rejection from server due to frequent scraping)
try:

  # Scrape visit pittsburgh base page for event name, date, and link + get list of links to access pages for each event for more info
    for url in URLs:
        j = j + 1
        URL = url
        page = requests.get(URL)
    
        soup = BeautifulSoup(page.content, "html.parser")
    
        event_names = []
        event_dates = []
        event_links = []
        event_descriptions = []
        event_time = []
        event_locations = []
        event_category = []
        
        #pat = r'[^A-Za-z0-9- ,.]+'
    
        results = soup.find(id="dir-results")
    
        elements = results.find_all("div", class_="card__body text-center")
    
        for el in elements:
            try:
                event_names.append(el.find('h4').text)
            except: 
                event_names.append("")
    
            try:
                event_dates.append((el.find_all("span")[2].text) + " " + (el.find_all("span")[1].text) + ", " + (el.find_all("span")[0].text))
            except: 
                event_dates.append("")
    
            try:
                event_links.append("https://www.visitpittsburgh.com" + el.find('a')['href'])
    
            except: 
                event_links.append("")
      
        
        # Scrape each specific event page for address, time, and description
        for link in event_links:
            links_URL = link
            links_page = requests.get(links_URL)
    
            links_soup = BeautifulSoup(links_page.content, "html.parser")
            
            links_results = links_soup.find(id="main")
    
            contacts_elements = links_results.find_all("ul", class_="list list--contact")
    
            for el in contacts_elements:
                        
                #location
                if (el.find("meta", {'itemprop': "streetAddress"})) is not None:
                    streetAddress = (el.find("meta", {'itemprop': "streetAddress"}).get("content"))
                else:
                    streetAddress = ""
    
                if (el.find("meta", {'itemprop': "addressLocality"})) is not None:
                    addressLocality = (el.find("meta", {'itemprop': "addressLocality"}).get("content"))
                else:
                    addressLocality = ""
    
                if (el.find("meta", {'itemprop': "postalCode"})) is not None:
                    postalCode = (el.find("meta", {'itemprop': "postalCode"}).get("content"))
                else:
                    postalCode = ""
    
                #time
                li_tags =[]
                for li_elements in el.find_all("li"):
                    li_tags.append(li_elements)
    
                try:
                    for li in li_tags:
                      if 'Time:' in li.text:
                        time_str = li.text
                        my_time = time_str[:time_str.index('\n')]
                      else:
                        my_time=''
                except:
                    my_time=''
    
            
            #description
            contacts_desc = links_results.find_all("div", class_="blk blk--no-padding from-wysiwyg")
    
            for el in contacts_desc:
                if (el.find("p")) is None:
                    event_description = ""
                else: 
                    event_description = el.find("p").text
    
            #Final lists
            if streetAddress != '':
                # Some addresses stored zip in addressLocality by mistake on the website, so tested for and fixed here
                # In this way, we provide users with more accurate representation of the addresses for these events
                if len(addressLocality)==5:
                  event_locations.append(streetAddress + ", Pittsburgh, PA " + addressLocality)
                else:
                  event_locations.append(streetAddress + ", Pittsburgh, PA " + postalCode)
            else:
                event_locations.append(np.nan)
            
            event_descriptions.append(event_description)
            
            if my_time:
              event_time.append(my_time)
            else:
              event_time.append('')
            
            # empty column for compatibility with downtown pittsburgh events, which have categories
            event_category.append('')
    
        dict_data = {'Name': event_names,
              'Date': event_dates,
              'Time': event_time,
              'Address': event_locations,
              'Category': event_category,
              'Link': event_links,
              'Description': event_descriptions}
    
        df_visit_events = df_visit_events.append(pd.DataFrame(dict_data)).reset_index(drop=True)
except:
    pass

# Drop nans for those events without addresses
df_visit_events = df_visit_events.dropna().reset_index(drop=True)

# %% Scrape events from Downtown Pittsburgh Partnership

# Get events from Downtown Pittsburgh Partnership

# Access base page to get links to each event
downtown_events_dict_list = []
events_url = 'https://downtownpittsburgh.com/events/'
events_page = requests.get(events_url)

# Find html for each unique event and assign to list event_results
events_content = BeautifulSoup(events_page.content, "html.parser")
events_results = events_content.find_all(class_="eventitem")

# For each result, produce a list of clean the event name, datetime, address, category, link, and description if available
for result in events_results:
    # Results need to be obtained by going to webpage of specific event which equals 'https://downtownpittsburgh.com/events/event/?id=' + last 5 chars of 'id' in each item
    url_end = result.get('id')[-5:]
    specific_event_url= 'https://downtownpittsburgh.com/events/event/?id=' + str(url_end)
    # Go to event page for this event and scrape data with html.parser
    specific_event = requests.get(specific_event_url)
    spec_event_content = BeautifulSoup(specific_event.content, 'html.parser')
    # Data on each event are in class_ = 'copyContent expanded', assign to spec_event results
    spec_event_results = spec_event_content.find_all('h1', class_="copyContent expanded")

    # Not all info is available for each event!!!
    # Use try except statements to look for name, datetime, address, category, link, description
        # In try statement, look for info and if found, clean and assign to variable of interest
        # In except statement, if info couldn't be found, assign empty np.nan for name, date, address, assign '' for time, cat, link, desc

    # Find name 
    try:
      names = []
      for n in spec_event_content.find_all('h1'):
        names.append(n.get_text())
      name = names[2]
    except:
      name = np.nan

    # find date
    try:
      dateinfo = str(spec_event_content.find("div", class_="eventdate")).replace('\t', '').replace('\n', '').replace(r'<div class="eventdate">','').replace('</div>','')
      date = re.search(r'^.*\|', dateinfo).group(0)[:-1].strip()
    except:
      date = np.nan

    # Find time
    try:
      timeinfo = str(spec_event_content.find("div", class_="eventdate")).replace('\t', '').replace('\n', '').replace(r'<div class="eventdate">','').replace('</div>','')
      my_time = re.search(r'\|.*$', timeinfo).group(0)[1:].strip()
    except:
      my_time = '' 

    # Find address
    try:
      address = str(spec_event_content.find("div", class_="eventlocation")).replace('<div class="eventlocation">','').replace('<strong>','').replace('</strong>','').replace('\n','').replace('\t','').replace('<br/>',', ').replace('</div>','')
    except:
      address = np.nan

    # Find category
    try:
      category = str(spec_event_content.find("div", class_="category")).replace('<div class="category">','').replace('<div class="term">','').replace('</div>', '').replace('\n','').replace('&amp','and').replace('+','and')
    except:
      category = ''

    # Find link 
    try:
      link = str(spec_event_content.find('div', class_='eventlink').find('a').get('href'))#['href'])
    except:
      link = ''

    # Find description
    try:
      desc_paras = []
      for para in spec_event_content.find_all('p'):
        # skip any paragraphs that are part of the basic page rather than specific to event
        if ("Contact Us" not in para.get_text()) and ("Pittsburgh Downtown Partnership" not in para.get_text()):
          desc_paras.append(str(para.get_text()))
      # clean description paragraphs to get rid of markup
      #desc_paras=[unicodedata.normalize("NFKD", para) for para in desc_paras]
      desc=''
      for i in range(len(desc_paras)):
        if i < (len(desc_paras)-1):
          desc=desc+desc_paras[i]+'\n'
        else:
          desc=desc+desc_paras[i]
    except:
      desc = ''
    # Add found variables to a dict with future column names as keys and vars as values
    specific_event_data_dict = {'Name':name, 'Date':date, 'Time':my_time, 'Address':address, 'Category':category, 'Link':link, 'Description':desc }
    # Make list of each dict
    downtown_events_dict_list.append(specific_event_data_dict)
# Make dataframe of all the downtown pittsburgh events from the downtown_events_dict_list
downtown_events_dataframe = pd.DataFrame(downtown_events_dict_list)

# Clean the Date column for downtown_events_dataframe
downtown_events_dataframe['Date'] = downtown_events_dataframe['Date'].apply(lambda x: str(x)[:str(x).index('-')] if '-' in str(x) else np.nan)
# First clean address column in dt dataframe
downtown_events_dataframe['Address'] = downtown_events_dataframe['Address'].apply(lambda x: re.search('([0-9].*)', str(x)).group(0) if re.search('([0-9].*)', str(x))!= None else np.nan)

# %% Combine events data from VisitPittsburgh events and Downtown Pittsburgh Partnership events

# Combine events data by appending one dataframe to the other since they have the same columns
all_events_df = downtown_events_dataframe.copy().append(df_visit_events).reset_index(drop=True)
# Convert date column to date_times to allow sorting by date
all_events_df['Date'] = all_events_df['Date'].apply(pd.to_datetime)
all_events_df = all_events_df[pd.notnull(all_events_df['Date'])]
all_events_df = all_events_df.sort_values(by='Date').reset_index(drop=True)
# Eliminate events with addresses for which only the location name and zipcode were provided (only zipcode would have been extracted in cleaning)
all_events_df = all_events_df[all_events_df['Address'].apply(lambda x: True if len(str(x))>5 else False)]
# Eliminate archived events that the website is still maintaining from prior to october 2021
all_events_df = all_events_df[all_events_df['Date'].apply(lambda x: True if x> pd.to_datetime('2021-10-01') else False)].reset_index(drop=True)


# %% Geocode all events

# Make a copy of the all_events_df to protect data
all_events_dfc = all_events_df.copy()

# Extract addresses
all_addresses = all_events_dfc[['Address']].copy()
# Drop duplicates
all_addresses = all_addresses.drop_duplicates()

# Geocode each address
all_addresses['geometry'] = all_addresses['Address'].apply(get_address_nm)
# Merge back onto original dataframe
all_events_dfc = all_events_dfc.merge(all_addresses, left_on='Address', right_on='Address', how='inner')

# # Remove any events that do not have geocode
all_events_dfc = all_events_dfc[pd.notnull(all_events_dfc['geometry'])]
all_events_gp = GeoDataFrame(all_events_dfc, crs='EPSG:4326', geometry=all_events_dfc.geometry)
# Reproject to appropriate local projection
all_events_gp = all_events_gp.to_crs('EPSG:2272')

# %% Test if events fall in the bounds of pittsburgh

# Get bounds of city of pittsburgh to drop any points not within city boundaries
url = 'https://pghgishub-pittsburghpa.opendata.arcgis.com/datasets/a99f25fffb7b41c8a4adf9ea676a3a0b_0.zip?outSR=%7B%22latestWkid%22%3A2272%2C%22wkid%22%3A102729%7D'
local_path = 'tmp/'
r = requests.get(url)
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall(path=local_path)
z.extractall(path=local_path)
filenames = [y for y in sorted(z.namelist()) for ending in ['dbf', 'prj', 'shp', 'shx'] if y.endswith(ending)] 
print(filenames)

# Make geodataframe of pittsburgh boundaries
pgh_bounds=gp.read_file(local_path+'City_Boundary.shp')

# Project to same projection
pgh_bounds = pgh_bounds.to_crs('EPSG:2272')

def check_in_pgh(points_gdf):
  """Checks if each point in a geodataframe is within one of the polygons in pgh_bounds"""
  each_poly = list(range(len(pgh_bounds)))
  gdf_ind = points_gdf.index.tolist()
  my_checks = []
  for i in gdf_ind:
    in_pgh = False
    for x in each_poly:
      check_in = points_gdf[i:i+1].within(pgh_bounds.loc[x, 'geometry'])[0:1].values
      if check_in.size>0:
        in_pgh = True
    my_checks.append(in_pgh)
  return my_checks

# Check if events are in pittsburgh
event_indices = check_in_pgh(all_events_gp)
# Only keep those events that are in pittsburgh 
all_gp_pgh = all_events_gp.loc[event_indices].reset_index(drop=True)

# Join event with neighborhood using spatial join
all_event_neighbor = gp.sjoin(all_gp_pgh, pgh_neighbor_merge, how='left', op='within').drop(labels=['index_right'], axis=1).reset_index(drop=True)
all_event_neighbor = all_event_neighbor.sort_values(by='Date').reset_index(drop=True)
all_event_neighbor['Date'] = all_event_neighbor['Date'].apply(str)
pgh_neighbor_merge = pgh_neighbor_merge.sort_values(by='hood').reset_index()
# Function to be called in other files to output the two main geodataframes produced by this module
def export_event_neighbor():
    return pgh_neighbor_merge, all_event_neighbor
