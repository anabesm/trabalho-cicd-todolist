from app import app

def test_health_check():
    client = app.test_client()
    response = client.get('/health')
    assert response.status_code == 200
    assert response.data == b"OK"