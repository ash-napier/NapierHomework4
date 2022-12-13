"""
Amy Napier
SDEV 400 4380
12/12/22
Final Project: NPC Builder
Purpose: The NPC Builder is a tool to help create Non-Playable Characters (NPCs)
for fantasy writing or games like Dungeons and Dragons.
"""
import logging
import json
import time
import decimal
import random
import textwrap
import sys
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from fpdf import FPDF
from datetime import datetime

# CONFIGURE AWS BOTO3
boto3.setup_default_session()
REGION='us-east-1'
TABLE_NAMES = {"class_type", "gender", "first_name", "family_name", "profession",
                "quirk", "race", "trait"}
dynamodb = boto3.resource('dynamodb', region_name = REGION)
s3 = boto3.client('s3', region_name = REGION)
BUCKET_NAME='npc-builder-amy-napier-sdev-400-4380'

# CONFIGURE LOGGING
logging.basicConfig(filename='./NapierHomework4/npc_builder.log',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s',
                    filemode='w')

# CONFIGURE PDF
class PDF(FPDF):
    def header(self):
        self.set_font('Times', 'I', 12)
        # Title
        self.cell(30, 10, 'NPC Builder')
        # Line break
        self.ln(20)

# FOR ALL USER YES/NO QUESTIONS
def user_continue_option():
    """ Asks user if they want to continue and returns true/false"""
    while True:
        user_choice = str(input("Enter yes or no: "))
        if user_choice.lower() in ['yes', 'y']:
            return True
        if user_choice.lower() in ['no', 'n']:
            return False
        logging.error('User entered %s when program expected yes or no.', user_choice)
        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("Please enter a valid selection such as 'yes' or 'no'")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

# FOR ALL USER NUMBER SELECT QUESTIONS
def user_number_choice(max_num):
    """ Asks user for their choice and returns the number"""
    while True:
        try:
            user_choice=int(input("Enter the number that corresponds to your selection: "))
            if user_choice > 0 and user_choice <= max_num:
                return user_choice
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!  Invalid user entry.                                        !")
            print("!  Please enter a number corresponding to a menu option.      !")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        except Exception as err:
            logging.error("User entered an invalid input.")
            logging.error(err)
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!  Invalid user entry.                                        !")
            print("!  Please enter a number corresponding to a menu option.      !")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

# INITIALIZE TABLES
def create_db():
    """ Create courses DB and populates with items from json file """
    for table_name in TABLE_NAMES:
        print(f'Initializing the {table_name} table...')
        try:
            table = dynamodb.Table(table_name)
            item_count = count_items_db(table)
            if table.table_status == 'ACTIVE':
                if item_count > 0:
                    logging.error('Attempted to create %s table, but it already exists', table_name)
                    print(f'Table already exists and has {item_count} records.')
                else:
                    print(f'The {table_name} table was already initialized, populating table...')
                    populate_db(table_name)
        except ClientError as error:
            try:
                table = dynamodb.create_table(
                    TableName=table_name,
                    KeySchema=[
                        {
                            'AttributeName': table_name + '_id',
                            'KeyType': 'HASH'  #Partition key
                        }
                    ],
                    GlobalSecondaryIndexes=[
                        {
                            'IndexName': table_name + '_index',
                            'KeySchema': [
                                {
                                'AttributeName': table_name,
                                'KeyType': 'HASH'
                                }
                            ],
                            'Projection': {
                                'ProjectionType': 'ALL',
                            },
                            'ProvisionedThroughput': {
                                'ReadCapacityUnits': 123,
                                'WriteCapacityUnits': 123
                            }
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': table_name + '_id',
                            'AttributeType': 'N'
                        },
                        {
                            'AttributeName': table_name,
                            'AttributeType': 'S'
                        }
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 10,
                        'WriteCapacityUnits': 10
                    }
                )
            except ClientError as err:
                logging.error(err)
                print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print(error)
                print(f'Could not create {table_name}.')
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    for table_name in TABLE_NAMES:
        print(f'Making sure the {table_name} table is ready...')
        table.wait_until_exists()
        print(f'Attempting to populate the {table_name} table...')
        populate_db(table_name)

