# FlightGPT
Trying to build a chatbot that answers your questions about flights.

Present Flow:

1. Main
2. Create RAG index, by defining index , vector store and retriever and giving metadata.
    a. Bag, pets, sports equipment policy of 3 airlines - American Airlines, Delta Airlines, United Airlines uploaded so far.
3. Ask for prompt till it says exit/quit/bye(hard-coded now, can be LLMised)
4. classify query:
    a. If RAG:
        1. call create_prompt.
        2. This calls classify_rag_query which determines the metadata
        3. Now build the query using output from RAG
        3. Now return it.
    b. If API related:
        1. Classify which API call can answer this query.
            a. Call FlightAvailBtwCities if 1(flights b/w 2 cities on particular date)
            b. Call FlightInspirationSearch if 2(cheapest flight from particular location)
            c. Call FlightOffersSearch if scenario 3(cheapest flight b/w 2 cities)
    c. Else return that the chatbot cannot answer the question

Questions Answered:

1. FlightAvailBtwCities will answer these questions
    a. Flights between 2 cities on a particular day 
    Issues:
        a. number_of_stops doesn't seem to be working. Returning 0 universally. 
        Need to return based on duration.
        b. Multiple flights are represented as second instance of segment.
    b. Number of seats in flight between 2 cities()
    c. Filter can be done by asking these questions(basically text-to-SQL) on Output(not input).
        1. Return me the fastest flights.
        2. Return flights less than 
        3. Return me only non-stop flights
        4. Return me (time of the day) flights( which could be ambigious)
        5. Avoiding a particular layover(which might be country based) - call AirlineCodeLook.py
        6. Avoiding or preferring a particular carrier
2. FlightInspirationSearch will answer this question.
    a. What is the cheapest flights from Delhi between these days?(no on these days)
        Need to call AirlineCodeLookup for full answer
    b. My budget is 10,000. What are the cheapest flight on dates or between dates?
        If on random dates like Feb 9, Feb 22, need to call this function multiple times.
    c. Location filter is not there in input.
        Cheapest flight between 2 locations IS NOT ANSWERED IN THIS QUESTION. REFER NEXT
    d. Notes:
        ViewBy = Date fetches more option when mentioned even though it's default
    e. Followup-Questions:
        What are the rates
3. FlightOffersSearch will answer this question:
    a. What are the cheapest flight between these 2 cities, sorted by cheapest first?
    b. Multiple dates are not allowed, so multi-query is needed if multiple questions asked at once.
    c. Entering just the mandatory values could result in overload, so return just the cheapest one or ask further questions.
    d. Filter in input:
        Airlines(include and exclude)
        Class - ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST
        nonStop - or not? # Not working now
        maxPrice per trraveller
    e. Filter in output:
        Departure and arrival time basis


    





