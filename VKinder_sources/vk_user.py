import os
import requests
import random

photos_list = []
likes_list = []
l_list = []
dir_photos_list = []


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def users_get(self, user_id=None):
        groups_url = self.url + 'users.get'
        users_params = {
            'user_id': user_id,
            'fields': 'photo_id, verified, sex, bdate, city, country, home_town, has_photo, '
                      'photo_50, photo_100, photo_200_orig, photo_200, photo_400_orig, photo_max, photo_max_orig, '
                      'online, domain, has_mobile, contacts, site, education, universities, schools, status, '
                      'last_seen, followers_count, common_count, occupation, nickname, relatives, relation, personal, '
                      'connections, exports, activities, interests, music, movies, tv, books, games, about, quotes, '
                      'can_post, can_see_all_posts, can_see_audio, message, can_send_friend_request, is_favorite, '
                      'is_hidden_from_feed, timezone, screen_name, maiden_name, crop_photo, is_friend, friend_status, '
                      'career, military, blacklisted, blacklisted_by_me, can_be_invited_group'
        }
        res = requests.get(groups_url, params={**self.params, **users_params}, timeout=5)
        return res.json()

    def users_search(self, q=''):
        groups_url = self.url + 'users.search'
        users_params = {
            'q': q,
            'count': 900,
            'fields': 'about, activities, bdate, blacklisted, blacklisted_by_mebooks, can_post, can_see_all_posts,'
                      'can_see_audio, can_send_friend_request, can_write_private_message, career, city, common_count,'
                      'connections, contacts, country, crop_photo, domain, education, exports, followers_count, '
                      'friend_status, games, has_mobile, has_photo, home_town, interests, is_favorite, is_friend,'
                      'is_hidden_from_feed, last_seen, lists, maiden_name, military, movies, music, nickname,'
                      'occupation, online, personal, photo_100, photo_200, photo_200_orig, photo_400_orig, photo_50,'
                      'photo_id, photo_max, photo_max_orig, quotes, relation, relatives, schools, screen_name, sex,'
                      'site, status, timezone, tv, universities, verified, wall_comments'
        }
        res = requests.get(groups_url, params={**self.params, **users_params}, timeout=5)
        return res.json()

    def get_top_photo_list(self, owner_id=None):
        photos_url = self.url + 'photos.get'
        photos_params = {
            'owner_id': owner_id,
            'album_id': 'profile',
            'extended': '1',
            'count': 500
        }
        res = requests.get(photos_url, params={**self.params, **photos_params}, timeout=5).json()
        sizes_album_list = res['response']['items']
        for album_list in sizes_album_list:
            likes_list.append(album_list['likes']['count'])
        if len(likes_list) > 0:
            l_max = max(likes_list)
            l_list.extend(sorted(likes_list)[-3:l_max])
            print(f'Список лайков у пользователя\n{l_list}')
        else:
            print('Фотографии отсутствуют')
        return sorted(l_list)

    def photos_get(self, owner_id=None):
        photos_url = self.url + 'photos.get'
        photos_params = {
            'owner_id': owner_id,
            'album_id': 'profile',
            'extended': '1',
            'count': 500
        }
        res = requests.get(photos_url, params={**self.params, **photos_params}).json()
        sizes_album_list = res['response']['items']
        if not os.path.isdir('images_profile_' + str(owner_id)):
            os.mkdir('images_profile_' + str(owner_id))
        for album_list in sizes_album_list:
            response_url = requests.get((album_list['sizes'][-1]['url']), timeout=5)
            for top_likes_photo in l_list:
                if album_list['likes']['count'] == top_likes_photo:
                    dir_photos_list.append('images_profile_' + str(owner_id))
                    random_post = random.randint(1, 100)
                    image_path = os.path.join(f'images_profile_' + str(owner_id),
                                              str(album_list['likes']['count']) + '_' + str(random_post) + '.jpg')
                    with open(image_path, 'bw') as image_vk:
                        image_vk.write(response_url.content)
                    photos_list.append(str(album_list['likes']['count']) + '_' + str(random_post) + '.jpg')
        print(f'Список файлов:\n{photos_list}')

