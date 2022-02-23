# -*- coding: utf-8 -*-
"""
Created on Sun Oct 10 12:33:54 2021

author: 
Allison Michalowski amichalo@andrew.cmu.edu
Eshan Mehotra emehotr@andrew.cmu.edu
Sowjanya Manipal smanipal@andrew.cmu.edu

Imports:
    TwitterScraping
    hood_event_scrape_module
"""


import tkinter as tk                    
from tkinter import ttk
import pandas as pd
import platform
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import geopandas as gp
import requests
import zipfile
import io
import re
from wordcloud import WordCloud
from geopandas import GeoDataFrame
import TwitterScraping as TS


# Set fonts for app
TitleFont = ('Verdana', 35)  
ButtonFont = ('Verdana', 16)
HeaderFont = ('Verdana', 18)
NeighborhoodFont = ('Verdana', 24) 
BodyFont = ('Verdana', 14)
SmallFont = ('Verdana', 11)

# def print_full(x):
#     pd.set_option('display.max_rows', None)
#     pd.set_option('display.max_columns', None)
#     pd.set_option('display.width', 2000)
#     pd.set_option('display.float_format', '{:20,.2f}'.format)
#     pd.set_option('display.max_colwidth', None)
#     print(x)
#     pd.reset_option('display.max_rows')
#     pd.reset_option('display.max_columns')
#     pd.reset_option('display.width')
#     pd.reset_option('display.float_format')
#     pd.reset_option('display.max_colwidth')


# %% Functions

# label_plot function for labeling plots made with matplotlib
def label_plot(plot_axis, title, x_axis_label, y_axis_label, title_weight="bold", title_size=16, axis_weight="bold", axis_size=14, title_color='black', axis_color='black' ):
  """This function applies a title and axis labels to a given plots and offers a variety of keyword parameters
  to quickly adjust the display of these components on the plots"""
  plot_axis.set_title(title, weight=title_weight, size=title_size, color=title_color)
  plot_axis.set_xlabel(x_axis_label, weight=axis_weight, size=axis_size, color=axis_color)
  plot_axis.set_ylabel(y_axis_label, weight=axis_weight, size=axis_size, color=axis_color)
  
def use_archive_data():        
    pgh_merge_data = pd.read_csv('pgh_neighbor_merge_final.csv')
    pgh_merge_data = pgh_merge_data.sort_values(by='hood').reset_index()
    all_the_events = pd.read_csv('all_event_neighbor_final.csv')
    return pgh_merge_data, all_the_events

def populate_event_page(my_scroll):                                 
    for i in range(len(all_the_events)):
        #print(all_the_events.loc[i])
        my_frame = tk.Frame(my_scroll.viewPort)
        my_frame.grid(row=i, column=0, sticky='nsew')
        this_event_name = tk.Text(my_frame, wrap='word', font=HeaderFont, height=1, bg='#0096a1')
        this_event_name.grid(row=0, column=0, sticky='ew')
        event_name_str = str(all_the_events.loc[i]['Name'])
        this_event_name.insert(tk.END, event_name_str)
        this_event_name.configure(state='disabled')
        # Add date and time smaller
        this_event_dt = tk.Text(my_frame, wrap='word', font=BodyFont, height=4)
        this_event_dt.grid(row=1, column=0, sticky='ew')
        event_date_str = 'Date: ' + str(all_the_events.loc[i]['Date'])[:-8] + '\n'
        if str(all_the_events.loc[i]['Time']) != 'nan':
            event_time_str = 'Time: ' + str(all_the_events.loc[i]['Time']) + '\n'
        else:
            event_time_str = ''
        event_neighborhood_str = 'Neighborhood: ' + str(all_the_events.loc[i]['hood'] + '\n')
        this_event_dt.insert(tk.END, event_date_str)
        this_event_dt.insert(tk.END, event_time_str)
        this_event_dt.insert(tk.END, event_neighborhood_str)
        this_event_dt.configure(state='disabled')
        event_more_info_btn = tk.Button(my_frame, text ="Click for more info!", command = lambda x=i: create_window(x, app), bg='light grey', font=BodyFont)
        event_more_info_btn.grid(row=2, column=0, sticky='we')
        
