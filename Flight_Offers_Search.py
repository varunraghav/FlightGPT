from amadeus import Client, ResponseError
from dotenv import load_dotenv
import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# Initialize Amadeus API client
api_key = os.getenv("AMADEUS_API_KEY")
api_secret = os.getenv("AMADEUS_SECRET")
amadeus = Client(client_id=api_key, client_secret=api_secret)

# Initialize LLM agent
llm = ChatOpenAI(temperature=0.7)

def find_cheapest_flights(origin, destination, departure_date, return_date=None, travel_class="ECONOMY", adults=1, max_results=3):
    """
    Finds the cheapest flights between two locations.

    :param origin: str - IATA code of the city of origin (mandatory)
    :param destination: str - IATA code of the city of destination (mandatory)
    :param departure_date: str - Departure date in ISO format (YYYY-MM-DD) (mandatory)
    :param return_date: str - Return date in ISO format (YYYY-MM-DD) (optional)
    :param travel_class: str - Travel class (ECONOMY, BUSINESS, etc.) (optional, default: ECONOMY)
    :param adults: int - Number of adult passengers (optional, default: 1)
    :param max_results: int - Maximum number of flight offers to return (optional, default: 3)
    :return: list of dictionaries containing flight information
    """
    try:
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "adults": adults,
            "max": max_results,
            "travelClass": travel_class
        }

        if return_date:
            params["returnDate"] = return_date

        response = amadeus.shopping.flight_offers_search.get(**params)
        flights = []
        for flight in response.data:
            flight_details = {
                "id": flight.get("id", "Unknown"),
                "source": flight.get("source", "Unknown"),
                "numberOfSeats": flight.get("numberOfBookableSeats", "Unknown"),
                "price": flight.get("price", {}).get("total", "Unknown"),
                "currency": flight.get("price", {}).get("currency", "Unknown"),
                "itineraries": []
            }

            for itinerary in flight.get("itineraries", []):
                itinerary_details = {
                    "duration": itinerary.get("duration", "Unknown"),
                    "segments": []
                }

                for segment in itinerary.get("segments", []):
                    segment_details = {
                        "departure": segment.get("departure", {}).get("iataCode", "Unknown"),
                        "arrival": segment.get("arrival", {}).get("iataCode", "Unknown"),
                        "carrier": segment.get("carrierCode", "Unknown"),
                        "flightNumber": segment.get("number", "Unknown"),
                        "aircraft": segment.get("aircraft", {}).get("code", "Unknown"),
                        "departureTime": segment.get("departure", {}).get("at", "Unknown"),
                        "arrivalTime": segment.get("arrival", {}).get("at", "Unknown"),
                        "duration": segment.get("duration", "Unknown")
                    }
                    itinerary_details["segments"].append(segment_details)

                flight_details["itineraries"].append(itinerary_details)

            flights.append(flight_details)

        return flights

    except ResponseError as error:
        print(f"Error: {error}")
        return []

def process_flight_offers(flights):
    """
    Processes and prints flight offer data in a user-friendly format.

    :param flights: list of dictionaries containing flight information
    """
    for flight in flights:
        print(f"Flight ID: {flight['id']}, Price: {flight['price']} {flight['currency']}")
        for itinerary in flight["itineraries"]:
            print(f"  Itinerary Duration: {itinerary['duration']}")
            for segment in itinerary["segments"]:
                print(f"    Segment: {segment['departure']} -> {segment['arrival']}")
                print(f"      Carrier: {segment['carrier']}, Flight Number: {segment['flightNumber']}")
                print(f"      Departure Time: {segment['departureTime']}, Arrival Time: {segment['arrivalTime']}")
                print(f"      Duration: {segment['duration']}, Aircraft: {segment['aircraft']}")

def get_user_input_with_llm(user_query):
    """
    Use an LLM agent to extract or confirm the required input values from the user.

    :param user_query: str - The user's input query
    :return: dict - Contains confirmed input parameters (origin, destination, departure_date, return_date, travel_class, adults, max_results)
    """
    prompt_template = PromptTemplate(
        input_variables=["user_query"],
        template=(
            "User query: {user_query}\n"
            "Extract and confirm the following details: \n"
            "1. Origin city (convert to IATA code if necessary). \n"
            "2. Destination city (convert to IATA code if necessary). \n"
            "3. Departure date in ISO format (e.g., YYYY-MM-DD). \n"
            "4. Return date in ISO format (optional). \n"
            "5. Travel class (e.g., ECONOMY, BUSINESS). \n"
            "6. Number of adults. \n"
            "7. Maximum results to return. \n"
            "Provide the extracted details in JSON format."
        )
    )
    prompt = prompt_template.format(user_query=user_query)
    response = llm(prompt)

    try:
        extracted_data = eval(response.strip())  # Ensure the response is a valid Python dictionary
        return extracted_data
    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        return {
            "origin": None,
            "destination": None,
            "departure_date": None,
            "return_date": None,
            "travel_class": "ECONOMY",
            "adults": 1,
            "max_results": 3
        }

def get_flight_offers_via_query(user_query):
    """
    Handles the user query to fetch and process flight offers.

    :param user_query: str - The user's input query
    """
    user_inputs = get_user_input_with_llm(user_query)

    origin = user_inputs.get("origin")
    destination = user_inputs.get("destination")
    departure_date = user_inputs.get("departure_date")
    return_date = user_inputs.get("return_date")
    travel_class = user_inputs.get("travel_class", "ECONOMY")
    adults = user_inputs.get("adults", 1)
    max_results = user_inputs.get("max_results", 3)

    if not origin or not destination or not departure_date:
        print("Unable to extract mandatory details. Please try again.")
        return

    flights = find_cheapest_flights(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        return_date=return_date,
        travel_class=travel_class,
        adults=adults,
        max_results=max_results
    )

    process_flight_offers(flights)