def populate_db(table_name):
    """ Fills all of the tables with data from Json files """
    try:
        table = dynamodb.Table(table_name)
        file_name = "./NapierHomework4/DB-Data/" + table_name + ".json"
        with open(file_name, encoding="utf-8") as json_file:
            data = json.load(json_file, parse_float = decimal.Decimal)
            if table_name == 'class_type':
                class_type_id=0
                for item in data:
                    class_type_id += 1
                    class_type = item['Class']
                    class_description = item['Description']
                    primary_stat = item['PrimaryStat']
                    logging.info('Adding ' + class_type + ' to ' + table_name)
                    response = table.put_item(
                        Item={
                            'class_type_id': class_type_id,
                            'class_type': class_type,
                            'class_description': class_description,
                            'primary_stat': primary_stat
                        }
                    )
            if table_name == 'gender':
                gender_id=0
                for item in data:
                    gender_id += 1
                    gender = item['Gender']
                    logging.info('Adding ' + gender + ' to ' + table_name)
                    response = table.put_item(
                        Item={
                            'gender_id': gender_id,
                            'gender': gender,
                        }
                    )
            if table_name == 'first_name':
                first_name_id=0
                for item in data:
                    first_name_id += 1
                    first_name = item['FirstName']
                    name_gender = item['NameGender']
                    logging.info('Adding ' + first_name + ' to ' + table_name)
                    response = table.put_item(
                        Item={
                            'first_name_id': first_name_id,
                            'first_name': first_name,
                            'name_gender': name_gender
                        }
                    )
            if table_name == 'family_name':
                family_name_id=0
                for item in data:
                    family_name_id += 1
                    family_name = item['FamilyName']
                    name_gender = item['NameGender']
                    logging.info('Adding ' + family_name + ' to ' + table_name)
                    response = table.put_item(
                        Item={
                            'family_name_id': family_name_id,
                            'family_name': family_name,
                            'name_gender': name_gender
                        }
                    )
            if table_name == 'profession':
                prof_id=0
                for item in data:
                    prof_id += 1
                    profession = item['Profession']
                    prof_description = item['Description']
                    toolkit = item['Toolkit']
                    logging.info('Adding ' + profession + ' to ' + table_name)
                    response = table.put_item(
                        Item={
                            'profession_id': prof_id,
                            'profession': profession,
                            'profession_description': prof_description,
                            'toolkit': toolkit
                        }
                    )
            if table_name == 'quirk':
                quirk_id=0
                for item in data:
                    quirk_id += 1
                    quirk = item['Quirk']
                    logging.info('Adding ' + quirk + ' to ' + table_name)
                    response = table.put_item(
                        Item={
                            'quirk_id': quirk_id,
                            'quirk': quirk
                        }
                    )
            if table_name == 'race':
                race_id=0
                for item in data:
                    race_id += 1
                    race = item['Race']
                    race_description = item['Description']
                    logging.info('Adding ' + race + ' to ' + table_name)
                    response = table.put_item(
                        Item={
                            'race_id': race_id,
                            'race': race,
                            'race_description': race_description
                        }
                    )
            if table_name == 'trait':
                trait_id=0
                for item in data:
                    trait_id += 1
                    trait = item['Trait']
                    logging.info('Adding ' + trait + ' to ' + table_name)
                    response = table.put_item(
                        Item={
                            'trait_id': trait_id,
                            'trait': trait
                        }
                    )
        item_count = count_items_db(table)
        logging.info('The %s table initalized with %s records', table_name, item_count)
        print("\n************************ SUCCESS ******************************")
        print(f"The {table_name} table initialized with {item_count} records")
        print("***************************************************************\n")
    except ClientError as error:
        logging.error(error)
        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(error)
        print(f'Could not populate {table_name}.')
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

# COUNT ITEMS IN TABLE
def count_items_db(table):
    """ scans table to determine live number of items """
    response = table.scan()
    complete = False
    records=[]
    scan_kwargs = {}
    while not complete:
        try:
            response = table.scan(**scan_kwargs)
        except ClientError as error:
            logging.error(error)

        records.extend(response.get('Items', []))
        next_key = response.get('LastEvaluatedKey')
        scan_kwargs['ExclusiveStartKey'] = next_key
        complete = True if next_key is None else False
    item_count = 0
    for item in records:
        item_count += 1
    return item_count

# CHECK TABLES EXIST
def check_tables():
    """ checks if all of the tables exist and have at least 1 record """
    for table_name in TABLE_NAMES:
        try:
            table = dynamodb.Table(table_name)
            item_count = count_items_db(table)
            if item_count == 0:
                return False
        except:
            return False
    return True

def get_random_key(table_name):
    """ uses total items in table to generate a random number """
    table = dynamodb.Table(table_name)
    item_count = count_items_db(table)
    return random.randrange(1,item_count)

