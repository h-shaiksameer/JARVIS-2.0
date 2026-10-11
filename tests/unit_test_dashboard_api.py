from app import app


def test_status_endpoint_reports_process_state():
    client = app.test_client()
    response = client.get('/status')
    assert response.status_code == 200
    payload = response.get_json()
    assert 'running' in payload
    assert 'ai_configured' in payload


def test_command_endpoint_requires_command():
    client = app.test_client()
    response = client.post('/command', json={})
    assert response.status_code == 400
