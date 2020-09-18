from tinydb import TinyDB, Query


db = TinyDB('./data/db.json')
db_data = db.table('data')


def get_data(name):
    Data = Query()
    data = db_data.search(Data.name == name)
    if len(data) > 0:
        return data[0]
    else:
        return None


def exists_data(name):
    data = get_data(name)
    return data is not None


def get_all_data():
    return db_data.all()


def add_data(name, entry):
    db_data.insert({f'{name}': entry})


def remove_data(name):
    Data = Query()
    return db_data.remove(Data.name == name)