def populate_hood_page(my_tab):
    hood_button_frame = tk.Frame(my_tab)
    hood_button_frame.grid(row=2, column=0, sticky='nsew')
    for i in range(len(thehoods_clean)):
        my_row_val = int(np.trunc(i/6))
       # print(my_row_val)
        my_col_val = (i)%6
       # print(my_col_val)
        #print(thehoods_clean.loc[i, 'hood'])
        neighborhood_button = tk.Button(hood_button_frame, text = thehoods_clean.loc[i, 'hood'], command = lambda x=i: create_hood_window(x, app), bg='light grey', font=SmallFont)
        neighborhood_button.grid(row=my_row_val, column=my_col_val, sticky='we')
        
def populate_tweet_page(my_scroll):
    my_frame = tk.Frame(my_scroll.viewPort)
    my_frame.grid(row=0, column=0, sticky='nsew')
    this_tweet_label = tk.Text(my_frame, wrap='word', font=HeaderFont, height=1, bg='#0096a1')
    this_tweet_label.grid(row=0, column=0, sticky='ew')
    this_tweet_label.insert(tk.END, 'Compare by All Time Popularity')
    this_tweet_label.configure(state='disabled')
    plot1=TS.plotAlltime(usertweetdf,df1,df2)
    my_map_plot = FigureCanvasTkAgg(plot1, my_frame)
    my_map_plot.get_tk_widget().grid(row=1, column=0, sticky='w')
    this_tweet_label2 = tk.Text(my_frame, wrap='word', font=HeaderFont, height=1, bg='#0096a1')
    this_tweet_label2.grid(row=2, column=0, sticky='ew')
    this_tweet_label2.insert(tk.END, 'Compare Recent Popularity')
    this_tweet_label2.configure(state='disabled') 
    plot2=TS.plotRecentAct(usertweetdf,df1,df2)
    my_map_plot = FigureCanvasTkAgg(plot2, my_frame)
    my_map_plot.get_tk_widget().grid(row=3, column=0, sticky='w')
    this_tweet_label3 = tk.Text(my_frame, wrap='word', font=HeaderFont, height=1, bg='#0096a1')
    this_tweet_label3.grid(row=4, column=0, sticky='ew')
    this_tweet_label3.insert(tk.END, "What's Happening in Pittsburgh?")
    this_tweet_label3.configure(state='disabled')
    plot3=TS.plotWC(usertweetdf,df1,df2)
    my_map_plot = FigureCanvasTkAgg(plot3, my_frame)
    my_map_plot.get_tk_widget().grid(row=5, column=0, sticky='w')

def plot_my_hood(my_index, df):
    this_hood = str(df.loc[my_index]['hood'])
    fig_pgh_neighborhoods, ax2 = plt.subplots(figsize=[6, 6])
    thehoods_clean.plot(ax=ax2, color="white")
    thehoods_clean.boundary.plot(ax=ax2, color="navy", linewidth=.15)
    thehoods_clean.loc[thehoods_clean['hood']==this_hood].plot(ax=ax2, color='#0096a1')
    ax2.set_facecolor("#EEEEEE")
    label_plot(ax2, "Find the neighborhood!", "Longitude", "Latitude")
    return fig_pgh_neighborhoods

def plot_my_art(my_index, df):
    this_hood = str(df.loc[my_index]['hood'])
    this_hood_gp = thehoods_clean.loc[thehoods_clean['hood']==this_hood]
    art_in_gp = gp.sjoin(art_gp, this_hood_gp, op='within', how='inner')
    fig_hood_art, ax3 = plt.subplots(figsize=[6, 6])
    thehoods_clean.loc[thehoods_clean['hood']==this_hood].plot(ax=ax3, color='white')
    thehoods_clean.loc[thehoods_clean['hood']==this_hood].boundary.plot(ax=ax3, color='navy')
    art_in_gp.plot(ax=ax3, color='#0096a1', alpha=0.5)
    ax3.set_facecolor("#EEEEEE")
    label_plot(ax3, "Public Art in " + this_hood, "Longitude", "Latitude")
    return fig_hood_art

