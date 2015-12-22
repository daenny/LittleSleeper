# import required libraries
import RPi.GPIO as GPIO
import subprocess, time

# setup the GPIO pins for the halt switch
HALT_SWITCH_GPIO_PIN = 25

GPIO.setmode(GPIO.BCM)
GPIO.setup(HALT_SWITCH_GPIO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
time.sleep(0.5)

print "FinnCam: started and now waiting for GPIO halt button to be pressed."

# wait for the button to be pressed and when pressed, issue
# the halt command to stop the raspberry pi
while True:
        try:
                GPIO.wait_for_edge(HALT_SWITCH_GPIO_PIN, GPIO.FALLING)
                print "FinnCam: Shutdown switch pressed - halting system."
                subprocess.call(["sudo", "halt"])
        except KeyboardInterrupt:
                print "Stopped by user"
                GPIO.cleanup()
        except:
                continue
