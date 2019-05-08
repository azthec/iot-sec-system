# IoT Security System PoC

Uses multiple Arduinos equipped with WiFi shields, infrared distance sensors, accelerometers and piezoelectric sensors to detect when doors are opened and when the equipment is interfered with.

Wireless communication with HTTP SSL. Provides a basic UI via pyQT.

## Create cert using
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout mycert.pem -out mycert.pem