def get_random_gender():
    print('*  Randomly selecting a gender...                             *')
    key_num = get_random_key('gender')
    try:
        table = dynamodb.Table('gender')
        response = table.query(
            ProjectionExpression="gender",
            KeyConditionExpression=Key('gender_id').eq(key_num)
        )
        # parse json to get just the attribute value we want
        json_dumps_response = json.dumps(response['Items'][0], skipkeys=True)
        json_loads_response = json.loads(json_dumps_response)
        gender = json_loads_response['gender']
        logging.info('Gender selected: %s', gender)
    except ClientError as err:
        print(err)
        logging.error(
            "Couldn't get gender from table. Here's why: %s: %s",
            err.response['Error']['Code'], err.response['Error']['Message'])
    return gender

def display_table_contents(table_name):
    try:
        table = dynamodb.Table(table_name)
        item_count = count_items_db(table)
        item_num = 0
        key_name = table_name + '_id'
        for item in range(item_count):
            item_num += 1
            response = table.query(
                ProjectionExpression=table_name,
                KeyConditionExpression=Key(key_name).eq(item_num)
            )
            # parse json to get just the attribute value we want
            json_dumps_response = json.dumps(response['Items'][0], skipkeys=True)
            json_loads_response = json.loads(json_dumps_response)
            item = json_loads_response[table_name]
            print(f'    {item_num}. {item}')
    except ClientError as err:
        print(err)
        logging.error(
            "Couldn't get items from table. Here's why: %s: %s",
            err.response['Error']['Code'], err.response['Error']['Message'])
    return item

def select_gender():
    """ Allows user to either use a random gender or select a gender """ 
    print('Would you like to use a random gender?')
    if user_continue_option():
        gender = get_random_gender()
        return gender
    try:
        print('Available Genders: ')
        table = dynamodb.Table('gender')
        display_table_contents('gender')
        max_num = count_items_db(table)
        user_choice = user_number_choice(max_num)
        response = table.query(
            ProjectionExpression="gender",
            KeyConditionExpression=Key('gender_id').eq(user_choice)
        )
        # parse json to get just the attribute value we want
        json_dumps_response = json.dumps(response['Items'][0], skipkeys=True)
        json_loads_response = json.loads(json_dumps_response)
        gender = json_loads_response['gender']
        logging.info('Gender selected: %s', gender)
        return gender
    except ClientError as err:
        print(err)
        logging.error(
            "Couldn't get gender from table. Here's why: %s: %s",
            err.response['Error']['Code'], err.response['Error']['Message'])
    return gender

def get_random_name(gender):
    """ Get a random name that matches the gender from DynamoDB table """
    print('*  Randomly selecting a gender appropriate name...            *')
    # First Name
    try:
        table = dynamodb.Table('first_name')
        name_found = False
        while name_found is False:
            key_num = get_random_key('first_name')
            response = table.query(
                ProjectionExpression='first_name, name_gender',
                KeyConditionExpression=Key('first_name_id').eq(key_num)
            )
            # parse json to get just the attribute value we want
            json_dumps_response = json.dumps(response['Items'][0], skipkeys=True)
            json_loads_response = json.loads(json_dumps_response)
            name_gender = json_loads_response['name_gender']
            # check that name is gendered correctly
            if name_gender in [gender, 'Non-binary']:
                name_found = True
                first_name = json_loads_response['first_name']
                logging.info('First name selected: %s', first_name)
    except ClientError as err:
        print(err)
        logging.error(
            "Couldn't get first name from table. Here's why: %s: %s",
            err.response['Error']['Code'], err.response['Error']['Message'])
    # Family Name
    key_num = get_random_key('family_name')
    try:
        table = dynamodb.Table('family_name')
        response = table.query(
            ProjectionExpression='family_name',
            KeyConditionExpression=Key('family_name_id').eq(key_num)
        )
        # parse json to get just the attribute value we want
        json_dumps_response = json.dumps(response['Items'][0], skipkeys=True)
        json_loads_response = json.loads(json_dumps_response)
        family_name = json_loads_response['family_name']
        logging.info('Family name selected: %s', family_name)
        full_name = first_name + " " + family_name
    except ClientError as err:
        print(err)
        logging.error(
            "Couldn't get family name from table. Here's why: %s: %s",
            err.response['Error']['Code'], err.response['Error']['Message'])
    return full_name

