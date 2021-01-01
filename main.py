import config
import requests
from pprint import pprint
from datetime import datetime
import json


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token_vk, version, user_id):
        self.token = token_vk
        self.version = version
        self.user_id = user_id
        self.params = {
            'access_token': self.token,
            'v': self.version,
            'user_id': self.user_id,
            'fields': 'domain'
        }
        self.owner_id = requests.get(self.url + 'users.get', self.params).json()['response'][0]['id']
        # self.owner_link = 'https://vk.com/' + requests.get(self.url + 'users.get', self.params).json()['response'][0]['domain']

    def get_photos(self, user_id=None):
        if user_id is None:
            user_id = self.owner_id
        photos_url = self.url + 'photos.get'
        photos_params = {
            'owner_id': user_id,
            'extended': '1',
            'album_id': 'profile',
            'rev': '1'
        }
        response_photo_vk = requests.get(photos_url, params={**self.params, **photos_params})
        print('Info about photos was loaded from vk')
        return response_photo_vk.json()

    def get_all_photos(self, user_id=None):
        if user_id is None:
            user_id = self.owner_id
        all_photos_url = self.url + 'photos.getAll'
        all_photos_params = {
            'owner_id': user_id,
            'extended': '1',
        }
        response_all_photos_vk = requests.get(all_photos_url, params={**self.params, **all_photos_params})
        print('Info about all photos was loaded from vk')
        return response_all_photos_vk.json()

    def change_vk_response(self, response_vk):
        ''' Changing vk_response to type of dictionary that we need:
         modified name, type of image and url'''
        list_of_dict_pic = []
        dict_height_size = {}
        list_height_size = []
        for one_pic in response_vk['response']['items']:
            dict_info_one_pic = {}
            pic_date = datetime.utcfromtimestamp(one_pic['date']).strftime('%d_%m_%Y_%H_%M_%S')
            dict_info_one_pic['pic_date'] = pic_date
            # print(pic_date)
            pic_likes = one_pic['likes']['count']
            dict_info_one_pic['pic_likes'] = pic_likes
            dict_info_one_pic['name'] = str(pic_likes)
            owner_id = one_pic['owner_id']
            dict_info_one_pic['owner_id'] = owner_id
            # print(pic_likes)
            for counter_sizes in range(len(one_pic['sizes'])):
                dict_height_size[one_pic['sizes'][counter_sizes]['type']] = one_pic['sizes'][counter_sizes]['height']
            list_height_size = list(dict_height_size.items())
            list_height_size.sort(key=lambda g: -g[1])
            # print(list_height_size[0][0])
            dict_info_one_pic['type_max_size'] = list_height_size[0][0]
            dict_height_size.clear()
            for one_image in one_pic['sizes']:
                if (one_image['type']) == list_height_size[0][0]:
                    dict_info_one_pic['url_max_size'] = one_image['url']
            list_of_dict_pic.append(dict_info_one_pic)

        '''Changing name to count_of_likes.jpg or 
        to count_of_likes-date.jpg if there is the same number of likes on photos'''
        for i in range(len(list_of_dict_pic)-1):
            for j in range(i+1, len(list_of_dict_pic)):
                if list_of_dict_pic[i]['pic_likes'] == list_of_dict_pic[j]['pic_likes']:
                    list_of_dict_pic[i]['name'] = str(list_of_dict_pic[i]['pic_likes']) + \
                                                  '-' + str(list_of_dict_pic[i]['pic_date']) + '.jpg'
                    list_of_dict_pic[j]['name'] = str(list_of_dict_pic[j]['pic_likes']) + \
                                                  '-' + str(list_of_dict_pic[j]['pic_date']) + '.jpg'

        for one_elem in list_of_dict_pic:
            if '.jpg' not in one_elem['name']:
                one_elem['name'] += '.jpg'
        # pprint(list_of_dict_pic)
        print('Information about photos was modified')
        return list_of_dict_pic


