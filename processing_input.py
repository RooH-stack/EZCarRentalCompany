import pendulum
import pandas as pd

def fn_is_weekend(journeyStartWeekday):
    if ((journeyStartWeekday == 5) | (journeyStartWeekday == 6)):
        return 1
    else:
        return 0

def fn_get_year_quarters(journeyStartMonth):
    if ((journeyStartMonth >= 0) & (journeyStartMonth <= 2)):
        return 1
    elif ((journeyStartMonth >= 3) & (journeyStartMonth <= 5)):
        return 2
    elif ((journeyStartMonth >= 6) & (journeyStartMonth <= 8)):
        return 3
    else:
        return 4

def fn_get_peak_hours(journeyStartHr):
    if ((journeyStartHr >= 21) & (journeyStartHr <= 5)):
        return 'nightHours'
    elif ((journeyStartHr == 6) | (journeyStartHr == 7)):
        return 'morningNonPeakHours'
    elif ((journeyStartHr >= 8) & (journeyStartHr <= 13)):
        return 'morningPeakHours'
    elif ((journeyStartHr >= 14) & (journeyStartHr <= 17)):
        return 'eveningPeakHours'
    else:
        return 'eveningNonPeakHours'

def process_data(input):
    
    #input = ['San Francisco', '2021-06-11', '13:51', '12']

    timeZones = {'San Francisco':'PST8PDT', 'Boston':'EST5EDT', 'Oakland':'PST8PDT', 'Washington':'PST8PDT', 'Chicago':'CST6CDT',
        'Berkeley':'PST8PDT', 'Daly City':'PST8PDT', 'Cambridge':'Etc/GMT+1', 'San Bruno':'PST8PDT', 'Brookline':'EST5EDT',
        'San Mateo':'PST8PDT', 'Hayward':'PST8PDT', 'Arlington':'CST6CDT'}

    df = pd.DataFrame(columns=['journeyDurationInHour', 'preBookingDurationInHour', 'isWeekend', \
        'Arlington', 'Berkeley', 'Boston', 'Brookline', 'Cambridge', 'Chicago', \
        'DalyCity', 'Hayward', 'Oakland', 'SanBruno', 'SanFrancisco', \
        'SanMateo', 'Washington', 'yearQuarter1', 'yearQuarter2', \
        'yearQuarter3', 'yearQuarter4', 'nightHours', 'eveningNonPeakHours', 'eveningPeakHours', \
        'morningNonPeakHours', 'morningPeakHours'])

    inputCity = input[0]
    inputJourneyStartDate = input[1]
    inputJourneyStartTime = input[2]+':00'
    inputjourneyDurationInHour = input[3]

    print(inputCity, inputJourneyStartDate, inputJourneyStartTime, inputjourneyDurationInHour)

    localTimeZone = timeZones.get(inputCity)
    journeyCreationTime = pd.to_datetime(pendulum.now(localTimeZone).format('YYYY-MM-DD HH:mm:ss'))
    inputJourneyStartTime = pd.to_datetime(inputJourneyStartDate + ' ' + inputJourneyStartTime, format="%Y/%m/%d %H:%M:%S")
    preBookingDurationInHour = int((inputJourneyStartTime - journeyCreationTime) / pd.Timedelta(hours=1))
    df['journeyDurationInHour'] = [inputjourneyDurationInHour]
    df['preBookingDurationInHour'] = [preBookingDurationInHour]
    df[inputCity.replace(" ", "")] = 1
    df['isWeekend'] = fn_is_weekend(inputJourneyStartTime.dayofweek)
    yearQuarterVar = fn_get_year_quarters(inputJourneyStartTime.month)
    df['yearQuarter' + str(yearQuarterVar)] = 1
    peakHoursVar = fn_get_peak_hours(inputJourneyStartTime.hour)
    df[peakHoursVar] = 1

    df = df.fillna(0)

    return df