def select_name(gender):
    """ Allows user to either use a random name or enter a name """ 
    print('Would you like to use a random name?')
    if user_continue_option():
        name = get_random_name(gender)
        return name
    while True:
        try:
            name = str(input("Enter a name for your character: "))
            if len(name) < 64:
                break
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print('!  The name you entered was too long.                         !')
            print('!  Please enter a name under 64 characters.                   !')
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        except ClientError as err:
            print(err)
    logging.info('Name enterered: %s', name)
    return name

def get_random_profession():
    """ Get a random profession from DynamoDB table """
    print('*  Randomly selecting a profession...                         *')
    key_num = get_random_key('profession')
    try:
        table = dynamodb.Table('profession')
        response = table.query(
            ProjectionExpression='profession',
            KeyConditionExpression=Key('profession_id').eq(key_num)
        )
        # parse json to get just the attribute value we want
        json_dumps_response = json.dumps(response['Items'][0], skipkeys=True)
        json_loads_response = json.loads(json_dumps_response)
        profession = json_loads_response['profession']
        logging.info('Profession selected: %s', profession)
    except ClientError as err:
        print(err)
        logging.error(
            "Couldn't get profession from table. Here's why: %s: %s",
            err.response['Error']['Code'], err.response['Error']['Message'])
    return profession

def select_profession():
    """ Allows user to either use a random profession or select a prof """ 
    print('Would you like to use a random profession?')
    if user_continue_option():
        profession = get_random_profession()
        return profession
    try:
        print('Available Professions: ')
        table = dynamodb.Table('profession')
        display_table_contents('profession')
        max_num = count_items_db(table)
        user_choice = user_number_choice(max_num)
        response = table.query(
            ProjectionExpression="profession",
            KeyConditionExpression=Key('profession_id').eq(user_choice)
        )
        # parse json to get just the attribute value we want
        json_dumps_response = json.dumps(response['Items'][0], skipkeys=True)
        json_loads_response = json.loads(json_dumps_response)
        profession = json_loads_response['profession']
        logging.info('Profession selected: %s', profession)
    except ClientError as err:
        print(err)
        logging.error(
            "Couldn't get profession from table. Here's why: %s: %s",
            err.response['Error']['Code'], err.response['Error']['Message'])
    return profession

def get_profession_desc(profession):
    """ Get a profession description from DynamoDB table """
    try:
        table = dynamodb.Table('profession')
        response = table.query(
            IndexName = 'profession_index',
            ProjectionExpression="profession_description",
            KeyConditionExpression=Key('profession').eq(profession)
        )
        # parse json to get just the attribute value we want
        json_dumps_response = json.dumps(response['Items'][0], skipkeys=True)
        json_loads_response = json.loads(json_dumps_response)
        profession_desc = json_loads_response['profession_description']
    except ClientError as err:
        print(err)
        logging.error(
            "Couldn't get profession description from table. Here's why: %s: %s",
            err.response['Error']['Code'], err.response['Error']['Message'])
    return profession_desc

def get_random_class():
    """ Get a random class from DynamoDB table """
    print('*  Randomly selecting a class...                              *')
    key_num = get_random_key('class_type')
    try:
        table = dynamodb.Table('class_type')
        response = table.query(
            ProjectionExpression='class_type',
            KeyConditionExpression=Key('class_type_id').eq(key_num)
        )
        # parse json to get just the attribute value we want
        json_dumps_response = json.dumps(response['Items'][0], skipkeys=True)
        json_loads_response = json.loads(json_dumps_response)
        class_type = json_loads_response['class_type']
        logging.info('Class selected: %s', class_type)
    except ClientError as err:
        print(err)
        logging.error(
            "Couldn't get class from table. Here's why: %s: %s",
            err.response['Error']['Code'], err.response['Error']['Message'])
    return class_type

def select_class():
    """ Allows user to either use a random class or select a class """ 
    print('Would you like to use a random class?')
    if user_continue_option():
        class_type = get_random_class()
        return class_type
    try:
        table = dynamodb.Table('class_type')
        print('Available classes: ')
        display_table_contents('class_type')
        max_num = count_items_db(table)
        user_choice = user_number_choice(max_num)
        response = table.query(
            ProjectionExpression="class_type",
            KeyConditionExpression=Key('class_type_id').eq(user_choice)
        )
        # parse json to get just the attribute value we want
        json_dumps_response = json.dumps(response['Items'][0], skipkeys=True)
        json_loads_response = json.loads(json_dumps_response)
        class_type = json_loads_response['class_type']
        logging.info('Class selected: %s', class_type)
    except ClientError as err:
        print(err)
        logging.error(
            "Couldn't get gender from table. Here's why: %s: %s",
            err.response['Error']['Code'], err.response['Error']['Message'])
    return class_type

