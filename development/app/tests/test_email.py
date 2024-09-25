# tests/test_email.py

from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)

@patch('app.main.send_email')  # Mock the send_email function
def test_send_email(mock_send_email):
    mock_send_email.return_value = None  # Assume send_email returns None or does nothing

    response = client.post(
        "/send-email/",
        json={
            "mail_from": "luispedrotrinta.1998@gmail.com",
            "mail_to": "luis.pedro_1998@hotmail.com",
            "subject": "Test Email Subject222",
            "message": "This is a test email message."
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Email has been sent"
