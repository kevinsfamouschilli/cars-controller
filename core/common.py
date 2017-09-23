''' CONFIG '''

# Number of milliseconds to sleep in the bluetooth loop
bt_loop_sleep = 25

# Whether or not to open CV window which shows position of cars on screen
cvDataWindow = True

''' END CONFIG '''


''' GLOBAL VARIABLES '''
# List of MAC addresses to connect to
addresses = []
    
# List of currently connected cars
cars = []

# Whether the communication threads are running
bt_running = True

# Whether or not the CV is connected to the socket and providing data
cv_running = False



''' COMMON FUNCTIONS '''
