import requests
import json
from io import BytesIO
from tqdm import tqdm

# User Input Yandex token and breed name
YANDEX_TOKEN = input("Yandex Disk Token: ")
YANDEX_API_URL = "https://cloud-api.yandex.net/v1/disk/resources"

HEADERS = {
    'Authorization': f'OAuth {YANDEX_TOKEN}'
}

def get_breeds():
    url = 'https://dog.ceo/api/breeds/list/all'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['message']

def get_image_url(breed, sub_breed=None):
    """Random image URL for the given breed and sub-breed."""
    if sub_breed:
        url = f'https://dog.ceo/api/breed/{breed}/{sub_breed}/images/random'
    else:
        url = f'https://dog.ceo/api/breed/{breed}/images/random'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['message']

def create_folder(folder_path):
    """Create folder"""
    params = {'path': folder_path}
    response = requests.put(YANDEX_API_URL, headers=HEADERS, params=params)
    if response.status_code not in [201, 409]:
        print(f"Error creating folder {folder_path}: {response.text}")
    return response

def upload_image(image_url, yandex_path):
    """Upload"""
    file_name = image_url.split('/')[-1]
    upload_path = f"{yandex_path}/{file_name}"

    params = {
        'path': upload_path,
        'overwrite': 'true'
    }
    upload_resp = requests.get(f"{YANDEX_API_URL}/upload", headers=HEADERS, params=params)
    upload_resp.raise_for_status()
    upload_url = upload_resp.json()['href']

    image_resp = requests.get(image_url, stream=True)
    image_resp.raise_for_status()

    with BytesIO(image_resp.content) as image_stream:
        put_resp = requests.put(upload_url, files={'file': image_stream})
        put_resp.raise_for_status()

    return upload_path

def validate_token():
    """Validate token."""
    test_url = 'https://cloud-api.yandex.net/v1/disk'
    response = requests.get(test_url, headers=HEADERS)
    if response.status_code == 401:
        raise Exception("❌, [Copy and Paste Yandex Disk Token]")
    else:
        print("✅")

def main():
    """Handle the process."""
    validate_token()

    breeds = get_breeds()

    breed = input(f"Breed name (choices: {', '.join(breeds.keys())}): ").lower()

    if breed not in breeds:
        print(f"❌ Breed '{breed}' not found. Enter a valid breed name.")
        return

    result_data = {}
    folder_name = f'dog_images/{breed}'
    create_folder(folder_name)

    result_data[breed] = []

    sub_breeds = breeds[breed]

    if sub_breeds:
        for sub in sub_breeds:
            image_url = get_image_url(breed, sub)
            upload_path = upload_image(image_url, folder_name)
            result_data[breed].append({
                'sub_breed': sub,
                'image_url': image_url,
                'yandex_path': upload_path
            })
    else:
        image_url = get_image_url(breed)
        upload_path = upload_image(image_url, folder_name)
        result_data[breed].append({
            'sub_breed': None,
            'image_url': image_url,
            'yandex_path': upload_path
        })

    with open('result.json', 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=4)

    print("✅ Successfully saved to result.json")


if __name__ == "__main__":
    main()