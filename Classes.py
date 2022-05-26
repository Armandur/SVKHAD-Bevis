import datetime

class Event:
    def __init__(self, date, church, priest):
        if date is str:
            self.date = datetime.date.fromisoformat(date)
        else:
            self.date = date
        self.church = church
        self.priest = priest

    def season(self):
        from main import settings
        seasons = settings["seasons"]

        if self.date.month >= 1 and self.date.month < seasons["spring"]: # winter
            return "winter"

        elif self.date.month >= seasons["spring"] and self.date.month < seasons["summer"]: # spring
            return "spring"

        elif self.date.month >= seasons["summer"] and self.date.month < seasons["autumn"]: # summer
            return "summer"

        elif self.date.month >= seasons["autumn"] and self.date.month < seasons["winter"]: # autumn
            return "autumn"

        elif self.date.month >= seasons["winter"] and self.date.month <= 12: # winter
            return "winter"

class Dop(Event):
    def __init__(self, date, church, priest, firstName, birthDate, godparents=[]):
        super().__init__(date, church, priest)
        self.firstName = firstName  # of dopkandidat
        self.birthDate = birthDate  # of dopkandidat
        self.godparents = godparents
        if godparents:
            self.god_parents = godparents.split(",")

    def season(self):
        return super().season()


class Vigsel(Event):
    def __init__(self, date, church, priest, persons):
        super().__init__(date, church, priest)
        self.persons = persons  # tuple of persons marrying

    def season(self):
        return super().season()