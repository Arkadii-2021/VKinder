import sqlalchemy
import psycopg2
import json
import os.path

ids_list = {'id': []}

try:
    engine = sqlalchemy.create_engine('postgresql+psycopg2://vkinder:vk_link@localhost:5432/vk_member')
    connection = engine.connect()
except sqlalchemy.exc.OperationalError:
    vk_member = False
else:
    vk_member = True


def clear_white_list():
    connection.execute(f"""TRUNCATE White_list;""")


def save_member_ids(member_id):
    if not os.path.isfile('member_ids.json'):
        with open("member_ids.json", "w") as data_ids:
            ids_list['id'].append(member_id)
            data_ids.write(json.dumps(ids_list))
            data_ids.close()
    else:
        with open("member_ids.json", "r") as ids_data:
            data = json.load(ids_data)
            data['id'].append(member_id)
        with open("member_ids.json", "w") as ids_data:
            json.dump(data, ids_data, ensure_ascii=False, indent=4)


def save_to_db_in_member_ids():
    if os.path.isfile('member_ids.json'):
        with open("member_ids.json", "r") as ids_data:
            data = json.load(ids_data)
            for ids in data['id']:
                connection.execute(f"""INSERT INTO Black_list (id_user) VALUES({ids});""")
        os.remove('member_ids.json')


def add_db_list(member):
    if vk_member:
        save_to_db_in_member_ids()
        connection.execute(f"""INSERT INTO White_list (id_user) VALUES({member['ID']});""")
        connection.execute(f"""INSERT INTO Black_list (id_user) VALUES({member['ID']});""")
    else:
        save_member_ids(member['ID'])


def find_user_id(id_user_in_table):
    query_user_id_table = str('SELECT id_user FROM Black_list')
    list_id_user = []
    id_table = connection.execute(query_user_id_table)
    for user_id in list(id_table):
        list_id_user.append(user_id[0])
    if list_id_user.count(id_user_in_table):
        return True
    else:
        return False
