''' CONFIG '''

# Number of milliseconds to sleep in the bluetooth loop
bt_loop_sleep = 25

# List of MAC addresses to connect to
addresses = [
  '00:06:66:61:A9:59',  # MicroCar-89 (Orange)
  #'00:06:66:61:A3:48'   # MicroCar-72 (Red)
]

# Whether or not to open CV window which shows position of cars on screen
cvDataWindow = True

''' END CONFIG '''



''' GLOBAL VARIABLES '''
# List of currently connected cars
cars = []

# Whether the communication threads are running
bt_running = True

# Whether or not the CV is connected to the socket and providing data
cv_running = False



''' COMMON FUNCTIONS '''
