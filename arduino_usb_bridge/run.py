import os
import time
import threading
import serial
import requests


SERIAL_PORT = "/dev/ttyUSB1"
BAUDRATE = 115200

HA_URL = "http://supervisor/core/api"
HA_TOKEN = os.environ.get("SUPERVISOR_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}


digital_states = {}
analog_states = {}


def ha_set_state(entity_id, state, attributes=None):

    data = {
        "state": state
    }

    if attributes:
        data["attributes"] = attributes

    try:

        response = requests.post(
            f"{HA_URL}/states/{entity_id}",
            headers=HEADERS,
            json=data,
            timeout=5
        )

        print(
            "HA:",
            entity_id,
            "=",
            state,
            response.status_code
        )

    except Exception as error:

        print(
            "HA ERROR:",
            error
        )


def create_entities():

    print("Creating Arduino entities...")

    for pin in range(2, 14):

        entity_id = f"binary_sensor.arduino_d{pin}"

        ha_set_state(
            entity_id,
            "off",
            {
                "friendly_name": f"D{pin}",
                "device_class": "connectivity"
            }
        )

    for pin in range(6):

        entity_id = f"sensor.arduino_a{pin}"

        ha_set_state(
            entity_id,
            "0",
            {
                "friendly_name": f"A{pin}",
                "unit_of_measurement": "V"
            }
        )


def process_line(line):

    print(
        "Arduino:",
        line
    )

    if ":" not in line:
        return

    name, value = line.split(
        ":",
        1
    )

    name = name.strip()
    value = value.strip()

    if name.startswith("D"):

        try:

            pin = int(name[1:])
            state = int(value)

        except ValueError:

            return

        if 2 <= pin <= 13:

            digital_states[pin] = state

            entity_id = (
                f"binary_sensor.arduino_d{pin}"
            )

            ha_set_state(
                entity_id,
                "on" if state else "off",
                {
                    "friendly_name": f"D{pin}",
                    "device_class": "connectivity"
                }
            )

    elif name.startswith("A"):

        try:

            pin = int(name[1:])
            value = int(value)

        except ValueError:

            return

        if 0 <= pin <= 5:

            analog_states[pin] = value

            entity_id = (
                f"sensor.arduino_a{pin}"
            )

            ha_set_state(
                entity_id,
                str(value),
                {
                    "friendly_name": f"A{pin}",
                    "unit_of_measurement": "raw",
                    "state_class": "measurement"
                }
            )


def main():

    print("================================")
    print(" Arduino USB Bridge")
    print("================================")

    print(
        "Opening:",
        SERIAL_PORT
    )

    while True:

        try:

            ser = serial.Serial(
                SERIAL_PORT,
                BAUDRATE,
                timeout=1
            )

            print(
                "Arduino connected!"
            )

            create_entities()

            while True:

                line = ser.readline()

                if not line:
                    continue

                line = line.decode(
                    "utf-8",
                    errors="ignore"
                ).strip()

                if line:

                    process_line(
                        line
                    )

        except Exception as error:

            print(
                "Serial ERROR:",
                error
            )

            time.sleep(5)


if __name__ == "__main__":

    main()
