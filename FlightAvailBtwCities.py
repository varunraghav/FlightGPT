# Install the Python library from https://pypi.org/project/amadeus
'''
This program looks for flights between 2 city 
In this program, we are manually inputting in
1. City code both arrival and destination
2. Departure Date
3. Number of passengers in GET request

Output has 
1. Number of stops
2. departure, arrival time and separate duration(which doesn't seem to be working)
'''

from amadeus import Client, ResponseError
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Amadeus client
amadeus = Client(
    client_id=os.environ["AMADEUS_API_KEY"],
    client_secret=os.environ["AMADEUS_SECRET"]
)

def get_flight_availability(origin, destination, date, traveler_type="ADULT"):
    try:
        body = {
            "originDestinations": [
                {
                    "id": "1",
                    "originLocationCode": origin,
                    "destinationLocationCode": destination,
                    "departureDateTime": {"date": date},
                }
            ],
            "travelers": [{"id": "1", "travelerType": traveler_type}],
            "sources": ["GDS"]
        }

        response = amadeus.shopping.availability.flight_availabilities.post(body)
        flight_data = []
        for flight in response.data:
            duration = flight.get("duration", "Unknown")
            segments = flight.get("segments", [])
            for segment in segments:
                flight_data.append({
                    "duration": duration,
                    "number_of_stops": segment.get("numberOfStops", "Unknown"),
                    "departure_time": segment.get("departure", {}).get("at", "Unknown"),
                    "arrival_time": segment.get("arrival", {}).get("at", "Unknown"),
                })
        return flight_data
    except ResponseError as error:
        return {"error": str(error)}
