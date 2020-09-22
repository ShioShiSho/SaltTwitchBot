from tinydb import TinyDB, Query, operations, where
from pathlib import Path

data_folder = Path("data/")
file_to_open = data_folder / "db.json"


db = TinyDB(file_to_open)
db_data = db.table('data')
db_admins = db.table('admins')


def get_data(name):
    data = db_data.search(where(name).exists())
    if len(data) > 0:
        return data
    else:
        return None


def exists_data(name):
    data = get_data(name)
    return data is not None


def get_all_data():
    return db_data.all()


def add_data(name, entry):
    db_data.insert({f'{name}': entry})


def increment_bruhs():
    data = db_data.search(where('bruhs').exists())
    if len(data) > 0:
        db_data.update(operations.increment('bruhs'), where('bruhs').exists())
    else:
        return None


def reset_bruh():
    data = db_data.search(where('bruhs').exists())
    if len(data) > 0:
        db_data.update(operations.set('bruhs', 0), where('bruhs').exists())
    else:
        return None


def get_admin(name):
    Admin = Query()
    admin = db_admins.search(Admin.name == name)
    if len(admin) > 0:
        return admin[0]
    else:
        return None


def exists_admin(name):
    admin = get_admin(name)
    return admin is not None


def get_all_admins():
    return db_admins.all()


def add_admin(name):
    db_admins.insert({'name': name})


def remove_admin(name):
    Admin = Query()
    return db_admins.remove(Admin.name == name)