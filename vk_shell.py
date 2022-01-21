import vk_api
import datetime
from VKinder_sources.vk_calc import get_user_token, get_member_token, random_member_table, get_member_list
from VKinder_sources.vk_user import *
from vk_api.longpoll import VkLongPoll, VkEventType
from VKinder_sources.vk_db_members import *

now = datetime.datetime.now()

print('Ожидание запуска сервиса...')
vk = vk_api.VkApi(token=get_member_token())
uploader = vk_api.VkUpload(vk)
longpoll = VkLongPoll(vk)

vk_client = VkUser(get_user_token(), '5.131')
vk_community_client = VkUser(get_member_token, '5.131')
member_list = []
event_list = []
member_items = vk_client.users_search()['response']['items']
event_item = vk_client.users_get()['response']


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': random.randrange(10 ** 7), })


def upload_photos(user_id, owner_id, media_id):
    vk.method('messages.send', {'user_id': user_id, 'attachment': 'photo' + str(owner_id) + '_' + str(media_id),
                                'random_id': random.randint(1, 1000)})


def make_dir_photos(event_user_id):
    print(f'Создана папка:\n{dir_photos_list[0]}')
    os.chdir(dir_photos_list[0])
    for plist in photos_list:
        photo_in_like = uploader.photo_messages(plist)
        media_id = photo_in_like[0]['id']
        owner_id = photo_in_like[0]['owner_id']
        upload_photos(event_user_id, owner_id, media_id)
    dir_photos_list.clear()
    l_list.clear()
    likes_list.clear()
    photos_list.clear()
    os.chdir('..')


def event_no_photos(member_random, event_user_id):
    print(f"\nУ пользователя с именем {member_random['Имя']} "
          f"с фамилией {member_random['Фамилия']} нет фотографий!")
    write_msg(event_user_id, f"\nУ пользователя с именем {member_random['Имя']} "
                             f"с фамилией {member_random['Фамилия']} нет фотографий!")


def get_member(member_random, event_user_id):
    vk_client.get_top_photo_list(member_random['ID'])
    vk_client.photos_get(member_random['ID'])
    write_msg(event_user_id, random_member_table(member_random))
    if dir_photos_list:
        make_dir_photos(event_user_id)
    else:
        event_no_photos(member_random, event_user_id)


def bot_shell():
    print('VKinder started')
    filter_member_list = []

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower()

                if request == 'Поиск' or 'ищи дальше':
                    my_user = vk_client.users_get(event.user_id)['response'][0]["first_name"]
                    write_msg(event.user_id, f"Привет, {my_user}! Ожидайте результаты...")
                    n = 1
                    while n <= 1:
                        member_id = get_member_list(member_list, member_items)
                        get_member_list(event_list, event_item)
                        for member_random in member_id:
                            if member_random['Возраст'] == event_list[0]['Возраст'] \
                                    and member_random['Пол'] != event_list[0]['Пол'] \
                                    and member_random['Город'] == event_list[0]['Город']:
                                filter_member_list.append(member_random)
                        filter_member = filter_member_list[random.randint(0, len(filter_member_list) - 1)]
                        if vk_member:
                            clear_white_list()
                            print(f"\nПользователь {filter_member['ID']} в БД добавлен")
                            while not find_user_id(filter_member['ID']):
                                add_db_list(filter_member)
                                get_member(filter_member, event.user_id)
                        else:
                            print('База данных недоступна')
                            write_msg(event.user_id, f"Из за недоступности базы данных, результаты могут повторяться")
                            add_db_list(filter_member)
                            get_member(filter_member, event.user_id)
                        n += 1
                    if n >= 1:
                        write_msg(event.user_id, "Поиск завершён!")
                        print("Поиск завершён!")
                    else:
                        write_msg(event.user_id, "Ожидаем следующего кандидата...")
                        print("\nОжидаем следующего кандидата...")

                elif request == "пока":
                    write_msg(event.user_id, "Пока((")
                else:
                    write_msg(event.user_id, "Не понял вашего ответа...")
