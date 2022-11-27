from peewee import *
import datetime
from enum import unique

# Using sqlite for local dev
DATABASE = SqliteDatabase('KaylaCares4Kids.sqlite')

class BaseModel(Model):
    class Meta:
        database = DATABASE
    
class User(BaseModel):
    email = CharField(unique=True)
    name = CharField()
    phone = CharField(null=True)

class Role(BaseModel):
    name = CharField(unique=True)

class Permission(BaseModel):
    permission = CharField()
    role_id = ForeignKeyField(Role, backref='permissions')

class UserRole(BaseModel):
    user = ForeignKeyField(User)
    role = ForeignKeyField(Role)
 
class Facility(BaseModel):
    name = CharField()
    address1 = CharField()
    address2 = CharField(null=True)
    city = CharField()
    state = CharField()
    country = CharField(default='USA')
    zipcode = CharField()
    contact_id = ForeignKeyField(User, backref='facility')

class Destination(BaseModel):
    name = CharField()
    address1 = CharField()
    address2 = CharField(null=True)
    city = CharField()
    state = CharField()
    country = CharField(default='USA')
    zipcode = CharField()
    contact_name = CharField()
    contact_email = CharField()
    contact_phone = CharField()

class LookUpSheet(BaseModel):
    description = CharField()
    value = DecimalField(decimal_places=2, constraints=[Check('value >= 0.0')])
    kids_served = IntegerField(constraints=[Check('kids_served > 0')])

class Item(BaseModel):
    facility_id = ForeignKeyField(Facility)
    category = CharField()
    condition = CharField(default='Gently Used')
    fair_market_value = DecimalField(decimal_places=2)
    kids_served = IntegerField(constraints=[Check('kids_served > 0')])
    title_desc = CharField()
    format = CharField(null=True)
    artist = CharField(null=True)
    genre = CharField(null=True)
    age_range = CharField()
    rating = CharField(null=True)
    location = CharField(null=True)
    upc_code = CharField(null=True)
    date_received = DateField(default=datetime.datetime.now)
    date_shipped = DateField(null=True)
    destination_id = ForeignKeyField(Destination, null=True, default=None)
    received_by = ForeignKeyField(User)

def initialize():
    '''connect to database and create tables if they don't exist then close connection'''
    DATABASE.connect()
    DATABASE.create_tables([
        User,
        Role,
        Permission,
        UserRole,
        Facility,
        Destination,
        LookUpSheet,
        # ItemCategory,
        Item
        ], safe=True)
    DATABASE.close()
