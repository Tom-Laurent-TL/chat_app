import httpx

client = httpx.Client(timeout=10.0)
response = client.get('http://127.0.0.1:8000/conversations/1')
print(f'Get conversation: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Title: {data["title"]}')
    print(f'Participants: {len(data.get("participants", []))}')
    for p in data.get('participants', []):
        print(f'  - {p.get("type")}: {p.get("full_name")}')
else:
    print(response.text)