import json
from datetime import datetime

import random
import mqtt_device
import paho.mqtt.client as paho
from paho.mqtt.client import MQTTMessage
from config_parser import parse_config


class CarPark(mqtt_device.MqttDevice):
    """Creates a carpark object to store the state of cars in the lot"""

    def __init__(self, config):
        super().__init__(config)
        self.total_spaces = config['total-spaces']
        self.total_cars = config['total-cars']
        self.client.on_message = self.on_message
        self.client.subscribe('sensor')
        self.client.loop_forever()
        self._temperature = None

    @property
    def available_spaces(self):
        available = self.total_spaces - self.total_cars
        return max(available, 0)

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        self._temperature = random.choice(range(10, 40))

    def _publish_event(self):
       readable_time = datetime.now().strftime('%H:%M')
       data = {
           'time': readable_time,
           'space': self.available_spaces,
           'temperature': self.temperature
       }
       message = json.dumps(data)
       self.client.publish('display', message)

    def on_car_entry(self):
        self.total_cars += 1
        self._publish_event()

    def on_car_exit(self):
        self.total_cars -= 1
        self._publish_event()

    def on_message(self, client, userdata, msg: MQTTMessage):
        payload = msg.payload.decode()
        data = json.loads(payload)
        # TODO: Extract temperature from payload

        self.temperature = data['temperature']
        if 'exit' in payload:
            self.on_car_exit()
        else:
            self.on_car_entry()


if __name__ == '__main__':
    # TODO: Read config from file
    config = parse_config()
    car_park = CarPark(config)


