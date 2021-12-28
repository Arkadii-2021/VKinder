import datetime
from datetime import date, timedelta
import re
from vk_user import *
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import sqlalchemy

engine = sqlalchemy.create_engine('postgresql+psycopg2://vkinder:vk_link@localhost:5432/vk_member')
connection = engine.connect()

with open('vk_token.txt', "r") as file:
    vk_token = file.readline()

now = datetime.datetime.now()
member_list = []

community_id = input('Введите ID Вашего сообщества: ')
member_token = input('Введите токен сообщества: ')

vk = vk_api.VkApi(token=member_token)
uploader = vk_api.VkUpload(vk)
longpoll = VkLongPoll(vk)

vk_client = VkUser(vk_token, '5.131')
member_items = vk_client.get_members(community_id)['response']['items']


def calculate_age(b_date):
    pattern = re.compile(r"^([\d]*)[.](\d+)[.](\d+)")
    year = pattern.sub(r"\3", b_date)
    month = pattern.sub(r"\2", b_date)
    number = pattern.sub(r"\1", b_date)
    age = (date.today() - date(int(year), int(month), int(number))) // timedelta(days=365.2425)
    return age


def determination_sex(sex):
    id_sex = {1: 'женский', 2: 'мужской'}
    return id_sex[sex]


def family_status(m_status):
    relation_status = {
        0: 'не указано',
        1: 'не женат/не замужем', 2: 'есть друг/есть подруга',
        3: 'помолвлен/помолвлена', 4: 'Женат/замужем',
        5: 'всё сложно', 6: 'в активном поиске',
        7: 'влюблён/влюблена', 8: 'в гражданском браке'
    }
    return relation_status[m_status]


def get_member_list():
    for member in member_items:
        if ('bdate' in member and len(member['bdate']) > 5) and 'city' in member and 'relation' in member:
            ages_member = calculate_age(member['bdate'])
            if ages_member <= 120:
                sex_member = determination_sex(member['sex'])
                status_relation = family_status(member['relation'])
                member_list.append({'ID': member['id'],
                                    'Ссылка на профиль': "https://vk.com/" + member['domain'],
                                    'Имя': member['first_name'],
                                    'Фамилия': member['last_name'],
                                    'Дата рождения': member['bdate'],
                                    'Возраст': ages_member,
                                    'Пол': sex_member,
                                    'Город': member['city']['title'],
                                    'Семейное положение': status_relation})
    return member_list


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': random.randrange(10 ** 7), })


def upload_photos(user_id, owner_id, media_id):
    vk.method('messages.send', {'user_id': user_id, 'attachment': 'photo' + str(owner_id) + '_' + str(media_id),
                                'random_id': random.randint(1, 1000)})


def find_user_id(id_user_in_table):
    query_user_id_table = str('SELECT id_user FROM Black_list')
    id_table = connection.execute(query_user_id_table)
    list_id_user = []
    for user_id in list(id_table):
        list_id_user.append(user_id[0])
    if list_id_user.count(id_user_in_table):
        return True
    else:
        return False


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text
            if request == 'Найди мне друзей':
                my_user = vk_client.users_get(event.user_id)['response'][0]["first_name"]
                write_msg(event.user_id, f"Привет, {my_user}! Ожидайте результаты...")
                n = 0
                connection.execute(f"""TRUNCATE White_list;
                """)
                while n <= 2:
                    member_random = get_member_list()[random.randint(0, len(get_member_list()) - 1)]
                    while not find_user_id(member_random['ID']):
                        connection.execute(f"""INSERT INTO White_list (id_user)
                            VALUES({member_random['ID']});
                        """)
                        connection.execute(f"""INSERT INTO Black_list (id_user)
                            VALUES({member_random['ID']});
                        """)
                        vk_client.get_top_photo_list(member_random['ID'])
                        vk_client.photos_get(member_random['ID'])
                        write_msg(event.user_id, f"\nИмя: {member_random['Имя']}\n"
                                                 f"Фамилия: {member_random['Фамилия']}\n"
                                                 f"Пол: {member_random['Пол']}\n"
                                                 f"Семейное положение: {member_random['Семейное положение']}\n"
                                                 f"Дата рождения: {member_random['Дата рождения']}\n"
                                                 f"Возраст: {member_random['Возраст']}\n"
                                                 f"Город: {member_random['Город']}\n"
                                                 f"Ссылка на профиль: {member_random['Ссылка на профиль']}\n")

                        if dir_photos_list:
                            print(f'Созданы папки:\n{dir_photos_list}')
                            os.chdir(dir_photos_list[0])
                            for plist in photos_list:
                                photo_in_like = uploader.photo_messages(plist)
                                media_id = photo_in_like[0]['id']
                                owner_id = photo_in_like[0]['owner_id']
                                upload_photos(event.user_id, owner_id, media_id)
                            dir_photos_list.clear()
                            l_list.clear()
                            likes_list.clear()
                            photos_list.clear()
                            os.chdir('..')
                            print(n)
                        else:
                            print(f"\nУ пользователя с именем {member_random['Имя']} "
                                  f"с фамилией {member_random['Фамилия']} нет фотографий!")
                            write_msg(event.user_id, f"\nУ пользователя с именем {member_random['Имя']} "
                                                     f"с фамилией {member_random['Фамилия']} нет фотографий!")
                        n += 1
                        if n <= 2:
                            write_msg(event.user_id, "Ожидаем следующего кандидата...")
                            print("\nОжидаем следующего кандидата...")
                        else:
                            write_msg(event.user_id, "Поиск завершён!")
                            print("Поиск завершён!")
            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                write_msg(event.user_id, "Не понял вашего ответа...")