def get_class_desc(class_type):
    """ Get a class description from DynamoDB table """
    try:
        table = dynamodb.Table('class_type')
        response = table.query(
            IndexName='class_type_index',
            ProjectionExpression="class_description",
            KeyConditionExpression=Key('class_type').eq(class_type)
        )
        # parse json to get just the attribute value we want
        json_dumps_response = json.dumps(response['Items'][0], skipkeys=True)
        json_loads_response = json.loads(json_dumps_response)
        class_desc = json_loads_response['class_description']
    except ClientError as err:
        print(err)
        logging.error(
            "Couldn't get class description from table. Here's why: %s: %s",
            err.response['Error']['Code'], err.response['Error']['Message'])
    return class_desc

def get_random_race():
    """ Get a random race from DynamoDB table """
    print('*  Randomly selecting a race...                               *')
    key_num = get_random_key('race')
    try:
        table = dynamodb.Table('race')
        response = table.query(
            ProjectionExpression='race',
            KeyConditionExpression=Key('race_id').eq(key_num)
        )
        # parse json to get just the attribute value we want
        json_dumps_response = json.dumps(response['Items'][0], skipkeys=True)
        json_loads_response = json.loads(json_dumps_response)
        race = json_loads_response['race']
        logging.info('Race selected: %s', race)
    except ClientError as err:
        print(err)
        logging.error(
            "Couldn't get race from table. Here's why: %s: %s",
            err.response['Error']['Code'], err.response['Error']['Message'])
    return race

def select_race():
    """ Allows user to either use a random race or select a race """ 
    print('Would you like to use a random race?')
    if user_continue_option():
        race = get_random_race()
        return race
    try:
        table = dynamodb.Table('race')
        print('Available classes: ')
        display_table_contents('race')
        max_num = count_items_db(table)
        user_choice = user_number_choice(max_num)
        response = table.query(
            ProjectionExpression="race",
            KeyConditionExpression=Key('race_id').eq(user_choice)
        )
        # parse json to get just the attribute value we want
        json_dumps_response = json.dumps(response['Items'][0], skipkeys=True)
        json_loads_response = json.loads(json_dumps_response)
        race = json_loads_response['race']
        logging.info('Class selected: %s', race)
    except ClientError as err:
        print(err)
        logging.error(
            "Couldn't get gender from table. Here's why: %s: %s",
            err.response['Error']['Code'], err.response['Error']['Message'])
    return race

def get_race_desc(race):
    """ Get a race description from DynamoDB table """
    try:
        table = dynamodb.Table('race')
        response = table.query(
            IndexName='race_index',
            ProjectionExpression="race_description",
            KeyConditionExpression=Key('race').eq(race)
        )
        # parse json to get just the attribute value we want
        json_dumps_response = json.dumps(response['Items'][0], skipkeys=True)
        json_loads_response = json.loads(json_dumps_response)
        race_desc = json_loads_response['race_description']
    except ClientError as err:
        print(err)
        logging.error(
            "Couldn't get race description from table. Here's why: %s: %s",
            err.response['Error']['Code'], err.response['Error']['Message'])
    return race_desc

def get_random_traits():
    """ Get three random traits from DynamoDB table """
    print('*  Randomly selecting three traits...                         *')
    traits = []
    for num in range(3):
        key_num = get_random_key('trait')
        try:
            table = dynamodb.Table('trait')
            response = table.query(
                ProjectionExpression="trait",
                KeyConditionExpression=Key('trait_id').eq(key_num)
            )
            # parse json to get just the attribute value we want
            json_dumps_response = json.dumps(response['Items'][0], skipkeys=True)
            json_loads_response = json.loads(json_dumps_response)
            trait = json_loads_response['trait']
            logging.info('Trait selected: %s', trait)
            traits.append(trait)
        except ClientError as err:
            print(err)
            logging.error(
                "Couldn't get traits from table. Here's why: %s: %s",
                err.response['Error']['Code'], err.response['Error']['Message'])
    return traits

def select_traits():
    """ Allows user to either use random traits or enter traits """ 
    traits = []
    print('Would you like to use random traits?')
    if user_continue_option():
        traits = get_random_traits()
        return traits
    try:
        for num in range(3):
            while True:
                trait = str(input("Enter trait " + str(num + 1) + " for your character: "))
                if len(trait) < 64:
                    logging.info('Trait %s entered: %s', num, trait)
                    traits.append(trait)
                    break
                print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print('!  The trait you entered was too long.                        !')
                print('!  Please enter a trait under 64 characters.                  !')
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    except ClientError as err:
        print(err)
    return traits

