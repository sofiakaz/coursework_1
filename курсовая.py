import requests
from datetime import datetime
import json

TOKEN = 'vk1.a.ELxGF69IK_NdoOYW7tUjDa3BsZYX1LJoHnjzQsTmM94Te-6-WXXRg5MEpGGeOCrDFWZ21fqS34z-UK1dkMFdd2ZQjf7g-R7pRX3jT6F0zhmuEkUWTBOtKia5myad23T1De0xvEQfWtm1t1VddTE6yOrdHnBYZ28o70YjDuiyLAVTn4kHXsQ-f6jo5cuR1-voVyeAtOj3xLLR9nMyHZgBlg'

class VKAPIClient:

    API_BASE_URL = 'https://api.vk.com/method'

    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id

    def get_common_params(self):
        return {
            'access_token': self.token,
            'v': '5.150'
        }

    def get_photos(self, owner_id):
        params = self.get_common_params()
        params.update({'album_id': 'wall', 'owner_id': owner_id, 'extended': '1', 'photo_sizes': '1'})
        response = requests.get(f'{self.API_BASE_URL}/photos.get', params=params)
        return response.json().get('response', {}).get('items', [])

class YandexDiskClient:

    API_BASE_URL = 'https://cloud-api.yandex.net/v1/disk/resources'

    def __init__(self, token):
        self.token = token

    def create_folder(self, folder_name):
        headers = {
            'Authorization': f'OAuth {self.token}'
        }
        params = {'path': folder_name}
        response = requests.put(f'{self.API_BASE_URL}/', headers=headers, params=params)
        return response.status_code == 201

    def upload_photo(self, folder_name, file_name, file_url):
        headers = {
            'Authorization': f'OAuth {self.token}'
        }
        params = {
            'path': f'{folder_name}/{file_name}',
            'url': file_url
        }
        response = requests.post(f'{self.API_BASE_URL}/upload', headers=headers, params=params)
        return response.status_code == 202

def main():
    user_id_to_download = int(input("Введите Ваш id: "))
    vk_client = VKAPIClient(TOKEN, user_id_to_download)

    yandex_client = YandexDiskClient(input('Введите Ваш токен Яндекс.Диска: '))
    folder_name = 'фото_из_ВК'
    if yandex_client.create_folder(folder_name):
        print('Папка на Яндекс.Диске создана.')

    photos = vk_client.get_photos(user_id_to_download)

    photo_info_list = []
    all_likes = []
    for photo in photos:
        all_likes.append(photo['likes']['count'])

    for photo in photos:
        likes = photo['likes']['count']
        if all_likes.count(likes) > 1:
            date = datetime.utcfromtimestamp(photo['date']).strftime('%Y-%m-%d')
            file_name = f'{likes}_{date}.jpg'
        else:
            file_name = f'{likes}.jpg'
        photo_info = {
            'file_name': file_name,
            'size': photo['sizes'][-1]['type']
        }
        photo_info_list.append(photo_info)

        photo_url = photo['sizes'][-1]['url']
        if yandex_client.upload_photo(folder_name, file_name, photo_url):
            print(f'Фотография {file_name} успешно загружена.')

    with open('photo_info.json', 'w', encoding='utf-8') as json_file:
        json.dump(photo_info_list, json_file, ensure_ascii=False, indent=4)

    print('Фотографии успешно сохранены и информация сохранена в photo_info.json')

if __name__ == '__main__':
    main()