def plot_my_playground(my_index, df):
    this_hood = str(df.loc[my_index]['hood'])
    this_hood_gp = thehoods_clean.loc[thehoods_clean['hood']==this_hood]
    playground_in_gp = gp.sjoin(playground_gp, this_hood_gp, op='within', how='inner')
    fig_hood_playground, ax4 = plt.subplots(figsize=[6, 6])
    thehoods_clean.loc[thehoods_clean['hood']==this_hood].plot(ax=ax4, color='white')
    thehoods_clean.loc[thehoods_clean['hood']==this_hood].boundary.plot(ax=ax4, color='navy')
    playground_in_gp.plot(ax=ax4, color = '#0096a1', alpha=0.5)
    ax4.set_facecolor("#EEEEEE")
    label_plot(ax4, "Playgrounds in " + this_hood, "Longitude", "Latitude")
    return fig_hood_playground
    
def plot_my_cloud(my_index, df):
    this_hood = str(df.loc[my_index]['hood'])
    my_desc_str = str(pgh_merge_data.loc[my_index]['desc_all'])
    my_desc_str_cs = re.sub(r' +', r',', my_desc_str)
    this_hood_text = ((this_hood + ',')*5) + my_desc_str_cs
    hood_wordcloud = WordCloud(max_words=50, background_color='white', regexp=r"\w[\w| ']+", collocations=False).generate(this_hood_text)
    fig_hood_word, ax5 = plt.subplots(figsize=[10, 6])
    ax5.imshow(hood_wordcloud, interpolation='bilinear')
    ax5.axis('off')
    label_plot(ax5, "What do people say about " + this_hood + '\n', "Longitude", "Latitude", title_color='#0096a1', title_size=22)
    return fig_hood_word

def plot_my_transport(my_index, df):
    figure = plt.Figure(figsize=(5.5,3), dpi=100)
    ax = figure.add_subplot(111)
    x = ['Walk Score', 'Bike Score', 'Transit Score']
    y = df.loc[[my_index],['walkscore','transitscore', 'bikescore']].values[0].tolist()
    ax.set_ylim([0, 100])
    ax.bar(x, y)
    bars = ax.bar(x, y, color=['#4a2374', '#228d8d', '#9fdc5c'])
    for bar in bars:
        my_val = bar.get_height()
        ax.text(bar.get_x() + 0.4, my_val, my_val, ha='center')
    
    ax.set_title('Transportation Quality', fontsize=18)
    return figure

