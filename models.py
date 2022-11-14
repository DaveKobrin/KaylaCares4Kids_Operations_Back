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
    permission = CharField(unique=True)

class UserRole(BaseModel):
    user = ForeignKeyField(User)
    role = ForeignKeyField(Role)
 
class Facility(BaseModel):
    address1 = CharField()
    address2 = CharField(null=True)
    city = CharField()
    state = CharField()
    country = CharField(default='USA')
    zipcode = CharField()
    contact_id = ForeignKeyField(User, backref='facility')

class Destinations(BaseModel):
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

class ItemCategory(BaseModel):
    category = CharField(unique=True)

class Item(BaseModel):
    facility_id = ForeignKeyField(Facility, backref='fac_items')
    category_id = ForeignKeyField(ItemCategory, backref='cat_items')
    condition = CharField(default='Gently Used')
    quantity = IntegerField(default=1, constraints=[Check('quantity >= 0')])
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
    date_last_modified = DateField(default=datetime.datetime.now)
    
def initialize():
    '''connect to database and create tables if they don't exist then close connection'''
    DATABASE.connect()
    DATABASE.create_tables([User, Role, UserRole, Facility, Destinations, LookUpSheet, ItemCategory, Item], safe=True)
    DATABASE.close()
