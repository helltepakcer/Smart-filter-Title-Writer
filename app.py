import pymysql
from pymysql.cursors import DictCursor
from .passwords import IMGCMS_LOGIN, IMGCMS_PASS

# connecting to db.sql
user = IMGCMS_LOGIN
pswd = IMGCMS_PASS

connection = pymysql.connect(
    host='localhost',
    user=user,
    password=pswd,
    db='santeh',
    charset='utf8mb4',
    cursorclass=DictCursor
)
connection.close()

# TODO write code which will take category id and return all category properties
'SELECT property_id FROM `shop_product_properties_categories` WHERE category_id = {}'.format('categ var')  # properties
# TODO then we need to get all values from properties
# TODO write func which will take category, property value and property to write a records
# TODO to create new url to property in smart filter

# TODO Create template for TITLE and H1
# TODO We should create records for 2 tables
# TODO Create template for first table
# TODO get records from 1 row; with .format put empty variables to create them later
# TODO Create template for second table
