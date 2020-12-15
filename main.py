import requests
from pprint import pprint
from datetime import datetime


with open('token.txt', 'r') as file_object:
    token = file_object.read().strip()


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version, user_id):
        self.token = token
        self.version = version
        self.user_id = user_id
        self.params = {
            'access_token': self.token,
            'v': self.version,
            'user_id': self.user_id,
            'fields': 'domain'
        }
        self.owner_id = requests.get(self.url + 'users.get', self.params).json()['response'][0]['id']
        self.owner_link = 'https://vk.com/' + requests.get(self.url + 'users.get', self.params).json()['response'][0]['domain']

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
        return response_photo_vk.json()

    def change_vk_response(self, response_vk):
        list_sizes_of_pic = []
        dict_height_size = {}
        list_height_size = []
        for one_pic in response_vk['response']['items']:
            pic_date = datetime.utcfromtimestamp(one_pic['date']).strftime('%d_%m_%Y_%H:%M:%S')
            print(pic_date)
            pic_likes = one_pic['likes']['count']
            print(pic_likes)
            number_of_photo_sizes = len(one_pic['sizes'])
            for counter_sizes in range(len(one_pic['sizes'])):
                dict_height_size[one_pic['sizes'][counter_sizes]['type']] = one_pic['sizes'][counter_sizes]['height']
            list_height_size = list(dict_height_size.items())
            list_height_size.sort(key=lambda i: -i[1])
            print(f'{list_height_size[0][0]}')
            dict_height_size.clear()
            print()

            #     pprint(one_pic['sizes'])

        return response_vk



vk_client1 = VkUser(token, '5.126', 552934290)
vk_client2 = VkUser(token, '5.126', 79932267)
vk_client3 = VkUser(token, '5.126', 144348760)

# pprint(vk_client3.get_photos())
result = vk_client3.get_photos()
# pprint(vk_client3.change_vk_response(result))
vk_client3.change_vk_response(result)


















# def main(info, berth):
#   while True:
#     user_input = input('Введите команду: ')
#     if user_input == 'p':
#       print(display_name_by_number_of_doc(info, berth))
#     elif user_input == 's':
#       print(display_name_by_shelf_of_doc(info, berth))
#     elif user_input == 'l':
#       display_info_by_number_of_doc(info, berth)
#     elif user_input == 'a':
#       add_new_doc(info, berth)
#       # print(info)
#       # print()
#       # print(berth)
#     elif user_input == 'd':
#       delete_doc(info, berth)
#       # print(info)
#       # print()
#       # print(berth)
#     elif user_input == 'm':
#       (move_doc(info, berth))
#       # print(info)
#       # print(berth)
#     elif user_input == 'as':
#       new_shelf(info, berth)
#       # print(berth)
#     elif user_input == 'q':
#       break
#
# main(documents, directories)