def get_random_quirk():
    """ Get a random quirk from DynamoDB table """
    print('*  Randomly selecting a quirk...                              *')
    key_num = get_random_key('quirk')
    try:
        table = dynamodb.Table('quirk')
        response = table.query(
            ProjectionExpression="quirk",
            KeyConditionExpression=Key('quirk_id').eq(key_num)
        )
        # parse json to get just the attribute value we want
        json_dumps_response = json.dumps(response['Items'][0], skipkeys=True)
        json_loads_response = json.loads(json_dumps_response)
        quirk = json_loads_response['quirk']
        logging.info('Quirk selected: %s', quirk)
    except ClientError as err:
        print(err)
        logging.error(
            "Couldn't get quirk from table. Here's why: %s: %s",
            err.response['Error']['Code'], err.response['Error']['Message'])
    return quirk

def select_quirk():
    """ Allows user to either use a random quirk or enter a quirk """ 
    print('Would you like to use a random quirk?')
    if user_continue_option():
        quirk = get_random_quirk()
        return quirk
    while True:
        try:
            quirk = str(input("Enter a quirk for your character: "))
            if len(quirk) < 128:
                break
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print('!  The quirk you entered was too long.                        !')
            print('!  Please enter a quirk under 128 characters.                 !')
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        except ClientError as err:
            print(err)
    logging.info('Quirk enterered: %s', quirk)
    return quirk

def display_character(gender, name, profession, class_type, race, traits, quirk):
    """ Print character summary """
    wrapper = textwrap.TextWrapper(width=50)
    print("   " + name + " is a " + gender + " " + race)
    print("   They are a " + profession + " " + class_type)
    print("   They have the following traits:")
    print("     1. " + traits[0])
    print("     2. " + traits[1])
    print("     3. " + traits[2])
    print("   Their quirk is: ")
    quirk_string = wrapper.fill(text=quirk)
    print(textwrap.indent(text=quirk_string, prefix='        '))

def save_character(gender, name, profession, class_type, race, traits, quirk):
    """ Create a PDF of character information and save it to S3 """
    print("\n************************* PROCESSING *************************")
    print("*  Initiating PDF...                                         *")
    pdf = FPDF('P', 'mm', 'letter')
    pdf.add_page()
    pdf.set_font('Times', 'B', 12)
    print("*  Adding character name...                                  *")
    pdf.cell(0, 10, 'Name: ' + name, ln=1)
    pdf.set_font('Times', '', 12)
    print("*  Adding character gender...                                *")
    pdf.cell(0, 10, 'Gender: ' + gender, ln=1)
    print("*  Adding character race...                                  *")
    race_desc = get_race_desc(race)
    pdf.multi_cell(0, 10, 'Race: ' + race + ' - ' + race_desc)
    print("*  Adding character profession...                            *")
    profession_desc = get_profession_desc(profession)
    pdf.multi_cell(0, 10, 'Profession: ' + profession + ' - ' + profession_desc)
    print("*  Adding character class...                                 *")
    class_desc = get_class_desc(class_type)
    pdf.multi_cell(0, 10, 'Class: ' + class_type + ' - ' + class_desc)
    print("*  Adding character traits...                                *")
    pdf.cell(0, 10, 'Traits: ', ln=1)
    pdf.multi_cell(0, 5, '1. ' + traits[0] \
            + '\n2. ' + traits[1]\
            + '\n3. ' + traits[2])
    print("*  Adding character quirk...                                 *")
    pdf.multi_cell(0, 10, 'Quirk: ' + quirk)
    print("*  Finalizing PDF...                                         *")
    now = datetime.now()
    timestamp = now.strftime("%d-%m-%y_%H%M")
    pdf_name = 'NPC-Builder_' + name + '-' + timestamp + '.pdf'
    pdf.output(pdf_name, 'F')
    upload_to_s3(pdf_name)

def upload_to_s3(filename):
    """Add a file to an Amazon S3 bucket"""
    try:
        s3.upload_file(filename, BUCKET_NAME, filename)
        logging.info(f'Uploaded {filename} to {BUCKET_NAME}.')
        print("\n*************************** SUCCESS ***************************")
        print(f'{filename} was saved successfully!')
        print("***************************************************************\n")
    except ClientError as error:
        logging.error(error)
        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(error)
        print(f'Could not upload {filename}.')
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

