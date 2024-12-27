from amadeus import Client, ResponseError
import os
from dotenv import load_dotenv
from autogen import ConversableAgent  # Import LLM agent

load_dotenv()

# Amadeus API credentials
api_key = os.getenv("AMADEUS_API_KEY")
api_secret = os.getenv("AMADEUS_SECRET")
amadeus = Client(client_id=api_key, client_secret=api_secret)

# LLM Agent Configuration
llm_agent = ConversableAgent(
    name="AirportAgent",
    system_message="You are an LLM assistant specialized in handling airport-related queries.",
    llm_config={
        "config_list": [{"model": "gpt-4o-mini", "api_key": os.getenv("OPENAI_API_KEY")}]
    },
    code_execution_config=False,
    human_input_mode="NEVER",
)

def fetch_airport_code_with_llm(location_name):
    """
    Use the LLM agent to fetch the airport code for a given location name.
    """
    prompt = f"""
    Your Task: Provide the IATA airport code for the following location name.

    Location: "{location_name}"

    Guidelines:
    - Search online for the most common or closest airport to the provided location.
    - Return only the 3-letter IATA code.
    - If multiple airports exist, return the main international airport.
    - If the location is invalid or ambiguous, respond with 'Unknown'.
    """
    response = llm_agent.generate_reply(messages=[{"content": prompt, "role": "user"}])
    return response.strip()

def get_on_time_performance(airport_code, date):
    """
    Fetch on-time performance data for a specific airport and date.
    """
    try:
        response = amadeus.airport.predictions.on_time.get(airportCode=airport_code, date=date)
        return response.data
    except ResponseError as error:
        return {"error": str(error)}

def process_airport_query(user_query):
    """
    Parse user query for airport-related details, fetch airport code if needed,
    and get on-time performance data.
    """
    #print("User was here at process airport")
    # Example user query: "Will there be delays at JFK on 2024-12-21?"
    location, date = None, None

    # Basic extraction of location and date (can use NLP for robustness)
    if "at" in user_query:
        location = user_query.split("at")[1].split()[0]
    if "on" in user_query:
        date = user_query.split("on")[1].split()[0]

    # Check if location is a code or name
    if location and len(location) != 3:
        location = fetch_airport_code_with_llm(location)  # Use LLM agent for lookup

    if not location or location == "Unknown":
        location = input("Sorry, I couldn't determine the airport code. Please provide a valid location. ").strip().upper()
        location = fetch_airport_code_with_llm(location)

    #print(location)

    if not date:
        date = input("Please provide a valid date in the format YYYY-MM-DD.").strip()

    print(date)

    # Get on-time performance data
    performance_data = get_on_time_performance(location, date)
    #print(f"API Response: {performance_data}")  # Debugging: Print the full response

    if "error" in performance_data:
        return f"Error fetching performance data: {performance_data['error']}"

        # Extract performance metrics using proper parsing

    on_time_result = float(performance_data.get('result', 'Unknown')) * 100  # Convert result to percentage
    prediction_accuracy = float(performance_data.get('probability', 'Unknown')) * 100  # Convert probability to percentage
    #print(on_time_result)
    #print(prediction_accuracy)

    # Format and return the response
    response = f"On-Time Performance for {location} on {date}:\n"
    response += f"Predicted On-Time Percentage: {on_time_result:.2f}%\n"
    response += f"Prediction Accuracy: {prediction_accuracy:.2f}%\n"

    return response

#Common Errors
# e issue lies in the use of double quotes (") inside a string that is already enclosed in double quotes ("). 
# This causes a syntax error because Python gets confused about where the string ends.