def create_window(my_index, controller): 
        toplevel = tk.Toplevel(controller)
        toplevel.title(str(all_the_events.loc[my_index]['Name']))
        toplevel.geometry('1000x600')
        toplevel.grid_columnconfigure(1, weight=1)
        toplevel.grid_rowconfigure(1, weight=1)
        e_frame = ScrollFrame(toplevel)
        e_frame.grid(row=0, column=0, sticky='nsew', columnspan=3, rowspan=2)
        event_name_det_str = str(all_the_events.loc[my_index]['Name'])
        this_event_det_name = tk.Text(e_frame.viewPort, wrap='word', font=HeaderFont, height=1)
        this_event_det_name.grid(row=0, column=0, sticky='ew')
        this_event_det_name.insert(tk.END, event_name_det_str)
        this_event_det_name.configure(state='disabled')
        
        this_event_det_other = tk.Text(e_frame.viewPort, wrap=tk.WORD, font=BodyFont, height=15, width=60)
        this_event_det_other.grid(row=1, column=0, sticky='w')
        event_date_det_str = 'Date: ' + str(all_the_events.loc[my_index]['Date'])[:-8] + '\n'
        this_event_det_other.insert(tk.END, event_date_det_str)
        if str(all_the_events.loc[my_index]['Time']) != 'nan':
            event_time_det_str = 'Time: ' + str(all_the_events.loc[my_index]['Time']) + '\n'
            this_event_det_other.insert(tk.END, event_time_det_str)
        if str(all_the_events.loc[my_index]['Address']) != 'nan':
            event_address_det_str = 'Address: ' + str(all_the_events.loc[my_index]['Address']) + '\n'
            this_event_det_other.insert(tk.END, event_address_det_str)   
        if str(all_the_events.loc[my_index]['Link']) != 'nan':
            event_link_det_str = 'Link: ' + str(all_the_events.loc[my_index]['Link']) + '\n'
            this_event_det_other.insert(tk.END, event_link_det_str)  
        if str(all_the_events.loc[my_index]['Description']) != 'nan':
            event_desc_det_str = '\n' + 'Description: ' + str(all_the_events.loc[my_index]['Description']) + '\n\n\n'
            this_event_det_other.insert(tk.END, event_desc_det_str)  
        
        hood_info_label = tk.Label(e_frame.viewPort, text ="Get to learn more about the neighborhood!", font = NeighborhoodFont, fg='#0096a1', bg='white', anchor='w', justify=tk.LEFT)
        hood_info_label.grid(row = 2, column = 0, padx = 1, pady = 10, sticky='w')
        hood_name_label = tk.Label(e_frame.viewPort, text ='Your Neighborhood: '+ str(all_the_events.loc[my_index]['hood']), font = HeaderFont, fg='#0096a1', bg='white', anchor='w')
        hood_name_label.grid(row = 3, column = 0, padx = 1, pady = 10, sticky='w')
            
        try:
            fig_pgh_neighborhoods = plot_my_hood(my_index, all_the_events)
            my_map_plot = FigureCanvasTkAgg(fig_pgh_neighborhoods, e_frame.viewPort)
            my_map_plot.get_tk_widget().grid(row=4, column=0, sticky='w', padx=10)
        except:
           pass

        # Plot artworks if any are in the neighborhood
        if all_the_events.loc[my_index]['art_count']>0:

            try:
                fig_hood_art = plot_my_art(my_index, all_the_events)
                my_map_plot = FigureCanvasTkAgg(fig_hood_art, e_frame.viewPort)
                my_map_plot.get_tk_widget().grid(row=5, column=0, sticky='w')
                
            except:
                pass
            
        if all_the_events.loc[my_index]['playground_count']>0:
            try:
                fig_hood_playground = plot_my_playground(my_index, all_the_events)
                my_map_plot = FigureCanvasTkAgg(fig_hood_playground, e_frame.viewPort)
                my_map_plot.get_tk_widget().grid(row=6, column=0)
            except:
                pass
        if len(str(all_the_events.loc[my_index]['desc_all']))>100:
            try:
                fig_hood_word = plot_my_cloud(my_index, all_the_events)
                my_map_plot = FigureCanvasTkAgg(fig_hood_word, e_frame.viewPort)
                my_map_plot.get_tk_widget().grid(row=7, column=0, sticky='w')
            except:
                pass
        if pgh_merge_data.loc[my_index]['walkscore'] >10:
            try:
                figure = plot_my_transport(my_index, all_the_events)
                my_bar = FigureCanvasTkAgg(figure, e_frame.viewPort)
                my_bar.get_tk_widget().grid(row=8, column=0, sticky='w')
            # if the values are nan, pops up posx and posy should be finite values, ignore because just not plotting
            except:
                pass
            
