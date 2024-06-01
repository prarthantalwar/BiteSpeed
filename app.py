from flask import Flask, request, jsonify
from services import ContactService
from models import create_tables

# Initialize the Flask application
app = Flask(__name__)

# Initialize the ContactService instance
contact_service = ContactService()

# Create database tables if they do not exist
create_tables()


# Define a route to handle the '/identify' endpoint with POST method
@app.route("/identify", methods=["POST"])
def identify():
    # Get JSON data from the request
    data = request.get_json()

    # Extract email and phone number from the request data
    email = data.get("email")
    phoneNumber = data.get("phoneNumber")

    # If neither email nor phone number is provided, return an error response
    if not email and not phoneNumber:
        return jsonify({"error": "Email or phone number required"}), 400

    # Call the identify_contact method of the contact_service to process the data
    response = contact_service.identify_contact(email, phoneNumber)

    # Return the response as JSON with a status code of 200 (OK)
    return jsonify(response), 200


# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)  # Run the app in debug mode for development
