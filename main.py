import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import csv
import PySimpleGUI as sg
import os
import re
import pandas as pd

sg.theme('Topanga')   # Add a little color to your windows
# All the stuff inside your window. This is the PSG magic code compactor...
layout = [[sg.Text('Job'), sg.InputText(), ],

          [sg.Text('Area'), sg.InputText()],
          [sg.Text('Collect')],

          [sg.Checkbox('Name', default=True)],
          [sg.Checkbox('Phone', default=False)],
          [sg.Checkbox('Map URL', default=False)],
          [sg.Checkbox('Website', default=False)],
          [sg.Checkbox('Email', default=False)],
          [sg.Checkbox('Paid Listing', default=True)],
          [sg.Checkbox('Free Listing', default=True)],
          [sg.Checkbox('Sponor Listing (Only for XO)', default=True)],

          [sg.Text('Folder'), sg.In(size=(25, 1), enable_events=True,
                                    key='-FOLDER-'), sg.FolderBrowse()],

          [sg.Text('File Name'), sg.InputText()],

          [sg.Radio('Find on Vrisko', "radios", default=True, key='-ONE-')],
          [sg.Radio('Find on Xo', "radios", default=False, key='-TWO-')],
          [sg.Radio('Find on Visko and Xo. Save two different files',
                    "radios", default=False, key='-THREE-')],
          [sg.Radio('Find on Visko and Xo. Combine data to one file',
                    "radios", default=False, key='-FOUR-')],

          [sg.Button('Start'), sg.Cancel()]
          ]


def start(values):
    job = values[0]
    area = values[1]
    name = values[2]
    phone = values[3]
    map = values[4]
    website = values[5]
    email = values[6]
    paid = values[7]
    free = values[8]
    sponsor = values[9]
    folder = values['-FOLDER-']
    file = values[10]

    if values['-ONE-'] == True:
        vriskoData(job, area, free, paid, name, phone,
                   map, website, email, folder, file)
    if values['-TWO-'] == True:
        xoData(job, area, free, paid, sponsor, name,
               phone, map, website, email, folder, file)
    if values['-THREE-'] == True:
        vriskoData(job, area, free, paid, name, phone,
                   map, website, email, folder, file)
        xoData(job, area, free, paid, sponsor, name,
               phone, map, website, email, folder, file)
    if values['-FOUR-'] == True:
        vriskoData(job, area, free, paid, name, phone,
                   map, website, email, folder, file)
        xoData(job, area, free, paid, sponsor, name,
               phone, map, website, email, folder, file)
        viskoFile = folder + '/' + file + '-Vrisko.csv'
        xoFile = folder + '/' + file + '-XO.csv'
        mergedFile = folder + '/' + file + '-Vrisko-XO.csv'
        try:
            mergeFiles(viskoFile, xoFile, mergedFile)
        except:
            print("Can't merge the files")


