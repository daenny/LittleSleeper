import argparse
import ConfigParser
import os
from datetime import datetime
from multiprocessing.connection import Client

import tornado.gen
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket

##LED Light
# import required libraries
import RPi.GPIO as GPIO

# Variables
IRLED_PIN = 14
IRLED_STATUS = False
LED_PIN = 4
LED_STATUS = False

SERVO_PIN = 18
SERVO_STATUS = False

# setmodes
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, False)

GPIO.setup(IRLED_PIN, GPIO.OUT)
GPIO.output(IRLED_PIN, False)

GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, 50)

parser = argparse.ArgumentParser(description='Listens from the microphone, records the maximum volume and serves it to the web server process.')
parser.add_argument('--config', default='default.conf', dest='config_file', help='Configuration file', type=str)

class IRLedsOn(tornado.web.RequestHandler):
    def get(self):
        global IRLED_STATUS
        GPIO.output(IRLED_PIN, True)
        IRLED_STATUS=True

class IRLedsOff(tornado.web.RequestHandler):
    def get(self):
        global IRLED_STATUS
        GPIO.output(IRLED_PIN, False)
        IRLED_STATUS=False

class LedOn(tornado.web.RequestHandler):
    def get(self):
        global LED_STATUS
        GPIO.output(LED_PIN, True)
        LED_STATUS=True

class LedOff(tornado.web.RequestHandler):
    def get(self):
        global LED_STATUS
        GPIO.output(LED_PIN, False)
        LED_STATUS=False

class ServoOn(tornado.web.RequestHandler):
    def get(self):
        global SERVO_STATUS
        pwm.start(30)
        pwm.ChangeDutyCycle(30)
        SERVO_STATUS = True
        
class ServoOff(tornado.web.RequestHandler):
    def get(self):
        global SERVO_STATUS
        pwm.ChangeDutyCycle()
        SERVO_STATUS = False

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

clients = []

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print "New connection"
        clients.append(self)

    def on_close(self):
        print "Connection closed"
        clients.remove(self)


def broadcast_mic_data(audio_server, upper_limit, noise_threshold, min_quiet_time, min_noise_time):
    # get the latest data from the audio server
    parameters = {"upper_limit": upper_limit,
                  "noise_threshold": noise_threshold,
                  "min_quiet_time": min_quiet_time,
                  "min_noise_time": min_noise_time}
    conn = Client(audio_server)
    conn.send(parameters)
    results = conn.recv()
    conn.close()
    # print results
    # send results to all clients
    now = datetime.now()
    results['date_current'] = '{dt:%A} {dt:%B} {dt.day}, {dt.year}'.format(dt=now)
    results['time_current'] = now.strftime("%I:%M:%S %p").lstrip('0')
    results['audio_plot'] = results['audio_plot'].tolist()
    results['cur_value'] = str(results['cur_value'])
    if LED_STATUS:
        results['led_status'] = " An"
    else:
        results['led_status'] = " Aus"
    if IRLED_STATUS:
        results['irled_status'] = " An"
    else:
        results['irled_status'] = " Aus"

    if SERVO_STATUS:
        results['servo_status'] = " An"
    else:
        results['servo_status'] = " Aus"

    for c in clients:
        c.write_message(results)


def main(audio_server, listen_on, upper_limit, noise_threshold, min_quiet_time, min_noise_time):
    settings = {
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
    }
    app = tornado.web.Application(
        handlers=[
            (r"/", IndexHandler),
            (r"/ws", WebSocketHandler),
            (r"/ledon", LedOn),
            (r"/ledoff", LedOff),
            (r"/irledon", IRLedsOn),
            (r"/irledoff", IRLedsOff),
            (r"/servoon", ServoOn),
            (r"/servooff", ServoOff),
        ], **settings
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(listen_on[1], listen_on[0])
    print "Listening on port:", listen_on[1]
 
    main_loop = tornado.ioloop.IOLoop.instance()
    scheduler = tornado.ioloop.PeriodicCallback(lambda: broadcast_mic_data(audio_server, upper_limit, noise_threshold, min_quiet_time, min_noise_time), 1000, io_loop=main_loop)
    scheduler.start()
    main_loop.start()
    
if __name__ == '__main__':
    args = parser.parse_args()
    config = ConfigParser.SafeConfigParser()
    config_status = config.read(args.config_file)
    if not config_status:
        raise IOError("Configuration file '%s' not found." % (args.config_file,))

    try:
        main(
            (config.get('web_server', 'audio_server_host'), int(config.get('web_server', 'audio_server_port')),),
            (config.get('web_server', 'host'), int(config.get('web_server', 'port')),),
            int(config.get('web_server', 'upper_limit')),
            float(config.get('web_server', 'noise_threshold')),
            int(config.get('web_server', 'min_quiet_time')),
            int(config.get('web_server', 'min_noise_time')),
        )
    except KeyboardInterrupt:
	print "Stopped by user"
	GPIO.cleanup()

        

