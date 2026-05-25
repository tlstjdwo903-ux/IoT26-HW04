from flask import Flask, render_template, abort
from gpiozero import LED, Device
from gpiozero.pins.lgpio import LGPIOFactory
import atexit

# Raspberry Pi 5 대응
Device.pin_factory = LGPIOFactory()

app = Flask(__name__)

# BCM 번호 기준: GPIO 23, GPIO 24
leds = {
    23: LED(23),
    24: LED(24),
}

pins = {
    23: {"name": "GPIO 23", "state": 0},
    24: {"name": "GPIO 24", "state": 0},
}


def update_pin_states():
    for pin, led in leds.items():
        pins[pin]["state"] = 1 if led.is_lit else 0


@app.route("/")
def main():
    update_pin_states()

    templateData = {
        "pins": pins
    }

    return render_template("main.html", **templateData)


@app.route("/<int:changePin>/<action>")
def action(changePin, action):
    if changePin not in leds:
        abort(404)

    if action not in ["on", "off"]:
        abort(400)

    deviceName = pins[changePin]["name"]

    if action == "on":
        leds[changePin].on()
        message = f"Turned {deviceName} on."
    else:
        leds[changePin].off()
        message = f"Turned {deviceName} off."

    update_pin_states()

    templateData = {
        "pins": pins,
        "message": message
    }

    return render_template("main.html", **templateData)


@atexit.register
def cleanup():
    for led in leds.values():
        led.off()
        led.close()


if __name__ == "__main__":
    # port 80은 sudo 권한 필요함.
    # 개발 중에는 5000 추천.
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
