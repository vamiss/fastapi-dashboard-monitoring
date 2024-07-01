import pytest
from fastapi.testclient import TestClient
from .main import app
from .security import pwd_context, HASHED_USERNAME, HASHED_PASSWORD
import psutil
from .monitor import update_df, df

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    expected_message = "You're in the root FastAPI's directory. It is now ready to work. Type '/dashboard' in your browser's URL to see the dashboard or '/docs' to see the documentation."
    assert response.json()["message"] == expected_message


def test_cpu_without_id(monkeypatch):
    monkeypatch.setattr("psutil.cpu_percent", lambda: 100)
    
    response = client.get("/cpu/", auth=("admin", "12345678"))
    assert response.status_code == 200
    assert response.json() == {"cpu": 100}

def test_cpu_with_id(monkeypatch):
    monkeypatch.setattr("psutil.cpu_percent", lambda percpu: [100]*psutil.cpu_count())
    response = client.get("/cpu/?cpu_id=0", auth=("admin", "12345678"))
    assert response.status_code == 200
    assert response.json() == {"cpu1": 100}
    
    response = client.get("/cpu/?cpu_id=121", auth=("admin", "12345678"))
    assert response.status_code == 404
    assert response.json() == {"detail": f"CPU not found. cpu_id must be between 1 and {psutil.cpu_count()-1}, but got 121"}

def test_dashboard_authorization():
    response = client.get("/dashboard")
    assert response.status_code == 401  # Expect Unauthorized without credentials

    # Проверка успешной авторизации
    response = client.get("/dashboard", auth=("admin", "12345678"))
    assert response.status_code == 200  # Expect OK with credentials


def test_update_df(monkeypatch):
    # Mock CPU and RAM usage
    mock_cpu_usage = [10.0] * psutil.cpu_count()
    mock_ram_usage = 50.0

    monkeypatch.setattr(psutil, "cpu_percent", lambda percpu: mock_cpu_usage)
    monkeypatch.setattr(psutil, "virtual_memory", lambda: type('obj', (object,), {'percent': mock_ram_usage}))

    # Call the function to update the DataFrame
    update_df()

    # Check if the DataFrame was updated correctly
    assert (df.iloc[-1, :-1] == mock_cpu_usage).all()
    assert df.iloc[-1, -1] == mock_ram_usage