def create_hood_window(my_index, controller):
    toplevel = tk.Toplevel(controller)
    toplevel.geometry('1000x600')
    toplevel.title(str(thehoods_clean.loc[my_index]['hood']))
    toplevel.grid_columnconfigure(1, weight=1)
    toplevel.grid_rowconfigure(1, weight=1)
    e_frame = ScrollFrame(toplevel)
    e_frame.grid(row=0, column=0, sticky='nsew', columnspan=3, rowspan=2)
    my_hood_name = str(thehoods_clean.loc[my_index]['hood'])
    neighborhood_heading = tk.Text(e_frame.viewPort, wrap='word', font=NeighborhoodFont, height=1, fg='#0096a1')
    neighborhood_heading.grid(row=0, column=0, sticky='ew')
    neighborhood_heading.insert(tk.END, my_hood_name)
    neighborhood_heading.configure(state='disabled')
    plot_spot = 0
    try:
        fig_pgh_neighborhoods = plot_my_hood(my_index, pgh_merge_data)
        my_map_plot = FigureCanvasTkAgg(fig_pgh_neighborhoods, e_frame.viewPort)
        my_map_plot.get_tk_widget().grid(row=4, column=0, sticky='w', padx=10)
    except:
       pass
    
    # Plot artworks if any are in the neighborhood
    if pgh_merge_data.loc[my_index]['art_count']>0:
        try:
            fig_hood_art = plot_my_art(my_index, pgh_merge_data)
            my_map_plot = FigureCanvasTkAgg(fig_hood_art, e_frame.viewPort)
            my_map_plot.get_tk_widget().grid(row=5, column=0, sticky='w')
        except:
            pass
        
    if pgh_merge_data.loc[my_index]['playground_count']>0:
        try:
            fig_hood_playground = plot_my_playground(my_index, pgh_merge_data)
            my_map_plot = FigureCanvasTkAgg(fig_hood_playground, e_frame.viewPort)
            my_map_plot.get_tk_widget().grid(row=6, column=0, sticky='w')
        except:
            pass
    if len(str(pgh_merge_data.loc[my_index]['desc_all']))>100:
        fig_hood_word = plot_my_cloud(my_index, pgh_merge_data)
        my_map_plot = FigureCanvasTkAgg(fig_hood_word, e_frame.viewPort)
        my_map_plot.get_tk_widget().grid(row=7, column=0, sticky='w', columnspan=2)
    
    if pgh_merge_data.loc[my_index]['walkscore'] >0:
        try:
            figure = plot_my_transport(my_index, pgh_merge_data)
            my_bar = FigureCanvasTkAgg(figure, e_frame.viewPort)
            my_bar.get_tk_widget().grid(row=8, column=0, sticky='w')
            
        except:
           pass
  


# %% Get geodata for plotting in app

### Get neighborhood geodata -> thehoods_clean  
# Download and get shapefile for pgh neighborhoods
url = 'https://pghgishub-pittsburghpa.opendata.arcgis.com/datasets/dbd133a206cc4a3aa915cb28baa60fd4_0.zip?outSR=%7B%22latestWkid%22%3A2272%2C%22wkid%22%3A102729%7D'
local_path = 'tmp/'
r = requests.get(url)
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall(path=local_path)
filenames = [y for y in sorted(z.namelist()) for ending in ['dbf', 'prj', 'shp', 'shx'] if y.endswith(ending)] 
# Create geodataframe from shapefile
thehoods=gp.read_file(local_path+'Neighborhoods_.shp')
# Make geodataframe keeping only potentially useful info from neighborhoods data
thehoods_clean=thehoods[['objectid', 'geoid10', 'sqmiles', 'hood', 'hood_no', 'unique_id', 'geometry']].copy()
thehoods_clean = thehoods_clean.to_crs('EPSG:2272')
# Sort by neighborhood alphabetically
thehoods_clean = thehoods_clean.sort_values(by='hood').reset_index()

### Get art data for plotting -> art_gp
# Turn public art into geodataframe
art_url = 'https://data.wprdc.org/datastore/dump/00d74e83-8a23-486e-841b-286e1332a151'
# Read data into normal dataframe
public_art = pd.read_csv(art_url)
# Clean and extract useful information
public_art_clean = public_art[['id', 'title', 'neighborhood', 'latitude', 'longitude']].copy().dropna().reset_index(drop=True)
art_gp = GeoDataFrame(public_art_clean, crs='EPSG:4326', geometry=gp.points_from_xy(public_art_clean.longitude, public_art_clean.latitude))
art_gp = art_gp.to_crs('EPSG:2272')


