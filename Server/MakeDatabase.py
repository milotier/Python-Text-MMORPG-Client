import lmdb
from time import sleep
from ast import literal_eval
from struct import *

staticWorld = {pack('II', 0, 0): {'name': 'Test field 00',
                                  'description': 'This is a test description.'},
               pack('II', 0, 1): {'name': 'Test field 01',
                                  'description': 'This is also a test description.'},
               pack('II', 0, 2): {'name': 'Test field 02',
                                  'description': 'This is a test description.'},
               pack('II', 1, 0): {'name': 'Test field 10',
                                  'description': 'This is also a test description.'},
               pack('II', 1, 1): {'name': 'Test field 11',
                                  'description': 'This is a test description.'},
               pack('II', 1, 2): {'name': 'Test field 12',
                                  'description': 'This is also a test description.'},
               pack('II', 2, 0): {'name': 'Test field 20',
                                  'description': 'This is a test description.'},
               pack('II', 2, 1): {'name': 'Test field 21',
                                  'description': 'This is also a test description.'},
               pack('II', 2, 2): {'name': 'Test field 22',
                                  'description': 'This is a test description.'}   
              }


env = lmdb.open('GameDatabase', map_size=1000000, max_dbs=20)
staticWorldDB = env.open_db(bytes('StaticWorld'.encode()))
txn = env.begin(write=True)
for field in staticWorld:
    txn.put(field, bytes(repr(staticWorld[field]).encode()), db=staticWorldDB)
txn.commit()

txn = env.begin(write=True)
for field in staticWorld:
    field = txn.get(field, db=staticWorldDB)
    field = literal_eval(field.decode())
    print(field)
