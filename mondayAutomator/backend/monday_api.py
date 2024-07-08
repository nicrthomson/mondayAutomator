import requests

def create_item(api_key, board_id, item_name, column_values):
    url = "https://api.monday.com/v2"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    query = f"""
    mutation {{
        create_item (board_id: {board_id}, group_id: "topics", item_name: "{item_name}", column_values: "{column_values}") {{
            id
        }}
    }}
    """
    print(f"Headers: {headers}")
    print(f"Create Item Query: {query}")
    response = requests.post(url, json={'query': query}, headers=headers)
    print(f"Create Item Response: {response.status_code}, {response.text}")
    return response.json()

def get_items(api_key, board_id):
    url = "https://api.monday.com/v2"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    query = f"""
    query {{
        boards (ids: {board_id}) {{
            items {{
                id
                name
                column_values {{
                    id
                    text
                }}
            }}
        }}
    }}
    """
    print(f"Headers: {headers}")
    print(f"Get Items Query: {query}")
    response = requests.post(url, json={'query': query}, headers=headers)
    print(f"Get Items Response: {response.status_code}, {response.text}")
    return response.json()

def update_item(api_key, board_id, item_id, column_id, value):
    url = "https://api.monday.com/v2"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    query = f"""
    mutation {{
        change_column_value (board_id: {board_id}, item_id: {item_id}, column_id: "{column_id}", value: "{value}") {{
            id
        }}
    }}
    """
    print(f"Headers: {headers}")
    print(f"Update Item Query: {query}")
    response = requests.post(url, json={'query': query}, headers=headers)
    print(f"Update Item Response: {response.status_code}, {response.text}")
    return response.json()
