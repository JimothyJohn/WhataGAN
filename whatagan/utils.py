#!/usr/bin/python
import requests     # HTTP requests
import shutil
import os
from time import sleep
from bs4 import BeautifulSoup
import argparse
import json
from pymongo import MongoClient

MONGO_PEM = os.environ.get("MONGO_PEM")
MONGO_STRING = os.environ.get("MONGO_STRING")

key = os.environ.get("STREETVIEW_API_KEY")


def SaveStreetView(filename, params):
    rootURL = "https://maps.googleapis.com/maps/api/streetview"
    params["key"] = key,

    res = requests.get(rootURL, params=params, stream=True)
    sleep(0.2)

    if res.status_code == 200:
        with open(f"{filename}", 'wb') as f:
            shutil.copyfileobj(res.raw, f)
            f.close()
    else:
        print('Image Couldn\'t be retrieved')


def getPage(url):
    ''' returns a soup object that contains all the information
    of a certain webpage'''
    result = requests.get(url)
    sleep(0.1)
    content = result.content
    return BeautifulSoup(content, "html.parser")


def getArgs():
    # Create argument parser for dry runs / testing
    parser = argparse.ArgumentParser(
        description="Generate artificial Whataburgers")
    parser.add_argument(
        "--samples",
        type=int,
        default=100,
        help="Number of samples to grab from page.",
    )
    parser.add_argument(
        "--input-file",
        type=str,
        help="Metadata JSON file",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./stores",
        help="Image output directory",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="test.json",
        help="Metadata output filename",
    )
    parser.add_argument(
        "--museum",
        type=str,
        help="Museum to peruse",
    )
    parser.add_argument(
        "--artist",
        type=str,
        default="",
        help="Artist name",
    )
    parser.add_argument(
        "--medium",
        type=str,
        default="",
        help="Art format",
    )
    parser.add_argument(
        "--classification",
        type=str,
        default="",
        help="Style of art",
    )
    return parser.parse_args()


def getMetadata(output_dir):
    '''
    Extract all Whataburger store metadata
    '''
    # Create output directories if needed
    if not os.path.exists(f"{output_dir}"):
        os.mkdir(f"{output_dir}")
    if not os.path.exists(f"{output_dir}/metadata"):
        os.mkdir(f"{output_dir}/metadata")

    rootURL = "https://locations.whataburger.com/"

    collection = get_collection()
    existingStores = [item["number"] for item in collection.find()]
    category_index = collection.create_index("number")

    # Get BS4 object from webpage
    stateDirectory = getPage(F"{rootURL}directory.html")
    # Find all state URLs
    stateSlugs = stateDirectory.findAll(
        "a", {"class": ["Directory-listLink"]}
    )

    for state in stateSlugs:
        state = state.attrs["href"]
        # Skip weird URLs
        if len(state) > 8:
            continue

        # Get state symbol (ex. "TX")
        stateSymbol = state.split(".")[0].upper()

        cityDirectory = getPage(f"{rootURL}{state}")
        citySlugs = cityDirectory.findAll(
            "a", {"class": "Directory-listLink"}
        )
        for city in citySlugs:
            city = city.attrs["href"]
            # Extract city name (Ex. "Dallas")
            cityName = city.split("/")[1].split(".")[0].title()
            storeDirectory = getPage(f"{rootURL}{city}")
            # First look for multiple addresses
            addresses = storeDirectory.findAll(
                "span", {"class": "c-address-street-1"}
            )

            # Extra store numbers from page
            numbers = storeDirectory.find(
                "span", {"id": "location-name"})

            # If first method fails try others
            if numbers is None:
                numbers = storeDirectory.findAll(
                    "span", {"class": "locationName-displayName"})
            else:
                addresses = [addresses[0]]

            if len(numbers) == 0:
                numbers = storeDirectory.findAll(
                    "span", {"class": "LocationName-displayName"})

            for number, address in zip(numbers, addresses):
                # Extract store number as integer
                storeNumber = int(number.text.split(" #")[1].strip())

                # DB Schema
                # Reformat address for Google API query
                # (ex. 123+First+St+City+ST)
                params = {
                    "query": f"Whataburger+{address.text.replace(' ', '+')},{cityName},{stateSymbol}",
                    "address": f"{address.text}",
                    "city": f"{cityName}",
                    "state": f'{stateSymbol}',
                    "number": storeNumber,
                    "oresent": False,
                    "size": "600x600",
                    "heading": [0, 340],
                    "fov": [60, 90],
                    "pitch": [8, 12],
                }

                if storeNumber in existingStores:
                    continue

                print(
                    f"Store {storeNumber} is in {params['address'].replace('+',' ')},{cityName},{stateSymbol}")
                collection.insert_one(params)
                '''
                with open(f"{output_dir}/metadata/{storeNumber}.json", "w") as f:
                    f.write(json.dumps(params))
                    f.close()

                for angle in range(12):
                    params["heading"] = angle * 30
                    SaveStreetView(
                        f"{output_dir}/images/{address}/{params['heading']}.jpg", params)
                '''


def ExtractParams(params):
    return {
        "location": params["location"],
        "size": params["size"],
    }


def getImages(output_dir):
    for fileName in sorted(os.listdir(f"{output_dir}/metadata"))[:10]:
        with open(f"{output_dir}/metadata/{fileName}", "r") as f:
            params = json.load(f)
            f.close()

        if os.path.exists(f"{output_dir}/images/{params['number']}"):
            print(f"Skipping store {params['number']}")
            # continue
        else:
            os.mkdir(f"{output_dir}/images/{params['number']}")

        queryParams = {
            "location": params["location"],
            "size": params["size"],
        }

        for degrees in range(params["heading"][0], params["heading"][1], 60):
            queryParams["heading"] = degrees
            for zoom in range(params["fov"][0], params["fov"][1], 5):
                print(f"Zoom: {zoom}")
                queryParams["fov"] = zoom
                for angle in range(params["pitch"][0], params["pitch"][1]):
                    queryParams["pitch"] = angle
                    print(queryParams)
                    SaveStreetView(
                        f"{output_dir}/images/{params['number']}/h={degrees},z={zoom},a={angle}.jpg", queryParams)


def get_collection():
    client = MongoClient(f"{MONGO_STRING}",
                         tls=True,
                         tlsCertificateKeyFile=f"{MONGO_PEM}")

    db = client['Whataburger']
    return db['stores']
