import lmdb
from ast import literal_eval
from struct import pack

staticWorld = {
    pack('III', 0, 0, 5): {'name': 'Test field 005',
                           'description': 'This is the test field at the coordinates 0, 0, 5.',
                           'summary': '005'},
    pack('III', 0, 1, 5): {'name': 'Test field 015',
                           'description': 'This is the test field at the coordinates 0, 1, 5.',
                           'summary': '015'},
    pack('III', 0, 2, 5): {'name': 'Test field 025',
                           'description': 'This is the test field at the coordinates 0, 2, 5.',
                           'summary': '025'},
    pack('III', 1, 0, 5): {'name': 'Test field 105',
                           'description': 'This is the test field at the coordinates 1, 0, 5.',
                           'summary': '105'},
    pack('III', 1, 1, 5): {'name': 'Test field 115',
                           'description': 'This is the test field at the coordinates 1, 1, 5.',
                           'summary': '115'},
    pack('III', 1, 2, 5): {'name': 'Test field 125',
                           'description': 'This is the test field at the coordinates 1, 2, 5.',
                           'summary': '125'},
    pack('III', 2, 0, 5): {'name': 'Test field 205',
                           'description': 'This is the test field at the coordinates 2, 0, 5.',
                           'summary': '205'},
    pack('III', 2, 1, 5): {'name': 'Test field 215',
                           'description': 'This is the test field at the coordinates 2, 1, 5.',
                           'summary': '215'},
    pack('III', 2, 2, 5): {'name': 'Test field 225',
                           'description': 'This is the test field at the coordinates 2, 2, 5.',
                           'summary': '225'}
}


env = lmdb.open('GameDatabase', map_size=1000000, max_dbs=20)
staticWorldDB = env.open_db(bytes('StaticWorld'.encode()))
txn = env.begin(write=True, db=staticWorldDB)
for field in staticWorld:
    txn.put(field, bytes(repr(staticWorld[field]).encode()))
txn.commit()

items = {
    pack('I', 0): {'name': 'test item'},
    pack('I', 1): {'name': 'test item 2'},
    pack('I', 3): {'name': 'test item 3'},
    pack('I', 4): {'name': 'test item 4'}
}

itemLocations = {
    pack('III', 0, 0, 5): [0],
    pack('III', 0, 1, 5): [],
    pack('III', 0, 2, 5): [],
    pack('III', 1, 0, 5): [],
    pack('III', 1, 1, 5): [1],
    pack('III', 1, 2, 5): [],
    pack('III', 2, 0, 5): [],
    pack('III', 2, 1, 5): [],
    pack('III', 2, 2, 5): [0, 1, 3, 4]
}

itemDB = env.open_db(bytes('Items'.encode()))
txn = env.begin(write=True, db=itemDB)
for item in items:
    txn.put(item, bytes(repr(items[item]).encode()))
txn.commit()

itemLocationDB = env.open_db(bytes('ItemLocations'.encode()))
txn = env.begin(write=True, db=itemLocationDB)
for location in itemLocations:
    txn.put(location, bytes(repr(itemLocations[location]).encode()))
txn.commit()
loginDB = env.open_db(bytes('Login'.encode()))
charactersDB = env.open_db(bytes('Characters'.encode()))
env.open_db(bytes('Accounts'.encode()))

txn = env.begin(write=True)
for field in staticWorld:
    field = txn.get(field, db=staticWorldDB)
    field = literal_eval(field.decode())
    print(field)
