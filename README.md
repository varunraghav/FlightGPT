# ✈️ Airline Policy and Flight Query Chatbot: Program Overview

This program implements a chatbot system that combines **Retrieval-Augmented Generation (RAG)** and **API-based flight search** to answer user queries related to airline policies and flight availability. It processes user input to classify and respond appropriately, leveraging **LLMs**, **vector databases**, and external APIs.

---

## 🚀 Key Features

1. **Query Classification**:
   - Classifies user queries into three categories:
     - **RAG-Related**: Queries about travel policies (e.g., luggage rules, traveling with pets, etc.).
     - **API-Related**: Questions requiring live flight information (e.g., cheapest flights, flight performance).
     - **General**: Queries outside the chatbot's scope.

2. **Policy Retrieval**:
   - Uses **LLamaIndex** with **ChromaDB** as the vector store for retrieving policy documents.
   - Handles both specific airline queries and general ones using metadata filtering.

3. **Flight Search**:
   - Supports various flight queries via APIs, including:
     - Flight availability between two cities.
     - Cheapest flight offers.
     - Performance of specific airports.

4. **Adaptive Query Engine**:
   - Dynamically configures the query engine based on the classification of the input (e.g., specific airline queries use metadata filtering).

5. **Multimodal Input Handling**:
   - Accepts free text from the user and extracts structured information (e.g., origin, destination, and date) using LLMs.
---

## Present Flow:

1. **Main**
2. **Create RAG Index**
   - Define the index, vector store, and retriever while providing metadata.
   - Current metadata includes:
     - Bag, pets, and sports equipment policies of 3 airlines: 
       - American Airlines
       - Delta Airlines
       - United Airlines
3. **Prompt Handling**
   - Continuously asks for user input until the user says `exit`, `quit`, or `bye` (currently hard-coded, can be enhanced with LLM).
4. **Query Classification**
   - **RAG Query**:
     1. Call `create_prompt`.
     2. Execute `classify_rag_query` to determine the relevant metadata.
     3. Build the query using the RAG output.
     4. Return the result.
   - **API-Related Query**:
     1. Classify the type of API call required:
        - Call `FlightAvailBtwCities` for flights between two cities on a specific date.
        - Call `FlightInspirationSearch` for the cheapest flights from a location.
        - Call `FlightOffersSearch` for the cheapest flights between two cities.
   - **Other Queries**:
     - Return a response indicating the chatbot cannot answer the question.

---

## Questions Answered:

### 1. FlightAvailBtwCities

#### Handles Questions:
   - Flights between two cities on a specific day.
   - Number of seats available on a flight between two cities.
   - Filtering based on:
     - Fastest flights.
     - Flights below a specific duration.
     - Non-stop flights.
     - Time of day (may be ambiguous).
     - Avoiding particular layovers (e.g., country-based).
     - Avoiding or preferring specific carriers.

#### Issues:
   - `number_of_stops` always returns 0. Needs adjustment to reflect duration.
   - Multiple flights are represented as a second instance of a segment.

---

### 2. FlightInspirationSearch

#### Handles Questions:
   - Cheapest flights from a specific location within a date range.
   - Flights based on a budget (e.g., "My budget is $10,000. What are the cheapest flights?").
   - Calls `AirlineCodeLookup` for comprehensive answers.

#### Notes:
   - `ViewBy = Date` fetches more options when explicitly mentioned, even though it's a default parameter.

#### Follow-Up Questions:
   - "What are the rates?"

#### Limitations:
   - Location filtering is not available in the input.
   - Does not answer "Cheapest flight between two locations" (use `FlightOffersSearch` for this).

---

### 3. FlightOffersSearch

#### Handles Questions:
   - Cheapest flights between two cities (sorted by price).
   - Filters for:
     - Airlines (include or exclude).
     - Class (ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST).
     - Non-stop flights (not working currently).
     - Maximum price per traveler.

#### Notes:
   - Only single-date queries are allowed; multi-query is required for multiple dates.
   - Provide just the cheapest option or ask follow-up questions for clarity if input is minimal.

#### Filters in Output:
   - Departure and arrival times.

---

## Summary of Issues:

- `number_of_stops` in `FlightAvailBtwCities` is returning 0 universally.
- Non-stop filter in `FlightOffersSearch` is currently non-functional.
- Location filtering in `FlightInspirationSearch` is absent.
- Multi-date queries require multiple function calls.

---
