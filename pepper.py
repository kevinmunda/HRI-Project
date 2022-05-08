# File with all the functionalities of Pepper
# Sensor names to pass in the python 'touch_sym': HeadMiddle, LHand, RHand
# Simulate human speech: python human_say.py --sentence "SENTENCE"
# Simulate touch: python touch_sim.py --sensor SENSORNAME

import time, os
import threading
import qi

RED = "\033[1;31m"
BLUE = "\033[1;34m"
CYAN = "\033[1;36m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"
BOLD = "\033[;1m"
REVERSE = "\033[;7m"


class Pepper:

    def __init__(self):
        self.isConnected = False
        # Sensors
        self.headTouch = 0.0
        self.handTouch = [0.0, 0.0]  # left, right
        self.sonar = [0.0, 0.0]  # front, back
        self.language = "English"

        self.headTouchValue = "Device/SubDeviceList/Head/Touch/Middle/Sensor/Value"
        self.handTouchValues = ["Device/SubDeviceList/LHand/Touch/Back/Sensor/Value",
                           "Device/SubDeviceList/RHand/Touch/Back/Sensor/Value"]

        self.jointNames = ["HeadYaw", "HeadPitch", "LShoulderPitch",
                           "LShoulderRoll", "LElbowYaw", "LElbowRoll",
                           "LWristYaw", "RShoulderPitch", "RShoulderRoll",
                           "RElbowYaw", "RElbowRoll", "RWristYaw", "LHand",
                           "RHand", "HipRoll", "HipPitch", "KneePitch"]

        self.fakeASRkey = 'FakeRobot/ASR'
        self.fakeASRtimekey = 'FakeRobot/ASRtime'
        self.fakeASRevent = 'FakeRobot/ASRevent'

        # CONNECT THE ROBOT #
        self.pip = os.getenv('PEPPER_IP')
        self.port = 9559
        self.alive = False

        if self.isConnected:
            print("Robot already connected.")
            return

        print("Connecting to robot %s:%d ..." % (self.pip, self.port))
        try:
            connection_url = "tcp://" + self.pip + ":" + str(self.port)
            self.app = qi.Application(["Pepper command", "--qi-url=" + connection_url ])
            self.app.start()
        except RuntimeError:
            print("%sCannot connect to Naoqi at %s:%d %s" % (RED, self.pip, self.port, RESET))
            self.session = None
            return

        print("%sConnected to robot %s:%d %s" % (GREEN, self.pip, self.port, RESET))
        self.session = self.app.session

        # STARTING SERVICES #
        print("Starting services...")
        self.memory_service = self.session.service("ALMemory")
        self.motion_service = self.session.service("ALMotion")
        self.anspeech_service = self.session.service("ALAnimatedSpeech")
        self.touch_service = self.session.service("ALTouch")

        self.isConnected = True

        # EVENT LISTENER
        self.touch = self.memory_service.subscriber("TouchChanged")
        self.touch_id = self.touch.signal.connect(self.onTouch)
        self.asr = self.memory_service.subscriber(self.fakeASRevent)
        self.asr_id = self.asr.signal.connect(self.onASR)

        eventHandlerThread = threading.Thread(target=self.app.run)
        eventHandlerThread.start()

    def quit(self):
        time.sleep(1)
        print("Quit Pepper Robot...")
        time.sleep(0.5)
        self.app.stop()

    # REACTION TO TOUCH #
    def onTouch(self, value):
        self.touch.signal.disconnect(self.touch_id)
        self.headTouch = self.memory_service.getData(self.headTouchValue)
        self.handTouch[0] = self.memory_service.getData(self.handTouchValues[0])
        self.handTouch[1] = self.memory_service.getData(self.handTouchValues[1])
        sensor_values = [self.headTouch, self.handTouch[0], self.handTouch[1]]
        if any(val > 0.0 for val in sensor_values):
            #self.say("You touched me")
            touched_bodies = []
            print(value)
            for p in value:
                if p[1]:
                    touched_bodies.append(p[0])
            print(touched_bodies)
        self.touch_id = self.touch.signal.connect(self.onTouch)

    # REACTION TO SPEECH #
    def onASR(self, value):
        print("Human says: %s" % value)

    # SPEECH #
    def say(self, interaction, delay=0):
        print('Say: %s' % interaction)
        if self.anspeech_service is not None:
            configuration = {"bodyLanguageMode": "contextual"}
            self.anspeech_service.say(interaction, configuration)
            time.sleep(delay)

    def reset_fake_asr(self):
        self.memory_service.insertData(self.fakeASRkey, '')

    def fake_asr(self, timeout=3, activeListening=True):
        self.reset_fake_asr()
        if activeListening:
            self.say("I'm listening...", 1)
        time.sleep(timeout)
        sentence = self.memory_service.getData(self.fakeASRkey)
        print('Fake ASR: [%s]' % sentence)
        return sentence

    # ANIMATIONS #
    def simulateLion(self):
        jointNames = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll",
                      "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll"]
        jointValues = [-1, -1, 0.1, 1,   # Right Arm
                       -1, 1, -0.1, -1]  # Left Arm
        timeLists = 4.0
        self.motion_service.angleInterpolation(jointNames, jointValues, timeLists, True)
        self.say("ROOOOOOOARR", 1)

    def simulateBear(self):
        jointNames = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw",
                      "LShoulderPitch", "LShoulderRoll", "LElbowYaw",
                      "HipPitch"]
        jointValues = [-1, -0.5, -0.1,  # Right Arm
                       -1, 0.5, 0.1,    # Left Arm
                       -0.5]            # Hip
        timeLists = 5.0
        self.motion_service.angleInterpolation(jointNames, jointValues, timeLists, True)
        self.say("GROOOOWLLL", 1)

    def simulateElephant(self):
        jointNames = ["HeadPitch",  # Head
                      "RShoulderPitch", "RShoulderRoll", "RElbowYaw",  # Right Arm
                      "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll"]   # Left Arm
        jointValues = [-0.5,               # Head
                       -1, 1, -0.3,        # Right Arm
                       -1, -1, 0.1, -1]    # Left Arm
        timeLists = 5.0
        self.motion_service.angleInterpolation(jointNames, jointValues, timeLists, True)
        self.say("IIIIIHHIIIHIHH", 1)

    def simulateMonkey(self):
        jointNames = ["RShoulderRoll", "RElbowRoll", "RElbowYaw",
                      "LShoulderRoll", "LElbowRoll", "LElbowYaw",
                      "RHand", "LHand",
                      "HipPitch"]
        "LElbowRoll",
        jointValues = [-1, 0.8, 0.6,         # Right Arm
                       1, -0.8, -0.6,   # Left Arm
                       1, 1,
                       -1.3]             # Hands
        timeLists = 4.0
        self.motion_service.angleInterpolation(jointNames, jointValues, timeLists, True)
        self.say("UUU AAA UU AA", 1)

