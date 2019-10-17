import pymysql
from pymysql.cursors import DictCursor
from passwords import IMGCMS_LOGIN, IMGCMS_PASS  # ignore error
import time


# TODO get brand value

# TODO write func which will take category, property value and property to write a records
# TODO to create new url to property in smart filter

# TODO Separate property template and brand template, after both will be done - create template for property and
# TODO brand together

def cleaner(i):
    i = i.replace('/', '')
    i = i.replace('"', '')
    i = i.replace("'", "")
    return i


def category_creator(category_id):
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

    try:
        with connection.cursor() as cursor:
            print('Category ID - ', category_id)
            print('Start creating titles for this category')
            print()
            cat_property_list = []
            parent_id = ''
            sql = 'SELECT parent_id FROM `shop_category` WHERE id = {}'.format(category_id)
            # Execute Query
            print(sql)
            cursor.execute(sql)
            for i in cursor:
                parent_id = i.get('parent_id')  # parent_id

            if not parent_id:
                parent_id = "0"

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



            # ENG property name
            for properti_id in properties_values:
                for value_id in properties_values[properti_id]:

                    id_smart_filter += 1

                    eng_properties = properties_eng_name[properti_id]
                    url = '{}-{}'.format(eng_properties, value_id)
                    data = ''

                    # if category PARENT
                    if parent_id == '0':
                        data = '"category_url":"{0}","property_id":"{1}","value_id":"{2}"'.format(category_url, properti_id, value_id)

                    # if category CHILD
                    if parent_id != '0':
                        parent_url = ''
                        sql = 'SELECT parent_url FROM `route` WHERE entity_id = {}'.format(category_id_for_sql)
                        # Execute Query
                        cursor.execute(sql)
                        for i in cursor:
                            parent_url = i.get('parent_url')


                        child_category_url = '{}\/{}'.format(parent_url, category_url)
                        data = '"category_url":"{0}","property_id":"{1}","value_id":"{2}"'.format(child_category_url, properti_id, value_id)

                    create = int(time.time())
                    update = int(time.time())
                    value = value_id_value_name[value_id]

                    sql_query_table1 = 'INSERT INTO smart_filter_patterns (id, category_id, active, url_pattern, data, ' \
                                       'meta_index, meta_follow, created, updated)' \
                    ' VALUES ("{0}", "{1}", "{2}", "property-{3}", {4}, "{5}", "{6}", "{7}", "{8}")'.format\
                        (id_smart_filter, category_id_for_sql, '1', url, "'{}'".format(data), '1', '1', create, update)

                    print(sql_query_table1)
                    try:
                        cursor.execute(sql_query_table1)

                        # get RUS category name
                        rus_cut_name = ''

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

                        # template for TITLE and H1
                        #title = '{} {} {}'.format(rus_cut_name, value, properti_name)
                        #h1 = '{} - {}'.format(rus_cut_name,  value)
                        title = '{{category.name}} {{brand.name}} {{value.name}} {{property.name}}'
                        h1 = '{{category.name}} {{brand.name}} {{property.name}} {{value.name}}'
                        desc = 'Купить {{category.name}} {{brand.name}} {{property.name}} {{value.name}} в Киеве и' \
                               ' Украине | (099)793-34-50 Интернет магазин Santehtech'

                        # filter
                        title = cleaner(title)
                        h1 = cleaner(h1)
                        smart_name = cleaner(smart_name)

                        sql_query_table2 = 'INSERT INTO smart_filter_patterns_i18n (id, locale, h1, meta_title, meta_description, meta_keywords, seo_text, name)' \
                                    ' VALUES ("{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}")'.format(id_smart_filter,
                                                                                             'ru', h1,
                                                                                             title, desc, '', '',
                                                                                             smart_name)

                        print(sql_query_table2)

                        cursor.execute(sql_query_table2)
                        connection.commit()

                    except pymysql.err.IntegrityError:
                        print('Catch dublicate, just ignore it and going forward...')
                        print()
                        pass

        cursor.close()

    finally:
        # Close connection
        connection.close()

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

try:
    with connection.cursor() as cursor:
            category_id = '3327'

            # get subcategories if exist
            sql = 'SELECT id FROM `shop_category` WHERE active = 1'.format(category_id)
            # Execute Query
            cursor.execute(sql)
            sub_cutegories = cursor
            print(sub_cutegories)
finally:
            connection.close()

if not sub_cutegories:  # if parent category
    category_creator(category_id)
else:
    for i in sub_cutegories:
        category = i.get('id')
        category_creator(category)
    category_creator(category_id)
