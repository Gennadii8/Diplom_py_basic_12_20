import requests
from pprint import pprint
from datetime import datetime
import time


with open('token.txt', 'r') as file_object:
    token_vk = file_object.read().strip()


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

    def make_a_folder(self):
        HEADERS = {"Authorization": "OAuth "}

        response_folder = requests.put("https://cloud-api.yandex.net/v1/disk/resources",
                                       params={"path": f"/id{photos_from_vk[0]['owner_id']}_{number_of_photos}"},
                                       headers=HEADERS)
        response_folder.raise_for_status()
        result_folder = response_folder.json()
        href_ya = result_folder['href']
        # print(href_ya)
        print('Folder on Yandex disk was created')
        return href_ya

    def upload_by_url(self):
        HEADERS = {"Authorization": "OAuth "}
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


def main():
    global number_of_photos
    global photos_from_vk
    number_of_photos = 5
    id_vk_input = int(input('Введите id пользователя vk: '))
    ya_token_input = input('Введите яндекс-токен: ')
    number_of_pic_input = input('Введите количество фотографий (по умолачанию скачаются последние 5): ')
    if number_of_pic_input != '':
        number_of_photos = int(number_of_pic_input)
    vk_client = VkUser(token_vk, '5.126', id_vk_input)
    result_vk = VkUser.get_photos(vk_client)
    photos_from_vk = VkUser.change_vk_response(vk_client, result_vk)
    ya_client = YaUploader(ya_token_input)
    href_for_ya = ya_client.make_a_folder()
    ya_client.upload_by_url()
    # print()
    # print(result_vk)


main()

# тестовый id vk - 552934290

















# Потом это удалю
# vk_client1 = VkUser(token_vk, '5.126', 552934290)
# vk_client2 = VkUser(token_vk, '5.126', 79932267)
# vk_client3 = VkUser(token_vk, '5.126', 144348760)

# pprint(vk_client1.get_photos())
# pprint(VkUser.get_photos(vk_client1))
# result = vk_client3.get_photos()

# pprint(VkUser.get_photos(vk_client3))
# result1 = VkUser.get_photos(vk_client3)
# pprint(vk_client3.change_vk_response(result))

# vk_client3.change_vk_response(result)
# pprint(VkUser.change_vk_response(vk_client3, result1))

# photos_from_vk = VkUser.change_vk_response(vk_client3, result1)

# print(photos_from_vk[0]['name'])
# print(photos_from_vk[0]['url_max_size'])


# number_of_photos = 4
#
# ya_client = YaUploader("AgAAAABGl0B0AADLW4oimzzNWkOThPSoLoSCJ9o")
# href_for_ya = ya_client.make_a_folder()
# ya_client.upload_by_url()









