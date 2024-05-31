from flask import Flask, request, jsonify
from services import ContactService
from models import create_tables

app = Flask(__name__)
contact_service = ContactService()
create_tables()


@app.route("/identify", methods=["POST"])
def identify():
    data = request.get_json()
    email = data.get("email")
    phoneNumber = data.get("phoneNumber")

    if not email and not phoneNumber:
        return jsonify({"error": "Email or phone number required"}), 400

    response = contact_service.identify_contact(email, phoneNumber)
    return jsonify(response), 200


if __name__ == "__main__":
    app.run(debug=True)
