#the code requires openpyxl to open the excel --> pip install openpyxl
import numpy as np
import pandas as pd
import math

# Import data
raw_data = pd.read_excel(r"worldcities.xlsx")
df = pd.DataFrame(raw_data, columns=["id", "city", "lat", "lng", "iso3", "population"])  #keep only relevant columns

# Data preprocessing (rename "city" --> "name", lng London = 0, all longitudes from London)
df.rename(columns={"city":"name"}, inplace=True) #to avoid confusion, the name of the city will be "name" and not "city"
df["lng"] = df["lng"] + 0.1275 #this is just to have London's lng at zero (and change all the others accordingly), which makes the next step easier
df["lng"] = np.where(df["lng"] < 0, df["lng"] + 360, df["lng"]) #I change "negative" (i.e. West) lngs to positive, so that the journey eastward can proceed with ever higher values of lng

# Define class: City
class City:
    def __init__(self, id: int, name: str, lat: float, lng: float, iso3: str, pop: float):
        self.id = id
        self.name = name
        self.lat = lat
        self.lng = lng
        self.iso3 = iso3
        self.population = pop

    def __repr__(self):
        return f"id {self.id}, {self.name}, {self.iso3}, lat {self.lat}, lng {self.lng}, pop {self.population}"

# set the function to compute the distance between two points on a spheric surface (haversine)
def spheric_distance(lat1, lng1, lat2, lng2):
    R = 6371  # Earth's radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c  
    return distance

# Create a list of Cities from the df
citylist = [City(*row) for row in df.values]

# set the function to find the three closest cities to the east (i.e. with higher lng value)
def find_closest_cities(city, citylist):
    distances = []
    for other_city in citylist:
        if other_city.lng > city.lng:
            distance = spheric_distance(city.lat, city.lng, other_city.lat, other_city.lng)
            distances.append((distance, other_city)) #the list is populated with couples distance-destination
    distances.sort(key=lambda x: x[0]) #sort the cities by distance (the first attribute), as calculated with the spheric distance function
    return distances[:3] #get the closest three by slicing the list

# calculate the travel time, taking into account the problem's rules
def calculate_travel_time(start_city, end_city, rank):
    time = 2 if rank == 1 else 4 if rank == 2 else 8 #baseline time depends on the position of the destination
    if start_city.iso3 != end_city.iso3: #+2 h if the city is in another country
        time += 2
    if end_city.population > 200000: #+2 h if the city has more than 200.000 citizens
        time += 2
    return time

# Define class: Trip
class Trip:
    def __init__(self, start_city, citylist):
        self.start_city = start_city
        self.citylist = citylist
        self.path = [start_city] #defines the path (which will be printed at the end) as a list of all the starting cities
        self.total_time = 0 

    def travel(self): #define the method to actually travel. 
        #NB the code ALWAYS gets the closest city, because after testing I saw that, since the cities are so many and so close to each other, using the closest one makes sense to avoid exceeding the maximum time allowed.
        current_city = self.start_city #set the starting city as the "current" city
        while True:
            closest_cities = find_closest_cities(current_city, self.citylist)
            if not closest_cities: #check if the list of closest cities is empty, if it is the cycle breaks
                break
            for rank in range(1, len(closest_cities) + 1): #if it is not empty, the cycle starts
                (distance, next_city) = closest_cities[rank - 1] #select the first tuple
                travel_time = calculate_travel_time(current_city, next_city, rank)
                self.total_time += travel_time #update the total time
                self.path.append(next_city) #update the path log
                current_city = next_city #update the current city
                break  #the cycle does not repeat after the first city
            if current_city == self.start_city:
                break  #the cycle interrupts when the current city becomes the original one

    def can_complete_in_80_days(self):
        return self.total_time <= 80 * 24  # check if total hours is less than 1920

# set London as first starting city
london = City(1826645935, "London", 51.5072, 0, "GBR", 10979000)

# execute the trip
trip = Trip(london, citylist)
trip.travel()

# print the route
for city in trip.path:
    print(city)

# check whether the total is under 80 days and print the total time
if trip.can_complete_in_80_days():
    print("È possibile fare il giro del mondo in 80 giorni partendo da Londra.")
else:
    print("Non è possibile fare il giro del mondo in 80 giorni partendo da Londra.")
print(f"Tempo totale di viaggio: {trip.total_time / 24:.2f} giorni")