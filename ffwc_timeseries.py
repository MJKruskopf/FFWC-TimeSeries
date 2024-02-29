# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 14:36:19 2023

@author: mkruskop

Purpose: creates time series using data scrapped from the ffwc website (http://www.ffwc.gov.bd/#) Data-> Observed Water Level   
that has been saved on SOCRATES

Inputs: Index requested for associated station

Output: csv of datetime object and associated water level

Usage Example: python ffwc_timeseries.py
"""

import csv, os, glob, shutil, pandas as pd,numpy as np,matplotlib.pyplot as plt
from datetime import datetime

#[ACTION] Change data and save paths as needed
#'/home/Socrates/brushi/FFWC/FFWC_Data/water_level'
#'/home/Socrates/mkruskopf/FFWC/FFWC_Test_Data'
data_path = '/home/Socrates/brushi/FFWC/FFWC_Data/water_level'
save_path = '/home/Socrates/mkruskopf/FFWC/Timeseries'

#Import stations of interest
station_path = '/home/Socrates/mkruskopf/FFWC/ML_Stations_ofInterest.csv'
#'/home/Socrates/mkruskopf/FFWC/BG_Stations_ofInterest.csv' Stations provided by Manish of interest to FFWC
#'/home/Socrates/mkruskopf/FFWC/ML_Stations_ofInterest.csv' Stations arouond BG for ML training
station_df = pd.read_csv(station_path)
stations_list=station_df['Stations'].tolist()
print(station_df)

#Select station
station_index = int(input("Enter index for selected station: "))#Select 

#Navigate to data location
os.chdir(data_path)

#use glob to get all the csv files in the folder
path = os.getcwd()

#glob.glob returns a list of files
csv_files = glob.glob(os.path.join(path, "*.csv")) #Note: gets files not in order

#Iterate through each file in data path and retrieve water level data for selected station
station = stations_list[station_index]
print(station)

water_level = []
dates = []
days_avail = 0

for f in csv_files:
  df = pd.read_csv(f)
  columnName = df.columns[1]#Previously column name changed to V2 at times
  
  #Get date from file name (will be used if one from column name is unavailable)
  end = f.find('_FFWC_water_level')
  filename_date = f[(end-10):end] #Optional: use date from filename
  year = f[(end-10):(end-6)]
  date = filename_date
  
  try:
    #Get water level at station
    station_data = df.loc[df[columnName]==station,:]#if location doesn't exist it errors here and moves to except
    water_level.append(float(station_data.iloc[:,4].iat[0]))#Retrieving column 4 'WL - Observe (m)-dd-mm'
    days_avail+=1
    
    #Extract date from column heading 
    if df.columns[4] != 'V5':
        date_column = df.columns[4]
        start_date = date_column.find('(m)-')
        col_day = date_column[(start_date+4):-3]
        col_month = date_column[(start_date+7):]
        date = year +"-"+ col_month+"-" + col_day #Create date from column heading
        print("Column Date Retrieved: ", date)
        print("Filename Date: ", filename_date)
        try: #If it can be converted to a datetime object it is a valid date
            datetime_date = datetime.strptime(date, '%Y-%m-%d').date()
        except: #Otherwise use the date from the filename
           date = filename_date
           
    

    #Create datetime object for water level table
    datetime_date = datetime.strptime(date, '%Y-%m-%d').date()
    dates.append(datetime_date)
    

  except:
     #Used to catch ValueError: could not convert string to float: '-' 
    #Note: Occurs when data does not exist (unsure of meaning)
    print('No Data: '+date)

print("Days Available: " + str(days_avail))

#Create and save csv 
print('Saving time series for: '+ station )
print("At: "+ save_path)

print("water level length: ", len(water_level))
print('date length: ', len(dates))
      

columns = {'Date':dates,'Water_Level':water_level}
wlv_df = pd.DataFrame(columns)
wlv_filename = station + '.csv'
os.chdir(save_path)
wlv_df.to_csv(wlv_filename,index = True)

#Plot data and display
print('Saving plot of timeseries for: ' + station)
wlv_df.plot.scatter(x=0,y = 1)
plt.title('Water Level at '+station)
plt.ylabel('Water Level [m]')
plt.xlabel('Date')
plt.xticks(rotation ='vertical' )
os.chdir(save_path)
plt.savefig(station+'_ts_plt.png',bbox_inches ='tight' )
plt.show

#Remove repeated values-------------------------------------------------------

#Convert to datetime object {'%Y-%m-%d'}
#type pandas._libs.tslibs.timestamps.Timestamp

#wlv_df['Date'] = pd.to_datetime(wlv_df['Date'], yearfirst = True)

#Sort by date
df_sorted = wlv_df.sort_values('Date', ascending=True)

#Remove repeated values from dataframe
#Note: dataframe must be sorted by date
past_wlv = -1 
indices = []
#Iterate through rows
for index, row in df_sorted.iterrows():
  wlv = row.Water_Level
  #If a repeated value is found add the index to the list of indices
  if wlv == past_wlv:
    past_wlv = wlv
    indices.append(index)
    print(past_wlv)
  else:
    past_wlv = wlv

#Remove repeated values based on index
df_sorted.drop(indices, axis=0, inplace = True)

print('Number of values removed: ', len(indices))
#-------------------------------------------------------------

#Create and save qc csv
wlv_qc_filename = station + '_qc.csv'
os.chdir(save_path)
df_sorted.to_csv(wlv_qc_filename,index = True)

#Plot QC data and display
print('Saving plot of timeseries for: ' + station)
df_sorted.plot.scatter(x=0,y = 1)
plt.title('Water Level at '+station)
plt.ylabel('Water Level [m]')
plt.xlabel('Date')
plt.xticks(rotation ='vertical' )
os.chdir(save_path)
plt.savefig(station+'_ts_qc_plt.png',bbox_inches ='tight' )
plt.show