# Get playground data for plotting
playgrounds_url = 'https://data.wprdc.org/datastore/dump/47350364-44a8-4d15-b6e0-5f79ddff9367'
# Read data into normal dataframe
playgrounds = pd.read_csv(playgrounds_url)
# Clean and extract useful information
playgrounds_clean = playgrounds[['id', 'name', 'neighborhood', 'latitude', 'longitude']].copy().dropna().reset_index(drop=True)
playground_gp = GeoDataFrame(playgrounds_clean, crs='EPSG:4326', geometry=gp.points_from_xy(playgrounds_clean.longitude, playgrounds_clean.latitude))
playground_gp = playground_gp.to_crs('EPSG:2272')
fig_pgh_neighborhoods, ax = plt.subplots(figsize=[10, 10])
thehoods_clean.plot(ax=ax, color="white")
thehoods_clean.boundary.plot(ax=ax, color="navy", linewidth=.15)
ax.set_facecolor("#EEEEEE")
label_plot(ax, "Pittsburgh Neighborhoods", "Longitude", "Latitude")
# fig_pgh_neighborhoods.show()
# fig_pgh_neighborhoods.savefig( "pgh_neighborhoods_outline.png")

pgh_merge_data = pd.DataFrame()
all_the_events = pd.DataFrame()
usertweetdf = pd.DataFrame()
df1 = pd.DataFrame()
df2 = pd.DataFrame()
get_twitter = False
# Make class for entire tkinter app
class SampleApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("1080x600")
        self.container = tk.Frame(self)
        container = self.container
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)        
        self.frames = {}
        frame1 = HomePage(container, self)
        frame1.grid(row=0, column=0, sticky='nsew')
        self.frames[HomePage] = frame1
        frame2 = Page1(container, self)
        frame2.grid(row=0, column=0, sticky='nsew')
        self.frames[Page1] = frame2
        frame3 = Page2(container, self)
        frame3.grid(row=0, column=0, sticky='nsew')
        self.frames[Page2] = frame3
        self.show_frame(HomePage)
        
    def show_frame(self, cont):
        if cont!=HomePage:
            import TwitterScraping as TS
            global pgh_merge_data
            global all_the_events
            global usertweetdf
            global df1
            global df2
            global get_twitter
            
            if cont==Page1:
                # global pgh_merge_data
                # global all_the_events
                usertweetdf,df1,df2 = TS.gettweetDFs_arc(filename="multiuser_tweets_arc.csv")
                pgh_merge_data, all_the_events = use_archive_data()
                self.frames[cont].destroy()
                get_twitter = True
                framenew = Page1(self.container, self)
                framenew.grid(row=0, column=0, sticky='nsew')
                self.frames[Page1] = framenew
                
                
            if cont==Page2:
                print("Geocoding is time consuming. \nPlease be patient and prepared to wait up to 20 or more minutes depending on amount of events.")
                import hood_event_scrape_module as hesm
                usertweetdf,df1,df2 = TS.gettweetDFs_live()
                pgh_merge_data, all_the_events = hesm.export_event_neighbor()
                pgh_merge_data = pgh_merge_data.sort_values(by='hood').reset_index()
                self.frames[cont].destroy()
                get_twitter = True
                framenew = Page2(self.container, self)
                framenew.grid(row=0, column=0, sticky='nsew')
                self.frames[Page2] = framenew
                print("Thank you for waiting!\n The application is ready for interaction.")
                
            
        frame= self.frames[cont]    
        frame.tkraise()
        

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        ex_space = tk.Label(self, text='\n\n', font=('ButtonFont'))
        ex_space.grid(row=0, column=0, padx=10, pady=10)
        hp_label = tk.Label(self, text ="WhatsUp PGH", font = TitleFont, fg='#0096a1')
        hp_label.grid(row = 1, column = 0, padx = 10, pady = 10, columnspan=2)
        hp_label = tk.Label(self, text =
                            "Use our application to find out what's happening around Pittsburgh! \nLearn about the latest events, get to know the neighborhoods, \nand hear what people are saying with our local Twitter data.", font = ButtonFont, fg='black')
        hp_label.grid(row = 2, column = 0, padx = 10, pady = 10, columnspan=2)
        ex_space2 = tk.Label(self, text='\n\n', font=('ButtonFont'))
        ex_space2.grid(row=3, column=0, padx=10, pady=10)
        button1 = tk.Button(self, text ="See latest archived events\n (Warning: may not include most recent data)", command = lambda x=Page1: controller.show_frame(Page1), 
                            font = ButtonFont)
        button1.grid(row = 4, column = 0, padx = 10, pady = 10)
        button2 = tk.Button(self, text ="Live scrape to see the most recent events\n (Warning: substantial loading time)", command = lambda x=Page2 : controller.show_frame(Page2), font = ButtonFont)
        button2.grid(row = 4, column = 1, padx = 10, pady = 10)

