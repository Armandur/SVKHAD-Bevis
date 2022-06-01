import datetime
import Functions

class Event:
    def __init__(self, date, church, priest):
        if type(date) == str:
            self.date = datetime.date.fromisoformat(date)
        else:
            self.date = date
        self.church = church
        self.priest = priest
        self.type = self.__class__.__name__
        self.__parish__ = getParish(self.church)

    def season(self):
        seasons = Functions.settings["seasons"]

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
    
    def getTemplate(self):
        return f"{self.__parish__} {self.type.lower()} {Functions.settings['seasonsSV'][self.season()]}.pdf"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__} - {self.date} - {self.church} - {self.priest}"


class Dop(Event):
    def __init__(self, date, church, priest, firstName, birthDate, godparents=[]):
        super().__init__(date, church, priest)
        self.firstName = firstName  # of dopkandidat
        self.birthDate = birthDate  # of dopkandidat
        self.godparents = godparents
        if godparents:
            self.godparents = godparents.split(", ")

    def season(self):
        return super().season()
    
    def getTemplate(self):
        return super().getTemplate()
    
    def getGodparentTemplate(self):
        return f"{self.__parish__} {Functions.settings['typesSV']['godparent']} {Functions.settings['seasonsSV'][self.season()]}.pdf"

    def __repr__(self) -> str:
        return f"{super().__repr__()} - {self.firstName}, {self.birthDate} - {self.godparents}"


class Vigsel(Event):
    def __init__(self, date, church, priest, persons):
        super().__init__(date, church, priest)
        self.persons = persons  # tuple of name-tuples of persons marrying (("1_FirstName", "1_LastName"), ("2_FirstName", "2_LastName"),)

    def season(self):
        return super().season()
    
    def getTemplate(self):
        return super().getTemplate()

    def __repr__(self) -> str:
        return f"{super().__repr__()} - {self.persons}"


def getParish(church, short=True):
    from Functions import parishes
    
    for parish in parishes:
        for _church in parishes[parish]["churches"]:
            if church == _church:
                if short:
                    return parish
                else:
                    return parishes[parish]["name"]
    return "ALLM"