def check_bucket():
    """Check if there is a bucket """ 
    s3 = boto3.resource('s3')
    return s3.Bucket(BUCKET_NAME) in s3.buckets.all()

def create_bucket():
    """Create an S3 bucket in us-east-1"""
    # Create bucket
    s3 = boto3.resource('s3')
    try:
        s3.create_bucket(Bucket=BUCKET_NAME)
    except ClientError as err:
        logging.error(err)
        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f'Failed to create {BUCKET_NAME} in region {REGION}.')
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    logging.info(f'Created bucket {BUCKET_NAME} in region {REGION}.')
    print("\n*************************** SUCCESS ***************************")
    print(f'Created {BUCKET_NAME} in region {REGION}.')
    print("***************************************************************\n")

def list_bucket_object_count():
    """List the objects in an Amazon S3 bucket"""
    # Retrieve the list of bucket objects
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        if 'Contents' in response:
            item_count = 0
            for item in response:
                item_count = item_count + 1
            return item_count
        return 0
    except ClientError as err:
        logging.error(err)
        return 0

def list_bucket_objects():
    """List the objects in an Amazon S3 bucket"""
    # Retrieve the list of bucket objects
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        if 'Contents' in response:
            item_count = 0
            for obj in response['Contents']:
                item_count = item_count + 1
                item_number = str(item_count)
                print("[" + item_number + "] " + obj["Key"])
        else: 
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print('Cannot select an item. Bucket is empty')
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    except ClientError as err:
        # AllAccessDisabled error == bucket not found
        logging.error(err)
        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print('Cannot display bucket items')
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

def user_object_select():
    """ lets see a list of s3 bucket objects to select one """ 
    object_count = list_bucket_object_count()
    if object_count > 0:
        list_bucket_objects()
        while True:
            object_choice = input("Which object would you like to select? ")
            try:
                validate_choice = int(object_choice)
                if validate_choice > 0 and validate_choice <= object_count:
                    try:
                        resp = s3.list_objects_v2(Bucket=BUCKET_NAME)
                        count = 0
                        for item in resp['Contents']:
                            count = count + 1
                            if count == int(object_choice):
                                object_name = item['Key']
                                print("You selected: " + object_name)
                        return object_name
                    except ClientError as e:
                        logging.error(e)
                        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        print(f'Could not select an object from {BUCKET_NAME}')
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
                else:
                    print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print('Invalid input. Number entered is out of expected range.')
                    print('Please enter the number that corresponds to the object.')
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            except:
                print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print('Invalid Input. Value should be digits.')
                print('Please enter the number that corresponds to the object.')
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

def delete_object():
    """Delete an object from an S3 bucket"""
    object_name = user_object_select()
    if object_name: 
        try:
            s3.delete_object(Bucket=BUCKET_NAME, Key=object_name)
            logging.info(f'Deleted {object_name} from {BUCKET_NAME}.')
            print("\n*************************** SUCCESS ***************************")
            print(f'Deleted {object_name} \nfrom {BUCKET_NAME} successfully!')
        except ClientError as e:
            logging.error(e)
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print(f'Could not delete {object_name}\n from {BUCKET_NAME}')
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        return
    logging.error(f'Attempt to delete an item from {BUCKET_NAME} failed. Bucket is empty.')
    print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(f'Attempt to delete an item from {BUCKET_NAME} failed. Bucket is empty.')
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

def empty_bucket():
    """Remove all objects from a bucket."""
    try:
        # First we list all files in folder
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        files_in_folder = response["Contents"]
        files_to_delete = []
        # We will create Key array to pass to delete_objects function
        for f in files_in_folder:
            files_to_delete.append({"Key": f["Key"]})
        # This will delete all files in a folder
        response = s3.delete_objects(
            Bucket=BUCKET_NAME, Delete={"Objects": files_to_delete}
        )
    except ClientError as error:
        logging.error(error)
        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print('Unable to empty bucket. Please see log for more info.')
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