def vriskoData(job, area, free, paid, name, phone, map, website, email, path, file):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
               'AppleWebKit/537.36 (KHTML, like Gecko) '
               'Chrome/75.0.3770.80 Safari/537.36'}

    URL = 'https://www.vrisko.gr/search/' + \
        urllib.parse.quote(job) + '/' + urllib.parse.quote(area) + '/'

    httpx = requests.get(URL, headers=headers)

    soup = BeautifulSoup(httpx.content, "html.parser")
    body = soup.find('body')
    pages = body.find('div', {"class": "pagerWrapper"})

    pages_array = []

    pages_array.append(URL)
    i = 0
    j = 0
    for i in range(3):
        try:
            for j in range(len(pages.find_all('a', {"class": "pageLink"}))):
                pages_array.append(URL + '?page=' + str(j+1))
            break
        except:
            print('Attempt...' + str(i) + '.. from 3')
            time.sleep(5)

    array = []

    fullPathUnedited = path + '\\' + file + 'UneditedVrisko.csv'
    fullPath = path + '\\' + file
    csvHeader = []

    if name:
        csvHeader.append('Όνομα')
    if phone:
        csvHeader.append('Τηλέφωνο')
    if map:
        csvHeader.append('Χάρτης')
    if website:
        csvHeader.append('Website')
    if email:
        csvHeader.append('Email')

    with open(fullPathUnedited, 'w+', encoding='utf-8') as f:
        print('Vrisko Scrapper Started')
        writer = csv.writer(f)
        writer.writerow(csvHeader)
        page_num = 0
        for page_num in range(len(pages_array)):
            page = pages_array[page_num]
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/75.0.3770.80 Safari/537.36'}

            httpx = requests.get(page, headers=headers)
            soup = BeautifulSoup(httpx.content, "html.parser")
            body = soup.find('body')

            paidClass = 'AdvItemBox'
            freeClass = 'FreeListingItemBox'

            array.clear()

            if free and paid:
                divs = body.findAll(True, {'class': [paidClass, freeClass]})

            elif free and not paid:
                divs = body.findAll(True, {'class': [freeClass]})
            else:
                divs = body.findAll(True, {'class': [paidClass]})
            for item in divs:
                array.clear()

                if name:
                    try:
                        name = item.find(
                            'h2', {"class": "CompanyName"}).get_text().strip()
                        array.append(name)
                    except:
                        array.append('No name')
                if phone:
                    try:
                        phone = getPhoneFromVrisko(item, body)
                        array.append(phone)
                    except:
                        array.append('No phone')

                if map:
                    try:
                        map = item.find('a', {"class": "siteLink"}).get(
                            'href').replace(' ', '-').strip()
                        array.append(map)
                    except:
                        array.append('No map')

                if website:
                    try:
                        website = item.find(
                            'meta', {"itemprop": "url"}).get('content')
                        array.append(website)
                    except:
                        array.append('No Website')

                if email:
                    try:
                        email = item.find(
                            'meta', {"itemprop": "email"}).get('content')
                        array.append(email)
                    except:
                        array.append('No email')

                writer.writerow(array)
            print('Vrisko Scrapper says: I\'m on page ' +
                  str(page_num) + ' out of ' + str(len(pages_array)))
            time.sleep(1)
    print("Vrisko Scrapper says: I finished gathering data.\n")
    clearData(fullPathUnedited, fullPath, '-Vrisko')


