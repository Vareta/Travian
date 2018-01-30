import random

import requests
from bs4 import BeautifulSoup
from datetime import time

url = 'https://ts19.travian.com/'  # Travian url
url_login = 'https://ts19.travian.com/dorf1.php'  # Travian login url
login_form = {'name': 'Your User',  # User name
              'password': 'Your Password',  # Password
              's1': 'Login',
              'w': '1920%3A1080', # Display resolution
              'login': '1517228549'  # Input value from login button (you need to extract this from the page)
              }
# Romans troops names. You must change it according to your race
troops_type_list = ['Legionnaires',
                    'Praetorians',
                    'Imperians',
                    'Equites Legati',
                    'Equites Imperatoris',
                    'Equites Caesaris',
                    'Battering Rams',
                    'Fire catapults',
                    'Senator',
                    'Settler'
                    ]
# Your village from where you need to calculate your total troops. This are the villages id.
villages_id_list = ['555', '12896']

session = requests.Session()


def create_troops_dictionary():
    """
    Create a dictionary with the troops list
    :return: Tropps Dictionarie
    """
    troops_dictionary = {}
    for troop_type in troops_type_list:
        troops_dictionary[troop_type] = 0

    return troops_dictionary


def login(url):
    """
    Carry out the identification process
    :param url: Main url from travian server
    """
    global session
    session.get(url)
    cookies_dict = session.cookies.get_dict()
    request = requests.Request('POST', url_login, data=login_form, cookies=cookies_dict)
    prepped = request.prepare()
    response = session.send(prepped)


def connect(url):
    """
    Carry out the process of access to a travian page when you are already logged
    :param url: url you want to access
    :return: Response object resultant from the action
    """
    request = requests.Request('GET', url, cookies=session.cookies.get_dict())
    prepped = request.prepare()
    response = session.send(prepped)

    return response


def get_incoming_troops(village_id):
    """
    Make the process of listing all the troops that are returning to the village.
    :param village_id: Integer who represent the village id
    :return: List of html tables with all the incoming troops
    """
    incoming_units_table_list = []
    page_number = 1
    while page_number > 0:
        incoming_url = 'https://tx3.travian.us/build.php?newdid=' + village_id + '&gid=16&tt=1&filter=1&subfilters=2' \
                                                                                 '&page=' + str(page_number)
        response = connect(incoming_url)
        page = BeautifulSoup(response.content.decode('latin-1'), 'lxml')
        incoming_troops_tables = page.find_all('table', class_='troop_details inReturn')
        for troop_table in incoming_troops_tables:
            unit_table = troop_table.find(class_='units last').find_all('td')
            incoming_units_table_list.append(unit_table)
        end_of_list = page.find(class_='next disabled')
        if end_of_list is not None:
            page_number = 0
        else:
            page_number = page_number + 1

        # Apply a random time pause, in this way we don't do to much consecutive requests to the page in the same second
        time(random.randint(1, 3))

    return incoming_units_table_list


def get_outgoing_troops(village_id):
    """
    Make the process of listing all the troops that are leaving the village.
    :param village_id: Integer who represent the village id
    :return: List of html tables with all the outgoing troops
    """
    outgoing_units_table_list = []
    page_number = 1
    while page_number > 0:
        outgoing_url = 'https://tx3.travian.us/build.php?newdid=' + village_id + '&gid=16&filter=2&tt=1&subfilters=5,4&page=' + str(
            page_number)
        response = connect(outgoing_url)
        page = BeautifulSoup(response.content.decode('latin-1'), 'lxml')
        outgoing_troops_tables = page.find_all('table', class_='troop_details outRaid')
        for troop_table in outgoing_troops_tables:
            unit_table = troop_table.find(class_='units last').find_all('td')
            outgoing_units_table_list.append(unit_table)
        end_of_list = page.find(class_='next disabled')
        if end_of_list is not None:
            page_number = 0
        else:
            page_number = page_number + 1

        time(random.randint(1, 3))

    return outgoing_units_table_list


def get_unoccupied_troops(village_id, troops_dict):
    """
    List all the troops that are in the village at that time
    :param village_id: Integer who represent the village id
    :param troops_dict: Dictionary with the troops of the respective village
    :return: Dictionary with the troops of the respective village
    """
    unoccupied_url = 'https://tx3.travian.us/dorf1.php?newdid=' + village_id + '&'
    response = connect(unoccupied_url)
    page = BeautifulSoup(response.content.decode('latin-1'), 'lxml')
    troops_table = page.find(id='troops').find('tbody').find_all('tr')
    for troops in troops_table:
        troop_type = troops.find(class_='un').string
        for type in troops_type_list:
            if troop_type == type:
                troops_dict[type] = troops_dict[type] + int(troops.find(class_='num').string)

    return troops_dict


def get_troops_number(troops_table_list, troops_dict):
    """
    List all the troops form the troops table list generated in previous process
    :param troops_table_list: List that contains a list of html tables with the troops
    :param troops_dict: Dictionary with the troops of the respective village
    :return: Dictionary with the troops of the respective village
    """
    for troops_table in troops_table_list:
        count = 0
        for troop_item in troops_table:
            if count == 10:
                break
            if troop_item.string != '0':
                troops_dict[troops_type_list[count]] = troops_dict[troops_type_list[count]] + int(troop_item.string)
            count = count + 1

    return troops_dict


def get_data():
    login(url)  # Login process
    for village_id in villages_id_list:  # go through all villages
        troops_dict = create_troops_dictionary()
        troops_dict = get_unoccupied_troops(village_id, troops_dict)
        incoming_units_table_list = get_incoming_troops(village_id)
        outgoing_units_table_list = get_outgoing_troops(village_id)
        troops_dict = get_troops_number(incoming_units_table_list, troops_dict)
        troops_dict = get_troops_number(outgoing_units_table_list, troops_dict)
        print(village_id)
        print(troops_dict)


get_data()
