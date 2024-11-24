# Initialize the Groq client
import os
from groq import Groq


def detect_intent_with_groq(client, user_query):
    llama_prompt = f"""
    The user will ask questions or provide commands. Identify whether the query requires filling out a contact form or answering a question. Respond with "contact_form" for form-related queries and "informational" for others. Do NOT OUTPuT anything else.

    Example 1:
    Query: Fill out the contact form.
    Response: contact_form

    Example 2:
    Query: What is the capital of France?
    Response: informational

    Example 3:
    Query: Submit my message on the contact us page.
    Response: contact_form

    Example 4:
    Query: Please send my details through the website form.
    Response: contact_form

    Query: {user_query}
    Response:
    """
    
    # Use Groq to interact with the Llama model
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": llama_prompt,
            }
        ],
        model="llama3-8b-8192",  # Specify the Llama model being used
    )
    
    # Extract the model's response and normalize it
    intent = chat_completion.choices[0].message.content.strip().lower()
    print(intent)
    return intent


GROQ_API_KEY = "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"

client = Groq(
    api_key=GROQ_API_KEY,
)

# Example user query
user_query = "Can you fill the contact us form for me?"

# Detect intent
intent = detect_intent_with_groq(client, user_query)

# Handle the detected intent
if intent == "contact_form":
    print("Detected intent to fill out the contact form. Proceeding to Step 2...")
    # Path to the scraped contact page
    contact_page_path = "contact_page.txt"
    # Step 2.1: Extract fields
    fields = extract_fields_from_contact_page(client, contact_page_path)
    print("Identified Fields:", fields)
    # Proceed to gather user information
elif intent == "informational":
    print("Detected informational query. Passing to Q&A pipeline.")
    # Use Llama for the normal Q&A pipeline
else:
    print(f"Unrecognized intent: {intent}. Unable to process the query.")