# ScrollFrame widget from github source: https://gist.github.com/mp035/9f2027c3ef9172264532fcd6262f3b01
class ScrollFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent) # create a frame (self)

        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")          #place canvas on self
        self.viewPort = tk.Frame(self.canvas, background="#ffffff")                    #place a frame on the canvas, this frame will hold the child widgets 
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview) #place a scrollbar on self 
        self.canvas.configure(yscrollcommand=self.vsb.set)                          #attach scrollbar action to scroll of canvas

        self.vsb.pack(side="right", fill="y")                                       #pack scrollbar to right of self
        self.canvas.pack(side="left", fill="both", expand=True)                     #pack canvas to left of self and expand to fil
        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw",            #add view port frame to canvas
                                  tags="self.viewPort")

        self.viewPort.bind("<Configure>", self.onFrameConfigure)                       #bind an event whenever the size of the viewPort frame changes.
        self.canvas.bind("<Configure>", self.onCanvasConfigure)                       #bind an event whenever the size of the canvas frame changes.
            
        self.viewPort.bind('<Enter>', self.onEnter)                                 # bind wheel events when the cursor enters the control
        self.viewPort.bind('<Leave>', self.onLeave)                                 # unbind wheel events when the cursorl leaves the control

        self.onFrameConfigure(None)                                                 #perform an initial stretch on render, otherwise the scroll region has a tiny border until the first resize

    def onFrameConfigure(self, event):                                              
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))                 #whenever the size of the frame changes, alter the scroll region respectively.

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width = canvas_width)            #whenever the size of the canvas changes alter the window region respectively.

    def onMouseWheel(self, event):                                                  # cross platform scroll wheel event
        if platform.system() == 'Windows':
            self.canvas.yview_scroll(int(-1* (event.delta/120)), "units")
        elif platform.system() == 'Darwin':
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll( -1, "units" )
            elif event.num == 5:
                self.canvas.yview_scroll( 1, "units" )
    
    def onEnter(self, event):                                                       # bind wheel events when the cursor enters the control
        if platform.system() == 'Linux':
            self.canvas.bind_all("<Button-4>", self.onMouseWheel)
            self.canvas.bind_all("<Button-5>", self.onMouseWheel)
        else:
            self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)

    def onLeave(self, event):                                                       # unbind wheel events when the cursorl leaves the control
        if platform.system() == 'Linux':
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")

