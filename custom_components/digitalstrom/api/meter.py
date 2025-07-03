from .apartment import DigitalstromApartment
from .client import DigitalstromClient


class DigitalstromMeter:
    def __init__(
        self, client: DigitalstromClient, apartment: DigitalstromApartment, dsuid: str
    ):
        self.client = client
        self.dsuid = dsuid
        self.apartment = apartment
        self.name = ""
        self.manufacturer = ""
        self.model = ""
        self.serial = ""
        self.power_consumed = None
        self.energy_consumed = None
        self.energy_produced = None

    def load_from_dict(self, data: dict) -> None:
        if (dsuid := data.get("id")) and (dsuid == self.dsuid):
            if (name := data.get("name")) and (len(name) > 0):
                self.name = name
            if (manufacturer := data.get("manufacturer")) and (len(manufacturer) > 0):
                self.manufacturer = manufacturer
            if (model := data.get("model")) and (len(model) > 0):
                self.model = model
            if (serial := data.get("serial")) and (len(serial) > 0):
                self.serial = serial
            if (power_consumed := data.get("powerConsumed")) is not None:
                self.power_consumed = power_consumed
            if (energy_consumed := data.get("energyConsumed")) is not None:
                self.energy_consumed = energy_consumed
            if (energy_produced := data.get("energyProduced")) is not None:
                self.energy_produced = energy_produced
