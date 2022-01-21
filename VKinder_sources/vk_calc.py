import os
import re
from datetime import date, timedelta


def get_user_token():
    if os.path.exists("vk_token.txt") and os.stat("vk_token.txt").st_size:
        with open("vk_token.txt", "r") as file:
            vk_token = file.readline()
    else:
        vk_token = input('Введите токен пользователя: ')
        with open("vk_token.txt", 'w') as user_token:
            user_token.write(vk_token)
    return vk_token


def get_member_token():
    if os.path.exists("vk_member_token.txt") and os.stat("vk_member_token.txt").st_size:
        with open("vk_member_token.txt", "r") as file:
            member_token = file.readline()
    else:
        member_token = input('Введите токен сообщества: ')
        with open("vk_member_token.txt", 'w') as user_token:
            user_token.write(member_token)
    return member_token


def data_member(member, ages_member, sex_member, status_relation):
    member_data = {'ID': member['id'],
                   'Ссылка на профиль': "https://vk.com/" + member['domain'],
                   'Имя': member['first_name'],
                   'Фамилия': member['last_name'],
                   'Дата рождения': member['bdate'],
                   'Возраст': ages_member,
                   'Пол': sex_member,
                   'Город': member['city']['title'],
                   'Семейное положение': status_relation}
    return member_data


def random_member_table(member_random):
    table_list = f"\nИмя: {member_random['Имя']}\n"\
                 f"Фамилия: {member_random['Фамилия']}\n"\
                 f"Пол: {member_random['Пол']}\n" \
                 f"Семейное положение: {member_random['Семейное положение']}\n"\
                 f"Дата рождения: {member_random['Дата рождения']}\n"\
                 f"Возраст: {member_random['Возраст']}\n"\
                 f"Город: {member_random['Город']}\n"\
                 f"Ссылка на профиль: {member_random['Ссылка на профиль']}\n"
    return table_list


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


def get_member_list(member_list, member_item):
    for member in member_item:
        if ('bdate' in member and len(member['bdate']) > 5) and 'city' in member:
            ages_member = calculate_age(member['bdate'])
            sex_member = determination_sex(member['sex'])
            if 'relation' in member:
                status_relation = family_status(member['relation'])
            else:
                status_relation = 'Не указано'
            member_list.append(data_member(member, ages_member, sex_member, status_relation))
    return member_list
