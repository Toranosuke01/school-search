import googlemaps
import settings

key = settings.API_KEY


class AddressFormatting:
    def __init__(self, address):
        self.address = address
        self.gmaps = googlemaps.Client(key=key)
        res = self.gmaps.geocode(address)
        ll = res[0]["geometry"]["location"]
        self.lat = ll["lat"]
        self.lng = ll["lng"]

    def get_prefecture(self):
        reverse_geocode_result = self.gmaps.reverse_geocode(
            (self.lat, self.lng),
            language="ja",
            result_type="administrative_area_level_1",
        )
        prefecture = reverse_geocode_result[0]["address_components"][0]["long_name"]
        return prefecture

    def get_municipality(self):
        reverse_geocode_result = self.gmaps.reverse_geocode(
            (self.lat, self.lng), language="ja", result_type="sublocality"
        )
        municipality = ""
        sublocality = ""
        for component in reverse_geocode_result[0]["address_components"]:
            if "sublocality" in component["types"]:
                sublocality = component["long_name"]
            elif "locality" in component["types"]:
                municipality = component["long_name"]
            compo = f"{municipality}{sublocality}"
        return compo