def download_object():
    # Download an object from a S3 Bucket
    """Download a file from a S3 bucket"""
    object_count = list_bucket_object_count()
    if object_count > 0:
        try:
            object_name = user_object_select()
            local_object_name = "download_" + object_name
            s3.download_file(BUCKET_NAME, object_name, local_object_name)
            logging.info(f'{object_name} was downloaded from {BUCKET_NAME}')
            print("\n*************************** SUCCESS ***************************")
            print(f'{object_name} was downloaded \nfrom {BUCKET_NAME} successfully!')
        except ClientError as error:
            logging.error(error)
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print(error)
            print(f'Could not download {object_name}.')
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        return
    logging.error(f'Attempt to download an object from\n {BUCKET_NAME} failed. Bucket is empty.')
    print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(f'Attempt to copy an object from {BUCKET_NAME} failed. Bucket is empty.')
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

def main_menu():
    """ User Menu """
    print("\n************************** MAIN MENU **************************")
    print("*  NPC BUILDER                                                *")
    print("***************************************************************")
    print("*  [1] Generate A Random Character                            *")
    print("*  [2] Build A Custom Character                               *")
    print("*  [3] View Saved Characters                                  *")
    print("*  [4] Download A Saved Character                             *")
    print("*  [5] Delete A Saved Character                               *")
    print("*  [6] Delete All Saved Characters                            *")
    print("*  [0] Exit the program                                       *")
    print("***************************************************************\n")

def main():
    """Character Builder Application"""
    # Check if environment is ready
    if check_tables() is False:
        print("Please wait while the cloud environment is being prepared...")
        create_db()
    if check_bucket() is False:
        print("Please wait while the cloud environment is being prepared...")
        create_bucket()
    # Main Menu
    print("***************************************************************")
    print("******************* FANTASY CHARACTER BUILDER *****************")
    print("***************************************************************\n")
    option = 9
    while option != 0:
        main_menu()
        try:
            option=int(input("Enter selection: "))
            # handle user selection - see each function for more info
            if option == 1:
                try:
                    print("\n************************* PROCESSING *************************")
                    gender = get_random_gender()
                    name = get_random_name(gender)
                    profession = get_random_profession()
                    class_type = get_random_class()
                    race = get_random_race()
                    traits = get_random_traits()
                    quirk = get_random_quirk()
                    print("***************************************************************")
                    print("\n************************** YOUR NPC ***************************")
                    display_character(gender, name, profession, class_type, race, traits, quirk)
                    print("***************************************************************\n")
                    print("Would you like to save this character?")
                    if user_continue_option():
                        save_character(gender, name, profession, class_type, race, traits, quirk)
                except Exception as e:
                    print(e)
            if option == 2:
                try:
                    print("\n******************* CUSTOM CHARACTER BUILDER *******************")
                    gender = select_gender()
                    name = select_name(gender)
                    profession = select_profession()
                    class_type = select_class()
                    race = select_race()
                    traits = select_traits()
                    quirk = select_quirk()
                    print("***************************************************************")
                    print("\n************************** YOUR NPC ***************************")
                    display_character(gender, name, profession, class_type, race, traits, quirk)
                    print("***************************************************************\n")
                    print("Would you like to save this character?")
                    if user_continue_option():
                        save_character(gender, name, profession, class_type, race, traits, quirk)
                except Exception as e:
                    print(e)
            if option == 3:
                print("\n********************** SAVED CHARACTERS ***********************")
                list_bucket_objects()
                print("***************************************************************\n")
            if option == 4:
                print("\n******************** DOWNLOAD A CHARACTER *********************")
                download_object()
                print("***************************************************************\n")
            if option == 5:
                print("\n********************* DELETE A CHARACTER **********************")
                print("Deleted characters are permanently erased and cannot be \n"\
                    "restored. Would you like to continue?")
                if user_continue_option():
                    delete_object()
                print("***************************************************************\n")
            if option == 6:
                print("\n******************** DELETE ALL CHARACTERS ********************")
                print("Deleted characters are permanently erased and cannot be \n"\
                    "restored. Are you sure you want to do this?")
                if user_continue_option():
                    empty_bucket()
                print("***************************************************************\n")
            if option == 0:
                # Exit application
                print("\n************************** GOOD BYE ***************************")
                print("*  Thank you for using the NPC Builder application            *")
                print("***************************************************************\n")
                sys.exit()
            # Error handling (invalid integer)
            if option < 0 or option > 6:
                logging.error("User entered an invalid input at the main menu.")
                print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print("!  Invalid number entered.                                    !")
                print("!  Please enter a number corresponding to a menu option.      !")
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        # Error handling (not an integer)
        except Exception as err:
            logging.error("User entered an invalid input at the main menu.")
            logging.error(err)
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!  Invalid user entry.                                        !")
            print("!  Please enter a number corresponding to a menu option.      !")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

if __name__ == '__main__':
    main()
