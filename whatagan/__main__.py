import json
from utils import SaveStreetView, getPage
from uuid import uuid4
import os


def getMetadata():
    if not os.path.exists(f"stores"):
        os.mkdir("stores")
    if not os.path.exists(f"stores/metadata"):
        os.mkdir("stores/metadata")
    if not os.path.exists(f"stores/images"):
        os.mkdir("stores/images")

    rootURL = "https://locations.whataburger.com/"

    stateDirectory = getPage(F"{rootURL}directory.html")
    stateSlugs = stateDirectory.findAll(
        "a", {"class": ["Directory-listLink"]}
    )

    for state in stateSlugs:
        state = state.attrs["href"]
        # Skip weird URL's
        if len(state) > 8:
            continue

        stateSymbol = state.split(".")[0].upper()

        print(stateSymbol)
        cityDirectory = getPage(f"{rootURL}{state}")
        citySlugs = cityDirectory.findAll(
            "a", {"class": "Directory-listLink"}
        )
        for city in citySlugs:
            city = city.attrs["href"]
            cityName = city.split("/")[1].split(".")[0].title()
            print(f"Querying {cityName}...")
            storeDirectory = getPage(f"{rootURL}{city}")
            addresses = storeDirectory.findAll(
                "span", {"class": "c-address-street-1"}
            )

            numbers = storeDirectory.find(
                "span", {"id": "location-name"})

            if numbers is None:
                numbers = storeDirectory.findAll(
                    "span", {"class": "locationName-displayName"})
            else:
                addresses = [addresses[0]]

            if len(numbers) == 0:
                numbers = storeDirectory.findAll(
                    "span", {"class": "LocationName-displayName"})

            for number, address in zip(numbers, addresses):
                storeNumber = int(number.text.split(" #")[1].strip())
                address = address.text.replace(" ", "+")
                # storeNumber = number.text.split(" # ")[1]

                params = {
                    "location": f"Whataburger+{address},{cityName},{stateSymbol}",
                    "uuid": uuid4().hex,
                    "number": storeNumber,
                    "oresent": False,
                    "size": "600x600",
                    "heading": [0, 340],
                    "fov": [60, 90],
                    "pitch": [8, 12],
                }

                address = address.replace("+", " ")

                if not os.path.exists(f"stores/images/{storeNumber}"):
                    os.mkdir(f"stores/images/{storeNumber}")

                if os.path.exists(f"stores/metadata/{storeNumber}.json"):
                    continue

                print(
                    f"Store {storeNumber} is in {address},{cityName},{stateSymbol}")
                with open(f"stores/metadata/{storeNumber}.json", "w") as f:
                    f.write(json.dumps(params))
                    f.close()

                '''
                for angle in range(12):
                    params["heading"] = angle * 30
                    SaveStreetView(
                        f"stores/images/{address}/{params['heading']}.jpg", params)
                '''


def ExtractParams(params):
    return {
        "location": params["location"],
        "size": params["size"],
    }


def getImages():
    for fileName in sorted(os.listdir(f"stores/metadata"))[:10]:
        with open(f"stores/metadata/{fileName}", "r") as f:
            params = json.load(f)
            f.close()

        if os.path.exists(f"stores/images/{params['number']}"):
            print(f"Skipping store {params['number']}")
            # continue
        else:
            os.mkdir(f"stores/images/{params['number']}")

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
                        f"stores/images/{params['number']}/h={degrees},z={zoom},a={angle}.jpg", queryParams)


def ChangeValues(param, values):
    for fileName in sorted(os.listdir(f"stores/metadata")):
        with open(f"stores/metadata/{fileName}", "r") as f:
            print(f"Filename: {fileName}")
            params = json.load(f)
            f.close()

        params[param] = [values[0], values[1]]
        with open(f"stores/metadata/{fileName}", "w") as f:
            f.write(json.dumps(params))
            f.close()


if __name__ == "__main__":
    getImages()
