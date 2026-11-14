import os
import sys

# Add the main project folder to Python's path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import app


def test_home_page_loads():
    response = app.test_client().get("/")
    assert response.status_code == 200