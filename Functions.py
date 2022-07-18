from sys import stderr
from Classes import Dop, Vigsel
import json
import sys
import pandas as pd
import csv
import os
import shutil
import datetime
import pdf_form

def loadSettings(conf="settings.json", confpriests="priests.json", confparishes="parishes.json"):
    global priests
    global parishes

    global settings

    priests  = {}
    parishes = {}

    settings = {}

    try:
        with open(confpriests, "r", encoding="utf-8") as file:
            priests = json.loads(file.read())
        
        with open(confparishes, "r", encoding="utf-8") as file:
            parishes = json.loads(file.read())

        with open(conf, "r", encoding="utf-8") as file:
            settings = json.loads(file.read())

    except IOError as e:
        print(e, file=sys.stderr)

def loadData(file):
    events = []
    try:
        excel = pd.read_excel(file)
        tempcsv = "temp.csv"
        excel.to_csv(tempcsv, encoding="utf-8", index=False)
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
                                (row[settings["headers"]["P1FirstName"]], row[settings["headers"]["P1LastName"]]),
                                (row[settings["headers"]["P2FirstName"]], row[settings["headers"]["P2LastName"]])
                            )
                        )
                    )
                else:
                    print("Error: Type not recognized", file=sys.stderr)
                    continue
    except IOError as e:
        print(e, file=sys.stderr)
        exit(-1)
    finally:
        os.remove(tempcsv)

    return events

def writeCertificates(events):
    outputFolder = settings["directories"]["output"]
    jobPath = os.path.join(outputFolder, str(datetime.datetime.now()).replace(":", "-")[:22])
    os.makedirs(os.path.join(jobPath))

    formattedOutputs = []

    for event in events:
        templatePath = os.path.join(settings["directories"]["templates"], event.getTemplate())
        destinationPath = f"{event.date} - {event.type} - "

        if not os.path.exists(templatePath):
            print(f"Error processing {event}")
            print(f"Template {event.getTemplate()} in directory [{settings['directories']['templates']}] doesn't exist.")
            continue

        fieldValues = {}
        filename = f"{event.date} - {event.type}bevis - "

        if event.type == "Vigsel":
            destinationPath += f"{event.persons[0][1]}-{event.persons[1][1]}"
            os.makedirs(os.path.join(jobPath, destinationPath))

            filename += f"{event.persons[0][1]}-{event.persons[1][1]}.pdf"

            fieldValues.update({
                "Prästnamn": f"{event.priest[0]}, {event.priest[1]}",
                "Namn1": " ".join(event.persons[0]),
                "Namn2": " ".join(event.persons[1]),
                "Plats": f"{event.church}, {event.date.day}/{event.date.month} {event.date.year}",
            })

        elif event.type == "Dop":
            destinationPath += f"{event.firstName}"
            os.makedirs(os.path.join(jobPath, destinationPath))

            filename += f"{event.firstName}.pdf"

            fieldValues.update({
                "Prästnamn": f"{event.priest[0]}, {event.priest[1]}",
                "Namn": event.firstName,
                "Dopnamn": event.firstName,
                "Född": f"född den {event.birthDate.day}/{event.birthDate.month} {event.birthDate.year}, döptes den {event.date.day}/{event.date.month} {event.date.year}\ni {event.church}\noch tillhör Svenska kyrkan",
                "Faddrar": ""
            })

            if event.godparents:
                fieldValues.update({
                    "Faddrar": f"Faddrar\n{', '.join(event.godparents)}"
                })

                godparentTemplatePath = os.path.join(settings["directories"]["templates"], event.getGodparentTemplate())
                godparentFilename = f"{event.date} - Fadderbrev - {event.firstName} - "

                for godparent in event.godparents:
                    fieldValues["Faddernamn"] = godparent
                    pdf_form.update_form_values(godparentTemplatePath, os.path.join(jobPath, destinationPath, f"{godparentFilename} {godparent}.pdf"), fieldValues)
                    shutil.copy(os.path.join(settings["directories"]["templates"], "Att vara fadder.pdf"), os.path.join(jobPath, destinationPath, f"Att vara fadder - {godparent}.pdf"))
        else:
            continue
                
        destinationPath = os.path.join(jobPath, destinationPath, filename)

        formattedOutputs.append((templatePath, destinationPath, fieldValues, event))

    for entry in formattedOutputs:
        print(f"Writing: {entry[3]}")
        pdf_form.update_form_values(entry[0], entry[1], entry[2])