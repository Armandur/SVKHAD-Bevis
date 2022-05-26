from sys import stderr
from Classes import Event, Dop, Vigsel
import json
import sys
import pandas as pd
import csv
import os
import datetime

priests  = {}
parishes = {}

settings = {}


def loadSettings(conf="settings.json", confpriests="priests.json", confparishes="parishes.json"):
    global priests
    global parishes

    global settings

    try:
        with open(confpriests, "r", encoding="utf-8") as file:
            priests = json.loads(file.read())
        
        with open(confparishes, "r", encoding="utf-8") as file:
            parishes = json.loads(file.read())

        with open(conf, "r", encoding="utf-8") as file:
            settings = json.loads(file.read())

    except IOError as e:
        print(e, file=sys.stderr)

loadSettings()

def loadData(file):
    events = []
    try:
        excel = pd.read_excel(file)
        tempcsv = "temp.csv"
        excel.to_csv(tempcsv,encoding="utf-8", index=False)
        with open(tempcsv, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=settings["delimiter"], quotechar=settings["quotechar"])

            #Check if all settings["headers"] are in reader.fieldnames
            check = all(item in reader.fieldnames for item in list(settings["headers"].values()))
            if not check:
                print(f"Error: Missing headers in '{file}'", file=sys.stderr)
                csvfile.close()
                os.remove(tempcsv)
                exit(1)

            for row in reader:
                date = datetime.datetime.strptime(row[settings["headers"]["Date"]], "%Y-%m-%d").date()
                location = row[settings["headers"]["Location"]]
                priestcell = row[settings["headers"]["Priest"]]
                priest = (priestcell, priests[priestcell])
                type = row[settings["headers"]["Type"]]

                if type == "Dop":
                    birthDate = row[settings["headers"]["BornDate"]]
                    birthDate = datetime.datetime.strptime(birthDate, "%Y-%m-%d").date()
                    
                    events.append(
                        Dop(
                            date,
                            location,
                            priest,
                            row[settings["headers"]["BapName"]],
                            birthDate,
                            row[settings["headers"]["Godparents"]]
                        )
                    )

                elif type == "Vigsel":
                    events.append(
                        Vigsel(
                            date,
                            location,
                            priest,
                            (
                                row[settings["headers"]["P1FirstName"]]+" "+row[settings["headers"]["P1LastName"]],
                                row[settings["headers"]["P2FirstName"]]+" "+row[settings["headers"]["P2LastName"]]
                            )
                        )
                    )
                else:
                    print("Error: Type not recognized", file=sys.stderr)
                    continue

    except IOError as e:
        print(e, file=sys.stderr)

    os.remove(tempcsv)
    return events

def writeCertificates(events):

    return

events = loadData("Thord Hägglund.xlsx")

for event in events:
    if event.__class__.__name__ == "Dop":
        print(event.__class__.__name__ + " " + str(event.date) + " - " + event.church + " - " + event.firstName)
    elif event.__class__.__name__ == "Vigsel":
        print(event.__class__.__name__ + " - " + str(event.date) + " - " + event.church + " P1: " + event.persons[0] + " P2: " + event.persons[1])