class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def make_a_folder_photos(self):
        HEADERS = {"Authorization": f"OAuth {self.token}"}

        response_folder = requests.put("https://cloud-api.yandex.net/v1/disk/resources",
                                       params={"path": f"/id{photos_from_vk[0]['owner_id']}_{number_of_photos}"},
                                       headers=HEADERS)
        response_folder.raise_for_status()
        result_folder = response_folder.json()
        href_ya = result_folder['href']
        # print(href_ya)
        print('Folder on Yandex disk for photos was created')
        return href_ya

    def make_a_folder_json(self):
        HEADERS = {"Authorization": f"OAuth {self.token}"}

        response_folder = requests.put("https://cloud-api.yandex.net/v1/disk/resources",
                                       params={"path": f"/id{photos_from_vk[0]['owner_id']}_{number_of_photos}/output"},
                                       headers=HEADERS)
        response_folder.raise_for_status()
        result_folder = response_folder.json()
        href_ya_json = result_folder['href']
        # print(href_ya)
        print('Folder on Yandex disk for json-file was created')
        return href_ya_json

    def upload_by_url(self):
        HEADERS = {"Authorization": f"OAuth {self.token}"}
        for n in range(number_of_photos):
            # print(len(photos_from_vk))
            # print(n)
            if n == len(photos_from_vk):
                print(f'There are only {len(photos_from_vk)} pictures in album')
                break
            response_folder = requests.post("https://cloud-api.yandex.net/v1/disk/resources/upload",
                                           params={"path": f"/id{photos_from_vk[0]['owner_id']}_{number_of_photos}/{photos_from_vk[n]['name']}",
                                                   "url": photos_from_vk[n]['url_max_size']},
                                           headers=HEADERS)
            response_folder.raise_for_status()
            result_folder = response_folder.json()
            print(f'{n + 1} pictures loaded')
        print('Photos from vk were uploaded to Yandex disk')

    def upload_json(self, file_path: str):
        """Метод загруджает файл file_path на яндекс диск"""
        HEADERS = {"Authorization": f"OAuth {self.token}"}

        resp1 = requests.get("https://cloud-api.yandex.net/v1/disk/resources/upload",
                             params={"path": f"/id{photos_from_vk[0]['owner_id']}_{number_of_photos}/output/upload.json",
                                     "overwrite": "true"},
                             headers=HEADERS)

        resp1.raise_for_status()
        result1 = resp1.json()
        # pprint(result1)
        href = result1["href"]

        with open(file_path, "r") as f:
            resp2 = requests.put(href, files={"file": f})

        resp2.raise_for_status()

        return print('Json was successfully uploaded')


def main():
    global number_of_photos
    global photos_from_vk
    number_of_photos = 5
    id_vk_input = int(input('Введите id пользователя vk: '))
    ya_token_input = input('Введите яндекс-токен: ')
    number_of_pic_input = input('Введите количество фотографий (по умолчанию скачаются последние 5): ')
    type_of_photos = input('Скачать фотографии только с профиля(1) или все(2)? Введите 1 или 2: ')

    # id_vk_input = 79932267
    # ya_token_input = "AgAAAABGl0B0AADLW4oimzzNWkOThPSoLoSCJ9o"
    # number_of_pic_input = input('Введите количество фотографий (по умолчанию скачаются последние 5): ')

    if number_of_pic_input != '':
        number_of_photos = int(number_of_pic_input)
    vk_client = VkUser(config.vk_token, '5.126', id_vk_input)

    if type_of_photos == '1':
        result_vk = VkUser.get_photos(vk_client)
    elif type_of_photos == '2':
        result_vk = VkUser.get_all_photos(vk_client)
    else:
        print("Введённые данные не верны")

    with open("output.json", 'w') as json_file:
        output = json.dumps(result_vk, sort_keys=True, indent=4)
        json_file.write(output)

    photos_from_vk = VkUser.change_vk_response(vk_client, result_vk)
    ya_client = YaUploader(ya_token_input)
    href_for_ya = ya_client.make_a_folder_photos()
    ya_client.make_a_folder_json()
    ya_client.upload_json("output.json")
    ya_client.upload_by_url()


    # print()
    # pprint(result_vk)


main()

# тестовый id vk - 552934290