def xoData(job, area, free, sponsor, paid, name, phone, map, website, email, path, file):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
               'AppleWebKit/537.36 (KHTML, like Gecko) '
               'Chrome/75.0.3770.80 Safari/537.36'}

    URL = 'https://www.xo.gr/search/?what=' + \
        urllib.parse.quote(job) + '&where=' + urllib.parse.quote(area)

    httpx = requests.get(URL, headers=headers)

    soup = BeautifulSoup(httpx.content, "html.parser")
    body = soup.find('body')
    pages = body.find('div', {"class": "row pagination"}).find(
        'ul').find_all('li')

    pages.pop(0)
    pages_array = []

    i = 0
    j = 1
    for i in range(3):
        try:
            for link in pages:
                pages_array.append(URL + link.find('a').get('href'))
            break
        except:
            print('Attempt...' + str(i) + '...from 3')
            time.sleep(3)

    try:
        pages_array.pop()
    except:
        print('XO Scrapper says: I didnt found any pages. Please check your queries\n')
    pages_array.insert(0, URL)

    array = []

    fullPathUnedited = path + '\\' + file + 'UneditedXO.csv'
    fullPath = path + '\\' + file
    csvHeader = []

    if name:
        csvHeader.append('Όνομα')
    if phone:
        csvHeader.append('Τηλέφωνο')
    if map:
        csvHeader.append('Χάρτης')
    if website:
        csvHeader.append('Website')
    if email:
        csvHeader.append('Email')

    with open(fullPathUnedited, 'w+', encoding='utf-8') as f:
        print('XO Scrapper Started')
        writer = csv.writer(f)
        writer.writerow(csvHeader)
        page_num = 0
        for page_num in range(len(pages_array)):
            page = pages_array[page_num]
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/75.0.3770.80 Safari/537.36'}

            httpx = requests.get(page, headers=headers)
            soup = BeautifulSoup(httpx.content, "html.parser")
            body = soup.find('body')

            sponsorClass = 'span12 listing spListing links_list'
            paidClass = 'span12 listing paidListing links_list'
            freeClass = 'span12 listing freeListing links_list'

            array.clear()

            if free and paid and sponsor:
                divs = body.findAll(
                    True, {'class': [paidClass, freeClass, sponsorClass]})

            elif free and paid and not sponsor:
                divs = body.findAll(True, {'class': [freeClass, paidClass]})

            elif free and not paid and sponsor:
                divs = body.findAll(True, {'class': [freeClass, sponsorClass]})

            elif not free and paid and sponsor:
                divs = body.findAll(True, {'class': [paidClass, sponsorClass]})

            elif not free and paid and not sponsor:
                divs = body.findAll(True, {'class': [paidClass]})

            elif not free and not paid and sponsor:
                divs = body.findAll(True, {'class': [sponsorClass]})

            else:
                divs = body.findAll(True, {'class': [freeClass]})

            for item in divs:
                array.clear()

                if name:
                    try:
                        name = item.find(
                            'span', {"itemprop": "name"}).get_text().strip()
                        array.append(name)
                    except:
                        array.append('No name')
                if phone:
                    try:
                        phone = item.find(
                            'a', {"data-event-v2": "phone"}).get('href').replace('tel:+30', ' ')
                        array.append(phone)
                    except:
                        array.append('No phone')

                if map:
                    try:
                        map = item.find(
                            'a', {"data-event": "directions"}).get('href')
                        array.append(map)
                    except:
                        array.append('No map')

                if website:
                    try:
                        website = item.find(
                            'a', {"itemprop": "url"}).get('href')
                        array.append(website)
                    except:
                        array.append('No Website')

                if email:
                    try:
                        email = item.find('a', {"itemprop": "email"}).get(
                            'href').replace('mailto:', ' ')
                        array.append(email)
                    except:
                        array.append('No email')

                writer.writerow(array)
            print('XO Scrapper says: I\'m on page ' +
                  str(page_num) + ' out of ' + str(len(pages_array)))
            time.sleep(1)
    print("XO Scrapper says: I finished gathering data.\n")
    clearData(fullPathUnedited, fullPath, '-XO')


def clearData(fullPathUnedited, fullPath, fromSite):
    print(fromSite + "Scrapper says: I'm processing the data now.\n")
    with open(fullPathUnedited, 'r', encoding='utf-8') as in_file, open(fullPath + fromSite + '.csv', 'w', encoding='utf-8') as out_file:
        seen = set()  # set for fast O(1) amortized lookup
        for line in in_file:
            if line in seen:
                continue  # skip duplicate
            seen.add(line)
            out_file.write(line)

        in_file.close()
        out_file.close()
        os.remove(fullPathUnedited)
        print(fromSite + "Scrapper says: I've finished processing data.\n")


def getPhoneFromVrisko(item, body):
    try:
        phoneFunction = item.find(
            'div', {"class": "phoneLinkMarker"}).get('onclick')
        phoneID = re.findall(r"\((\d+)\)", phoneFunction)
        phone = body.find(
            'div', {"id": "phoneDetails_" + str(phoneID[0])}).find('label').get_text()
        return phone
    except:
        return False


def mergeFiles(viskoFile, xoFile, mergedFile):
    print('Merge started')
    vrisko = pd.read_csv(viskoFile)
    xo = pd.read_csv(xoFile)
    merged = pd.concat([vrisko, xo]).drop_duplicates(
        subset=['Όνομα', 'Τηλέφωνο']).reset_index(drop=True)
    merged.to_csv(mergedFile, index=False)
    os.remove(viskoFile)
    os.remove(xoFile)
    print('Merge finished')


# Create the Window
window = sg.Window('Scraper', layout)
# Event Loop to process "events"
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Cancel'):
        break
    if event == 'Start':
        start(values)
window.close()
