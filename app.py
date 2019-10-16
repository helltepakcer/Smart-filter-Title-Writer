import pymysql
from pymysql.cursors import DictCursor
from passwords import IMGCMS_LOGIN, IMGCMS_PASS  # ignore error
import time

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

# TODO write code which will take category id and return all category properties
# add category with which you want to work
category_id = '3640'
cat_property_list = []

try:

    with connection.cursor() as cursor:

        # SQL
        sql = 'SELECT property_id FROM `shop_product_properties_categories` WHERE category_id = {0}'.format(category_id)

        # Execute Query
        cursor.execute(sql)

        print("cursor.description: ", cursor.description)

        print()

        for row in cursor:  #
            cat_property_list.append(row.get('property_id'))

        #print(cat_property_list)

        # TODO then we need to get all values from properties
        properties_values = {}
        'SELECT position FROM `shop_product_property_value` WHERE property_id={}.format("property")'

        for prop in cat_property_list:
            sql = 'SELECT id FROM `shop_product_property_value` WHERE property_id={0}'.format(prop)

            # Execute Query
            cursor.execute(sql)

            positions_list = []
            for id_value in cursor:
                id_value = id_value.get('id')

                positions_list.append(id_value)

            properties_values[prop] = positions_list

        print(properties_values)

        new_property_value = {}
        value_id_value_name = {}
        for properti in properties_values:
            values_id_list = properties_values[properti]
            new_value_list = []
            for value_id in values_id_list:

                sql = 'SELECT value FROM `shop_product_property_value_i18n` WHERE id={0}'.format(value_id)

                # Execute Query
                cursor.execute(sql)

                for value in cursor:
                    new_value_list.append(value.get('value'))
                    value_id_value_name[value_id] = value.get('value')

            new_property_value[properti] = new_value_list

        print(value_id_value_name)
        print(new_property_value)

        # get property name on RUS and ENG(trascript)
        properties_eng_name = {}
        for value_id in new_property_value:
            sql = 'SELECT csv_name FROM `shop_product_properties` WHERE id={0}'.format(value_id)

            # Execute Query
            cursor.execute(sql)

            for prop_eng_name in cursor:
                properties_eng_name[value_id] = prop_eng_name.get('csv_name')

        print(properties_eng_name)

        # TODO Create template for first table

        new_smart_filter_value_table_1 = {
            'id': 'int',  # get max result from sql table and +1 for it num
            'category_id': 'int',  # =category_id_var
            'active': 'tinyint',  # =1
            'url_patter': 'varchar255| property-moschnost',  # property-{}.format(propertry_name)
            'data': '{"category_url":"boilery","property_id":"441","value_id":"818"}',
        # category_url":"{}.format(categName)
            'meta_index': 'tinyint',  # 1 or 0
            'meta follow': 'tinyint',  # 1 or 0
            'craeted': '',  # TODO create variables
            'updated': ''
        }

        # get max value of id from table and add 1 too it
        id_smart_filter = ''
        sql = 'SELECT MAX(id) FROM `smart_filter_patterns`'

        # Execute Query
        cursor.execute(sql)
        for i in cursor:
            id_smart_filter = i.get('MAX(id)')

        if id_smart_filter == None:
            id_smart_filter = 1

        # get category_id at the moment from user
        category_id_for_sql = category_id

        # get category url
        category_url = ''
        sql = 'SELECT url FROM `route` WHERE entity_id = {}'.format(category_id_for_sql)
        # Execute Query
        cursor.execute(sql)
        for i in cursor:
            print(i)
            category_url = i.get('url')

            #category_url = category_url.replace('/', '')

        # ENG property name
        for properti_id in properties_values:
            for value_id in properties_values[properti_id]:
                id_smart_filter += 1

                eng_properties = properties_eng_name[properti_id]
                url = '{}-{}'.format(eng_properties, value_id)

                data = '"category_url":"{0}","property_id":"{1}","value_id":"{2}"'.format(category_url, properti_id, value_id)
                create = int(time.time())
                update = int(time.time())
                value = value_id_value_name[value_id]

                # TODO get records from 1 row; with .format put empty variables to create them later
                sql_query_table1 = 'INSERT INTO smart_filter_patterns (id, category_id, active, url_pattern, data, ' \
                                   'meta_index, meta_follow, created, updated)' \
                ' VALUES ("{0}", "{1}", "{2}", "property-{3}", {4}, "{5}", "{6}", "{7}", "{8}")'.format\
                    (id_smart_filter, category_id_for_sql, '1', url, "'{}'".format(data), '1', '1', create, update)

                print(sql_query_table1)
                # try:
                cursor.execute(sql_query_table1)

                # except:
                #     continue

                # get RUS category name
                rus_cut_name = ''
                # parent_id = ''
                # sql = 'SELECT parent_id FROM `shop_category` WHERE id = {}'.format(category_id_for_sql)
                # # Execute Query
                # cursor.execute(sql)
                # for i in cursor:
                #     parent_id = i.get('parent_id')  # parent_id

                sql = 'SELECT name FROM `shop_category_i18n` WHERE id = {}'.format(category_id_for_sql)
                # Execute Query
                cursor.execute(sql)
                for i in cursor:
                    rus_cut_name = i.get('name')  # RUS category name

                # get RUS property name
                properti_name = ''
                sql = 'SELECT name FROM `shop_product_properties_i18n` WHERE id = {}'.format(properti_id)
                # Execute Query
                cursor.execute(sql)
                for i in cursor:
                    properti_name = i.get('name')  # RUS property name

                smart_name = '{0}({1})'.format(properti_name, value)
                property_tail = ''

                # TODO Create template for TITLE and H1
                title = '{} {} {}'.format(rus_cut_name, value, properti_name)
                h1 = '{} - {}'.format(rus_cut_name,  value)

                sql_query_table2 = 'INSERT INTO smart_filter_patterns_i18n (id, locale, h1, meta_title, meta_description, meta_keywords, seo_text, name)' \
                            ' VALUES ("{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}")'.format(id_smart_filter,
                                                                                     'ru', h1,
                                                                                     title, '', '', '',
                                                                                     smart_name)

                print(sql_query_table2)
                # try:
                cursor.execute(sql_query_table2)
                connection.commit()
                # except:
                #     continue


finally:
    # Close connection
    connection.close()



'SELECT property_id FROM `shop_product_properties_categories` WHERE category_id = {}'.format('categ var')  # properties
'SELECT csv_name FROM `shop_product_properties` WHERE property_id={}.format("property")'  # eng properties for url




# TODO get brand value

# TODO write func which will take category, property value and property to write a records
# TODO to create new url to property in smart filter

# TODO We should create records for 2 tables
# TODO Separate property template and brand template, after both will be done - create template for property and
# TODO brand together


# TODO Create template for second table

new_smart_filter_value_table_2 = {
    'id': '',  # =id from 1 table
    'locale': 'ru',  # static
    'h1': '',  # data from my template
    'meta_title': '',  # data from my template
    'meta_description': '',  # data from my template
    'meta_keywords': '',  # data from my template
    'seo_text': '',  # data from my template
    'name': ''  # =RU property_name
}




