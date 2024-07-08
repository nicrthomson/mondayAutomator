import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Get the API key and board ID from environment variables
API_KEY = os.getenv('MONDAY_API_KEY')
BOARD_ID = os.getenv('MONDAY_BOARD_ID')
API_URL = 'https://api.monday.com/v2'

headers = {
    "Authorization": API_KEY
}

# GraphQL query to get items and their subitems
query = """
{
  boards(ids: %s) {
    items_page {
      cursor
      items {
        id
        name
        subitems {
          id
          name
          column_values {
            id
            text
          }
        }
      }
    }
  }
}
""" % BOARD_ID

def get_board_data():
    response = requests.post(API_URL, headers=headers, json={'query': query})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"API request failed with status code {response.status_code}")
        print(f"Response: {response.text}")
        raise Exception(f"Query failed to run by returning code of {response.status_code}. {query}")

def print_subitems(data):
    boards = data.get('data', {}).get('boards', [])
    if not boards:
        print("No boards found.")
        return

    for board in boards:
        items_page = board.get('items_page', {})
        items = items_page.get('items', [])
        if not items:
            print("No items found.")
            return

        for item in items:
            print(f"Item: {item['name']} (ID: {item['id']})")
            subitems = item.get('subitems', [])
            if not subitems:
                print("No subitems found for this item.")
                continue

            for subitem in subitems:
                print(f"  Subitem: {subitem['name']} (ID: {subitem['id']})")
                column_values = subitem.get('column_values', [])
                for column_value in column_values:
                    print(f"    {column_value['id']}: {column_value['text']}")

if __name__ == "__main__":
    try:
        data = get_board_data()
        print(json.dumps(data, indent=2))  # Print the entire response for debugging
        print_subitems(data)
    except Exception as e:
        print(e)
