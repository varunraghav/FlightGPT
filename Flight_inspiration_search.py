from amadeus import Client, ResponseError
import os
import requests
from dotenv import load_dotenv
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

def find_cheapest_places(origin, departure_date_range, one_way=None, max_price=None, view_by="WEEK"):
    """
    Finds the cheapest places to fly from a given origin.

    :param origin: str - IATA code of the city from which the flight will depart (mandatory)
    :param departure_date_range: str - ISO 8601 date range (e.g., '2025-02-01,2025-02-10') (mandatory)
    :param one_way: bool - Whether to search for one-way flights (optional)
    :param max_price: int - Maximum price for the flights (optional)
    :param view_by: str - View results by DESTINATION, DATE, etc. (optional)
    :return: list of dictionaries containing flight information
    """
    try:
        params = {
            "origin": origin,
            "departureDate": departure_date_range
        }
        if one_way is not None:
            params["oneWay"] = one_way
        if max_price is not None:
            params["maxPrice"] = max_price
        if view_by is not None or view_by == "WEEK":
            params["viewBy"] = view_by

        response = amadeus.shopping.flight_destinations.get(**params)
        return response.data
    except ResponseError as error:
        print(f"Error: {error}")
        return []

def fetch_additional_flight_data(link, access_token):
    """
    Fetches additional flight data from a given API link.

    :param link: str - URL to the API endpoint
    :param access_token: str - Bearer token for authorization
    :return: dict containing flight data or None if an error occurs
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching additional data: {response.status_code} - {response.text}")
        return None

def process_flight_data(flight_data):
    """
    Processes and prints flight data in a user-friendly format.

    :param flight_data: list of dictionaries containing flight information
    """
    for place in flight_data:
        print(f"Destination: {place.get('destination')}")
        print(f"Departure Date: {place.get('departureDate')}")
        print(f"Price: {place.get('price', {}).get('total')} INR")
        print("-" * 40)

        links = place.get("links", {})
        if "flightDates" in links:
            print(f"Flight Dates URL: {links['flightDates']}")
        if "flightOffers" in links:
            print(f"Flight Offers URL: {links['flightOffers']}")

def get_access_token():
    """
    Retrieves the current access token from the Amadeus client.

    :return: str - Access token
    """
    return amadeus.access_token.access_token

def get_user_input_with_llm(query):
    """
    Use an LLM agent to extract or confirm the required input values from the user.

    :param query: str - The user's input query
    :return: dict - Contains confirmed input parameters (origin, departure_date_range, one_way, max_price)
    """
    prompt_template = PromptTemplate(
        input_variables=["query"],
        template=(
            "User query: {query}\n"
            "Extract and confirm the following details: \n"
            "1. Origin city (convert to IATA code if necessary). \n"
            "2. Departure date range in ISO format (e.g., YYYY-MM-DD,YYYY-MM-DD). \n"
            "3. Whether the user wants a one-way trip (yes/no). \n"
            "4. Maximum price (optional). \n"
            "Provide the extracted details in JSON format."
        )
    )
    prompt = prompt_template.format(query=query)
    response = llm(prompt)

    try:
        extracted_data = eval(response.strip())  # Ensure the response is a valid Python dictionary
        return extracted_data
    except Exception as e:
        print(f"Error parsing LLM response: {e}")
        return {
            "origin": None,
            "departure_date_range": None,
            "one_way": None,
            "max_price": None
        }
