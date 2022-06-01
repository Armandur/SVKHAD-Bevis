import Functions

if __name__ == "__main__":
    Functions.loadSettings()
    events = Functions.loadData("Export.xlsx")
    Functions.writeCertificates(events)