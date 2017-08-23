"""
ZenWheels protocol specification

Notes:
 * Messages are 2 bytes and specify a channel and a value
 * Channels are 7 bit unsigned, high bit is set
 * Values are 7 bit signed, high bit is clear
 * Maximum packet size is 128 bytes
"""

# Bluetooth service UUID
CAR_UUID = '00001101-0000-1000-8000-00805F9B34FB'

# Steering channel (send only)
# 0x00      = straight
# 0x01-0x3f = right turn (max is 0x3f)
# 0x40-0x7f = left turn  (max is 0x40)
STEERING = 0x81

# Throttle channel (send only)
# 0x00      = stop
# 0x01-0x3f = forward (max is 0x3f)
# 0x40-0x7f = reverse (max is 0x40)
# Use values of at least 4 to avoid stalling
THROTTLE = 0x82

# Left/right signal channels (send only)
LEFT_SIGNAL  = 0x83
RIGHT_SIGNAL = 0x84
SIGNAL_OFF          = 0x00
SIGNAL_FRONT_BRIGHT = 0x01
SIGNAL_FRONT_DIM    = 0x02
SIGNAL_REAR_BRIGHT  = 0x04
SIGNAL_REAR_DIM     = 0x08

# Headlight channel (send only)
HEADLIGHT = 0x85
HEADLIGHT_OFF    = 0x00
HEADLIGHT_DIM    = 0x01
HEADLIGHT_BRIGHT = 0x02

# Horn channel (send only)
HORN = 0x86
HORN_OFF = 0x00
HORN_ON  = 0x01

# Effects channel (send only)
EFFECTS = 0x87
EFFECTS_OFF           = 0x00
EFFECTS_GLOW          = 0x01
EFFECTS_PULSATE       = 0x02
EFFECTS_POLICE_HILO   = 0x03
EFFECTS_POLICE_WAIL   = 0x04
EFFECTS_POLICE_SILENT = 0x05

# Volume channel (send only)
# Volume level = (1 + (value / 7)) * 10%
# Current setting is stored in EEPROM
VOLUME = 0x89
VOLUME_10  = 0x00
VOLUME_20  = 0x07
VOLUME_30  = 0x0e
VOLUME_40  = 0x15
VOLUME_50  = 0x1c
VOLUME_60  = 0x23
VOLUME_70  = 0x2a
VOLUME_80  = 0x31
VOLUME_90  = 0x38
VOLUME_100 = 0x3f

# Hall effect sensor channel (receive only)
HALL_SENSOR = 0x8a
HALL_SENSOR_OFF = 0x00
HALL_SENSOR_ON  = 0x01

# Battery channel (receive only)
# Battery voltage = value / 10
BATTERY = 0xc0

# Firmware channel (send/receive)
# Querying DEVICEID_LSB also triggers a shutdown
FIRMWARE = 0xc1
FIRMWARE_VERSION_LSB   = 0x00
FIRMWARE_VERSION_MSB   = 0x01
FIRMWARE_DEVICEID_LSB  = 0x02
FIRMWARE_DEVICEID_MSB  = 0x03
FIRMWARE_EXPANSION_LSB = 0x04
FIRMWARE_EXPANSION_MSB = 0x05

# Shutdown channel (receive only)
SHUTDOWN = 0xc2
SHUTDOWN_CAR_OFF        = 0x00
SHUTDOWN_LOW_VOLTAGE    = 0x01
SHUTDOWN_FIRMWARE_ERROR = 0x02
SHUTDOWN_CAR_TIMEOUT    = 0x04
SHUTDOWN_STEERING_ERROR = 0x07