class Page1(tk.Frame): 
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        tabControl = ttk.Notebook(self)
  
        ls_tab1 = ttk.Frame(tabControl)
        ls_tab2 = ttk.Frame(tabControl)
        ls_tab3 = ttk.Frame(tabControl)
        
        tabControl.add(ls_tab1, text ='Events')
        tabControl.add(ls_tab2, text ='Neighborhoods')
        tabControl.add(ls_tab3, text ='Twitter')
        tabControl.pack(expand = 1, fill ="both")
        ttk.Label(ls_tab1, 
                  text ="Check out these Pittsburgh events!", font=ButtonFont).grid(column = 0, 
                                        row = 0,
                                        padx = 30,
                                        pady = 30,
                                        sticky = 'w')  
        ttk.Label(ls_tab2,
                  text ="Explore Pittsburgh Neighborhoods!", font=ButtonFont).grid(column = 0,
                                            row = 1, 
                                            padx = 30,
                                            pady = 30,
                                            sticky = 'w')
            
        ttk.Label(ls_tab3,
                   text ="Find out what's going on in Pittsburgh directly from the people!", font=ButtonFont).grid(column = 0,
                                            row = 1, 
                                            padx = 30,
                                            pady = 30,
                                            sticky = 'w')
                                                                                                  
                                                                                                  
                                                                  
        scroll_ls1 = ScrollFrame(ls_tab1)
        ls_tab1.grid_columnconfigure(1, weight=1)
        ls_tab1.grid_rowconfigure(2, weight=1)
        ls_tab1.grid_rowconfigure(3, weight=1)
        scroll_ls1.grid(row=1, column=0, sticky='nsew', columnspan=3, rowspan=2)
        
        populate_event_page(scroll_ls1)
        populate_hood_page(ls_tab2)
        
        scroll_ls3 = ScrollFrame(ls_tab3)
        ls_tab3.grid_columnconfigure(1, weight=1)
        ls_tab3.grid_rowconfigure(2, weight=1)
        ls_tab3.grid_rowconfigure(3, weight=1)
        scroll_ls3.grid(row=2, column=0, sticky='nsew', columnspan=2, rowspan=2)
        if get_twitter == True:
            populate_tweet_page(scroll_ls3)

class Page2(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tabControl2 = ttk.Notebook(self)
  
        ls2_tab1 = ttk.Frame(tabControl2)
        ls2_tab2 = ttk.Frame(tabControl2)
        ls2_tab3 = ttk.Frame(tabControl2)
        
        tabControl2.add(ls2_tab1, text ='Events')
        tabControl2.add(ls2_tab2, text ='Neighborhoods')
        tabControl2.add(ls2_tab3, text ='Twitter')
        tabControl2.pack(expand = 1, fill ="both")
        ttk.Label(ls2_tab1, 
                  text ="Check out these Pittsburgh events!", font=ButtonFont).grid(column = 0, 
                                        row = 0,
                                        padx = 30,
                                        pady = 30,
                                        sticky = 'w')  
        ttk.Label(ls2_tab2,
                  text ="Explore Pittsburgh Neighborhoods!", font=ButtonFont).grid(column = 0,
                                            row = 1, 
                                            padx = 30,
                                            pady = 30,
                                            sticky='w')
            
        ttk.Label(ls2_tab3,
                   text ="Find out what's going on in Pittsburgh directly from the people!", font=ButtonFont).grid(column = 0,
                                            row = 1, 
                                            padx = 30,
                                            pady = 30,
                                            sticky = 'w')
        scroll1_ls2 = ScrollFrame(ls2_tab1)
        ls2_tab1.grid_columnconfigure(1, weight=1)
        ls2_tab1.grid_rowconfigure(2, weight=1)
        ls2_tab1.grid_rowconfigure(3, weight=1)
        scroll1_ls2.grid(row=2, column=0, sticky='nsew', columnspan=3, rowspan=2)
        
        populate_event_page(scroll1_ls2)
        populate_hood_page(ls2_tab2)
        scroll3_ls2 = ScrollFrame(ls2_tab3)
        ls2_tab3.grid_columnconfigure(1, weight=1)
        ls2_tab3.grid_rowconfigure(2, weight=1)
        ls2_tab3.grid_rowconfigure(3, weight=1)
        ls2_tab3.grid_columnconfigure(1, weight=1)
        scroll3_ls2.grid(row=2, column=0, sticky='nsew', columnspan=3, rowspan=2)
        if get_twitter == True:
            populate_tweet_page(scroll3_ls2)
        
if __name__ == '__main__':
    app = 0
    app = SampleApp()
    app.mainloop()
    app.quit()
            
