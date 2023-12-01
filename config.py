# The main assistant prompt
assistant_instructions = """
    This assistant is designed to assist users with real estate inquiries, offering valuable information and services while also capturing potential lead details for follow-up.

    Key Functions and Approach:

    1. Property Search Assistance:
       - When users express interest in finding properties, engage them by asking about their budget, preferred location, and type of property (e.g., apartment, house).
       - Utilize the 'property_search' tool to provide a list of properties that match their criteria.
       - Focus on delivering value by offering detailed information about each property and answering any specific questions they may have.

    2. Scheduling Property Viewings:
       - If a user shows interest in a specific property, offer to schedule a viewing.
       - Collect necessary details such as the property ID, their preferred viewing date and time, and their email address using the 'schedule_viewing' tool.
       - Confirm the viewing appointment and provide them with a summary of the scheduled viewing details.

    3. Lead Capture:
       - Throughout the interaction, if the user seems engaged and interested, gently transition into capturing their contact details.
       - Use the 'create_lead' tool to record their name, phone number, email, and property preferences.
       - Assure the user that their information will be used to provide them with tailored information and updates.

    Interaction Guidelines:
       - Maintain a friendly, professional, and helpful tone.
       - Offer clear, concise, and relevant information to build trust and rapport.
       - If the user's needs exceed the assistant's capabilities, suggest contacting a human representative for more personalized assistance.
       - Aim to provide a seamless and positive experience, encouraging users to leave their contact details for further engagement.

    Remember, the goal is to be as helpful as possible, providing value in each interaction, which naturally leads to the opportunity to capture lead information.
"""

# Define the tools and their configurations
schedule_viewing_tool = {
    "type": "function",
    "function": {
        "name": "schedule_viewing",
        "description":
        "Schedule a property viewing based on user preferences.",
        "parameters": {
            "type": "object",
            "properties": {
                "property_id": {
                    "type":
                    "integer",
                    "description":
                    "The ID of the property to schedule a viewing for."
                },
                "desired_date": {
                    "type":
                    "string",
                    "description":
                    "The desired date for the viewing in 'YYYY-MM-DD' format."
                },
                "desired_time": {
                    "type":
                    "string",
                    "description":
                    "The desired time for the viewing in 'HH:MM' format."
                },
                "email": {
                    "type":
                    "string",
                    "description":
                    "Email address of the user for confirmation and further communication."
                }
            },
            "required":
            ["property_id", "desired_date", "desired_time", "email"]
        }
    }
}

# Define the tools and their configurations
contact_tool = {
    "type": "function",
    "function": {
        "name": "contact_us",
        "description":
        "Schedule a property viewing based on user preferences.",
        "parameters": {
            "type": "object",
            "properties": {
                "property_id": {
                    "type":
                    "integer",
                    "description":
                    "The ID of the property to schedule a viewing for."
                },
                "desired_date": {
                    "type":
                    "string",
                    "description":
                    "The desired date for the viewing in 'YYYY-MM-DD' format."
                },
                "desired_time": {
                    "type":
                    "string",
                    "description":
                    "The desired time for the viewing in 'HH:MM' format."
                },
                "email": {
                    "type":
                    "string",
                    "description":
                    "Email address of the user for confirmation and further communication."
                }
            },
            "required":
            ["property_id", "desired_date", "desired_time", "email"]
        }
    }
}

create_lead_tool = {
    "type": "function",
    "function": {
        "name": "create_lead",
        "description": "Capture lead details and save to CRM.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the lead."
                },
                "phone": {
                    "type": "string",
                    "description": "Phone number of the lead."
                },
                "email": {
                    "type": "string",
                    "description": "Email address of the lead."
                },
                "property_preferences": {
                    "type": "string",
                    "description":
                    "Details of the lead's property preferences."
                }
            },
            "required": ["name", "phone", "email", "property_preferences"]
        }
    }
}

property_search_tool = {
    "type": "function",
    "function": {
        "name": "property_search",
        "description": "Search for properties based on user preferences.",
        "parameters": {
            "type": "object",
            "properties": {
                "budget": {
                    "type": "integer",
                    "description": "Budget for the property search."
                },
                "location": {
                    "type": "string",
                    "description": "Preferred location for the property."
                },
                "property_type": {
                    "type": "string",
                    "description": "Type of property (e.g., apartment, house)."
                }
            },
            "required": ["budget", "location", "property_type"]
        }
    }
}
