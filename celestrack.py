'''
Created on Monday November 10, 2020

@author: Prudhviraj Tirumanisetti
'''

import os, ephem, requests, datetime, random, string, math
from  geopy.geocoders import Nominatim

# where the file is downloaded and reused
SOURCE = os.path.join(os.getcwd(),'Brightsatelites.txt')
# ReDownload the source text file again after the maximum retention in days
MAXIMUM_RETENTION = 1
RightAbove_SatAlt = 0
DEGREES_PER_RADIANS = 180.0/math.pi
ListofSateliteIDs = []


class FileLoader:

    global SOURCE

    global ListofSateliteIDs

    def open_file(self, flag, tupple=None):
       with open(SOURCE) as celestrackdata:
                self.last_modified = ephem.Date(datetime.datetime.strptime(celestrackdata.readline().strip()[7:],"%d %b %Y %H:%M:%S %Z"))
                return self.line_loader(celestrackdata, flag, tupple)

    def line_loader(self, file, flag, tupple):
        lines = [line.strip() for line in file]
        # print('------>'+lines[0]+lines[1]+lines[2]+'<----------')
        args = [iter(lines)] * 3
        if flag ==0:
            for name, line1, line2 in zip(*args):
                self[name] = ephem.readtle(name, line1, line2)
                ListofSateliteIDs.append(name)
        if flag ==1:
            Observer = ephem.Observer()
            Observer.lat, Observer.lon = self.get_user_Coordinates(tupple[0], tupple[1])
            Observer.date = tupple[2]
            RightAbove_SatAlt = 0
            global DEGREES_PER_RADIANS
            RightAbove_SatName, RightAbove_SatAz,RightAbove_SatRange,RightAbove_SatHeight = None, 0, 0, 0
            for name, line1, line2 in zip(*args):
                LoS= ephem.readtle(name, line1, line2)
                LoS.compute(Observer)
                if LoS.alt*DEGREES_PER_RADIANS >RightAbove_SatAlt:
                    RightAbove_SatAlt = LoS.alt*DEGREES_PER_RADIANS
                    RightAbove_SatName = LoS.name
                    RightAbove_SatAz = LoS.az
                    RightAbove_SatRange = LoS.range/1000
                    RightAbove_SatHeight = LoS.elevation/1000
                    FOUND = True
            return (tupple[0],tupple[1],RightAbove_SatName,RightAbove_SatAlt,RightAbove_SatAz, RightAbove_SatRange, RightAbove_SatHeight) if FOUND == True else (tupple[0],tupple[1],'There is No Satelite',0,0, 0, 0)
        if flag ==2:
            for name, line1, line2 in zip(*args):
                if tupple[2]==name:
                    RiseTime, AzumithRise, MaxAltitude, VISIBLE = self.pass_next_cal(tupple, name, line1, line2)
                    return RiseTime, AzumithRise, MaxAltitude, VISIBLE


class ResourceFile(dict, FileLoader):
    #URL --> From where the 100orso bright satelight data is downloaded
    URL = 'http://celestrak.com/NORAD/elements/visual.txt'
    LINE_END = '\r\n'

    global SOURCE

    def __init__(self):
        super().__init__()
        self.load()

    def __str__(self):
        return (
            "[{1:,}] "
            "{0.__class__.__name__} {0.last_modified}".format(
                self, len(self)))

    def load(self):
        self.clear()
        try:
            self.open_file(0)
        except FileNotFoundError:
            self.last_modified = 0

    def fetch(self):
        # Download the data and save it for later use; until the retention time
        try:
            data = requests.get(self.URL)
            if data.status_code == 200:
                with open(SOURCE, 'w') as celestrackdata:
                    celestrackdata.write('# {}{}'.format(
                        data.headers['Last-Modified'],self.LINE_END))
                    celestrackdata.write(data.text)
            return data.status_code == 200
        except requests.exceptions.RequestException as e:
            print("Unable to fetch the file from the internet with reuests %s as the error code" %(e))
        return False


class Compute_Satelite(FileLoader):

    global SOURCE

    def get_user_Coordinates(self, City, Country=None):
        # User agent is a random string to be passed to geopy to get the corordinates.
        UserAgent = ''.join(random.sample((string.ascii_letters)*9,9))
        Location_Agent = Nominatim(user_agent=UserAgent)
        if Country !=None:
            Location = Location_Agent.geocode(City+','+Country)
        else: Location = Location_Agent.geocode(City)
        return Location.latitude, Location.longitude

    def over_head(self, City, Country, User_Date):
        UserDetails = (City, Country, User_Date)
        Compute =self.open_file(1,UserDetails)
        return ('The Brighetest Satelight closest to directly overhead to observer on %s at %s,%s is %s \nThe Altitude of the satelite above the horizon is %4.1f in degrees \nThe Azmuith of the Satelight in clockwise from the north is %5.1f \nThe Distance of the Satelight from the current Observer is %.2f KMs \nThe Height of the satelight from the surface of the earth is %.2f kMs'%(User_Date, Compute[0], Compute[1], Compute[2], Compute[3],Compute[4],Compute[5], Compute[6]))

    def pass_next(self, City, Country, SateliteID):
        UserDetails=(City, Country, SateliteID)
        RiseTime, AzumithRise, MaxAltitude, VISIBLE  = self.open_file(2,UserDetails)
        return ('The %s Satelight is again visible on %s with rise azimuth of %s and the current visibility is %s (true visible, false not visible)' %(SateliteID,RiseTime, AzumithRise, VISIBLE))

    def pass_next_cal(self,UserDetails,Name, Line1, Line2):
        Observer = ephem.Observer()
        Observer.lat, Observer.lon = self.get_user_Coordinates(UserDetails[0], UserDetails[1])
        Observer.horizon = '-0:34'
        Observer.elevation = 2000
        LoS = ephem.readtle(Name, Line1, Line2)
        RiseTime, AzumithRise, MaxTime, MaxAltitude, SetTime, AzumithSet = Observer.next_pass(LoS)
        Observer.date = MaxTime
        global DEGREES_PER_RADIANS
        Sun = ephem.Sun()
        Sun.compute(Observer)
        LoS.compute(Observer)
        SunAltitude = Sun.alt*DEGREES_PER_RADIANS
        VISIBLE = False
        if -18 < SunAltitude < -6 and LoS.eclipsed is False:
            VISIBLE = True
        print(RiseTime, AzumithRise*DEGREES_PER_RADIANS, MaxAltitude*DEGREES_PER_RADIANS, VISIBLE)
        return RiseTime, AzumithRise*DEGREES_PER_RADIANS, MaxAltitude*DEGREES_PER_RADIANS, VISIBLE
