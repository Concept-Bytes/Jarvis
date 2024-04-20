

#This is an example for a later tutorial of how I trigger actions based on the response from Jarvis
#This simply prints things out if he says any of these commands
#I use this method for triggering 3d prints, laser cutting, and other things
def parse_command(command):
    if command == "print":
        print("Hello World!")
    elif command == "light_on":
        print("Turning on the light")
    elif command == "light_off":
        print("Turning off the light")
    elif command == "exit":
        print("Exiting program")
        exit()
    else:
        print("Invalid command") 