import pandas as pd
import numpy as np
import datetime
import pickle
from sklearn.ensemble import RandomForestRegressor

# required functions
def fn_is_weekend(row):
    if ((row['journeyStartWeekday'] == 5) | (row['journeyStartWeekday'] == 6)):
        return 1
    else:
        return 0

def fn_get_year_quarters(row):
    if ((row['journeyStartMonth'] >= 0) & (row['journeyStartMonth'] <= 2)):
        return 1
    elif ((row['journeyStartMonth'] >= 3) & (row['journeyStartMonth'] <= 5)):
        return 2
    elif ((row['journeyStartMonth'] >= 6) & (row['journeyStartMonth'] <= 8)):
        return 3
    else:
        return 4

def fn_get_peak_hours(row):
    if ((row['journeyStartHr'] >= 21) | (row['journeyStartHr'] <= 5)):
        return 'nightHours'
    elif ((row['journeyStartHr'] == 6) | (row['journeyStartHr'] == 7)):
        return 'morningNonPeakHours'
    elif ((row['journeyStartHr'] >= 8) & (row['journeyStartHr'] <= 13)):
        return 'morningPeakHours'
    elif ((row['journeyStartHr'] >= 14) & (row['journeyStartHr'] <= 17)):
        return 'eveningPeakHours'
    else:
        return 'eveningNonPeakHours'


# Reading data from given files
dfJourneys = pd.read_csv('data/journeys.csv')


# Pre-processing dfJourneys
dfJourneys['Trip Start At Local Time'] = pd.to_datetime(dfJourneys['Trip Start At Local Time'], format="%Y/%m/%d %H:%M:%S")
dfJourneys['Trip End At Local Time'] = pd.to_datetime(dfJourneys['Trip End At Local Time'], format="%Y/%m/%d %H:%M:%S")
dfJourneys['Trip Created At Local Time'] = pd.to_datetime(dfJourneys['Trip Created At Local Time'], format="%Y/%m/%d %H:%M:%S")

dfJourneys['Trip Sum Trip Price'] = dfJourneys['Trip Sum Trip Price'].astype(str)
dfJourneys['Trip Sum Trip Price'] = dfJourneys['Trip Sum Trip Price'].str.replace('$','')
dfJourneys['Trip Sum Trip Price'] = dfJourneys['Trip Sum Trip Price'].str.replace(',','')
dfJourneys['Trip Sum Trip Price'] = dfJourneys['Trip Sum Trip Price'].astype(float)

dfJourneys.rename(columns = { 'Car Parking Address City':'city'
                             , 'Trip Start At Local Time':'journeyStartTime'
                             , 'Trip End At Local Time':'journeyEndTime'
                             , 'Trip Created At Local Time':'journeyCreationTime'
                             , 'Trip Sum Trip Price':'priceInDollar'
                            }, inplace = True)

dfJourneys['journeyDurationInHour'] = (dfJourneys.journeyEndTime - dfJourneys.journeyStartTime) / pd.Timedelta(hours=1)
dfJourneys['journeyDurationInHour'] = dfJourneys['journeyDurationInHour'].apply(np.int64)

dfJourneys['preBookingDurationInHour'] = (dfJourneys.journeyStartTime - dfJourneys.journeyCreationTime) / pd.Timedelta(hours=1)
dfJourneys['preBookingDurationInHour'] = dfJourneys['preBookingDurationInHour'].apply(np.int64)

dfJourneys.drop(dfJourneys.columns[[0, 1, 2, 5, 6]], axis = 1, inplace = True)

dfJourneys = dfJourneys[['city', 'journeyStartTime', 'journeyDurationInHour', 'preBookingDurationInHour', 'priceInDollar']]

dfJourneys['journeyStartHr'] = dfJourneys['journeyStartTime'].dt.hour
dfJourneys['journeyStartWeekday'] = dfJourneys['journeyStartTime'].dt.weekday
dfJourneys['journeyStartMonth'] = dfJourneys['journeyStartTime'].dt.month
dfJourneys.drop(dfJourneys.columns[[1]], axis = 1, inplace = True)


# detecting outliers
Q1 = np.percentile(dfJourneys['priceInDollar'], 25, interpolation = 'midpoint')
Q2 = np.percentile(dfJourneys['priceInDollar'], 50, interpolation = 'midpoint')  
Q3 = np.percentile(dfJourneys['priceInDollar'], 75, interpolation = 'midpoint')
IQR = Q3 - Q1
lowerLimit = Q1 - 1.5 * IQR
upperLimit = Q3 + 1.5 * IQR

# dropping outliers records
dfJourneys.drop(dfJourneys[(dfJourneys['priceInDollar'] > upperLimit) | (dfJourneys['priceInDollar'] < lowerLimit)].index, inplace = True)


# derving features
dfJourneys['isWeekend'] = dfJourneys.apply(lambda x: fn_is_weekend(x), axis=1)
dfJourneys['yearQuarter'] = dfJourneys.apply(lambda x: fn_get_year_quarters(x), axis=1)
dfJourneys['peakHours'] = dfJourneys.apply(lambda x: fn_get_peak_hours(x), axis=1)    
dfJourneys.drop(dfJourneys.columns[[4,5,6]], axis = 1, inplace = True)

dfDummies1 = pd.get_dummies(dfJourneys['city'])
dfDummies1.columns = [str(col).replace(" ", "") for col in dfDummies1.columns]
dfJourneys = pd.concat([dfJourneys, dfDummies1], axis=1)
dfJourneys.drop('city', axis=1, inplace=True)

dfDummies2 = pd.get_dummies(dfJourneys['yearQuarter'])
dfDummies2.columns = ['yearQuarter' + str(col) for col in dfDummies2.columns]
dfJourneys = pd.concat([dfJourneys, dfDummies2], axis=1)
dfJourneys.drop('yearQuarter', axis=1, inplace=True)

dfDummies3 = pd.get_dummies(dfJourneys['peakHours'])
dfDummies3.columns = [str(col) for col in dfDummies3.columns]
dfJourneys = pd.concat([dfJourneys, dfDummies3], axis=1)
dfJourneys.drop('peakHours', axis=1, inplace=True)


#Indentify X & y
X = dfJourneys.iloc[:, dfJourneys.columns != 'priceInDollar']
y = dfJourneys.iloc[:, 2]


# model
fit_RF = RandomForestRegressor(max_depth=9, n_estimators=15, random_state=0).fit(X,y)


# Saving model to disk
pickle.dump(fit_RF, open('model.pkl','wb'))

