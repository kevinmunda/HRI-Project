import time
import threading
import random

from pepper import Pepper
from Tablet.app import FlaskApp
from global_ import *
from utils import resetFlags


def main():
    # VARIABLES
    robot = Pepper()
    tablet = FlaskApp()
    app_thread = threading.Thread(target=tablet.run)

    serviceKeys = ['faceRegistrationFlag', 'faceRecognitionFlag', 'orderFlag', 'gameFlag']
    registrationKeys = ['registration', 'register']
    recognitionKeys = ['recognition', 'recognize']
    gameKeys = ['game', 'play']
    orderKeys = ['order']
    endKeys = ['quit', 'leave']

    yesKeys = ['yes', 'Yes']
    noKeys = ['no', 'No']

    firstInteraction = True

    # STARTING
    # Run in parallel the web application
    app_thread.start()
    time.sleep(1)

    # Welcome the customer
    robot.say(welcome1, 1)
    robot.say(welcome2, 1)

    while True:
        if flagDict['interactionFlag']:
            if firstInteraction:
                robot.say(interaction1, 1)
                robot.say(interaction2, 1)
                robot.say(leave, 1)
                firstInteraction = False
            else:
                robot.say(interaction3, 1)
            while all(not flagDict[key] for key in serviceKeys):
                # Listen the user request
                sentence = robot.fake_asr()
                if sentence == '':
                    continue
                else:
                    # Classify the request
                    words = sentence.split()
                    if any(w in registrationKeys for w in words):
                        flagDict['faceRegistrationFlag'] = True
                        break
                    if any(w in recognitionKeys for w in words):
                        flagDict['faceRecognitionFlag'] = True
                        break
                    if any(w in orderKeys for w in words):
                        flagDict['orderFlag'] = True
                        break
                    if any(w in gameKeys for w in words):
                        flagDict['gameFlag'] = True
                        break
                    if any(w in endKeys for w in words):
                        flagDict['quitFlag'] = True
                        break
                    # If the request is not understood
                    robot.say(random.choice(randomReplies), 1)

            # FACE REGISTRATION
            if flagDict['faceRegistrationFlag']:
                # Start face registration taking a picture
                robot.say(registration1, 1)
                robot.say(registration2, 1)
                # Wait until the picture is taken and confirmed
                while not flagDict['photoTakenFlag'] and not flagDict['menuFlag']:
                    pass
                # The user returns to the menu
                if flagDict['menuFlag']:
                    resetFlags(flagDict)
                    continue
                # Photo taken
                robot.say(registration3, 1)
                while not flagDict['photoConfirmedFlag'] and not flagDict['menuFlag']:
                    pass
                if flagDict['menuFlag']:
                    resetFlags(flagDict)
                    continue
                # Photo confirmed
                robot.say(registration4, 1)
                # Get user's name and confirm name
                while not flagDict['nameFlag'] and not flagDict['menuFlag']:
                    sentence = robot.fake_asr()
                    if sentence == '':
                        continue
                    else:
                        words = sentence.split()
                        # We suppose that the entry is just the name
                        name = words[0]
                        robot.say(str(name) + ', right?', 1)
                        robot.say(registration6, 1)
                        while True:
                            sentence = robot.fake_asr()
                            if sentence == '':
                                continue
                            else:
                                words = sentence.split()
                                break
                        if any(w in yesKeys for w in words):
                            flagDict['nameFlag'] = True
                            flagDict['name'] = str(name)
                        elif any(w in noKeys for w in words):
                            robot.say(registration7, 1)
                if flagDict['menuFlag']:
                    resetFlags(flagDict)
                    continue
                # Get user's surname and confirm surname
                robot.say(registration5, 1)
                while not flagDict['surnameFlag'] and not flagDict['menuFlag']:
                    sentence = robot.fake_asr()
                    if sentence == '':
                        continue
                    else:
                        words = sentence.split()
                        # We suppose that the entry is just the surname
                        surname = words[0]
                        robot.say(str(surname) + ', right?', 1)
                        robot.say(registration6, 1)
                        while True:
                            sentence = robot.fake_asr()
                            if sentence == '':
                                continue
                            else:
                                words = sentence.split()
                                break
                        if any(w in yesKeys for w in words):
                            flagDict['surnameFlag'] = True
                            flagDict['surname'] = str(surname)
                        elif any(w in noKeys for w in words):
                            robot.say(registration8, 1)
                if flagDict['menuFlag']:
                    resetFlags(flagDict)
                    continue
                # Wait confirm of the data
                robot.say(registration9, 1)
                while not flagDict['dataConfirmedFlag'] and not flagDict['menuFlag']:
                    pass
                if flagDict['menuFlag']:
                    resetFlags(flagDict)
                    continue
                # End registration
                flagDict['name'] = False
                flagDict['surname'] = False
                resetFlags(flagDict)
                time.sleep(1)
                robot.say(registration10, 1)

            # FACE RECOGNITION
            if flagDict['faceRecognitionFlag']:
                recognitionCounter = 0
                # Start face recognition
                robot.say(recognition1, 1)
                while not flagDict['faceConfirmedFlag'] and not flagDict['menuFlag']:
                    # Wait until a match in the database is found
                    while not flagDict['faceMatchedFlag'] and not flagDict['menuFlag']:
                        time.sleep(1)
                        recognitionCounter += 1
                        if recognitionCounter >= 5:
                            break
                        pass
                    if not flagDict['faceMatchedFlag']:
                        robot.say(recognition4, 1)
                        continue
                    if flagDict['faceMatchedFlag']:
                        name = flagDict['name']
                        surname = flagDict['surname']
                        robot.say("Are you " + name + " " + surname + "?", 1)
                        robot.say(recognition2, 1)
                        # Wait the user to retry or confirm
                        while not flagDict['faceRetryFlag'] and not flagDict['faceConfirmedFlag'] and not flagDict['menuFlag']:
                            pass
                        if flagDict['faceRetryFlag']:
                            flagDict['faceRetryFlag'] = False
                            flagDict['faceMatchedFlag'] = False
                            continue
                        if flagDict['menuFlag']:
                            break
                    if flagDict['menuFlag']:
                        break
                if flagDict['menuFlag']:
                    resetFlags(flagDict)
                    continue
                # End recognition
                resetFlags(flagDict)
                #flagDict['name'] = name
                #flagDict['surname'] = surname
                time.sleep(1)
                robot.say(recognition3, 1)

            # ORDER
            if flagDict['orderFlag']:
                if not flagDict['name']:
                    robot.say(order1, 1)
                    robot.say(order2, 1)
                else:
                    robot.say(order1bis + flagDict['name'], 1)
                    robot.say(order2bis, 1)
                while not flagDict['orderConfirmedFlag'] and not flagDict['menuFlag']:
                    pass
                if flagDict['menuFlag']:
                    resetFlags(flagDict)
                    continue
                # Order confirmed
                resetFlags(flagDict)
                time.sleep(1)
                robot.say(order3, 1)

            # GAME
            if flagDict['gameFlag']:
                robot.say(game1, 1)
                robot.say(game2, 1)
                simulationList = [robot.simulateLion, robot.simulateBear,
                                  robot.simulateElephant, robot.simulateMonkey]
                correctAnswerList = ['lion', 'bear', 'elephant', 'monkey']
                while not flagDict['menuFlag']:
                    choice = None
                    if flagDict['repeatGameFlag']:
                        flagDict['repeatGameFlag'] = False
                        if choice is None:
                            robot.say(game11, 1)
                    if flagDict['startGameFlag']:
                        flagDict['startGameFlag'] = False
                        choice = random.choice([0, 1, 2, 3])
                        simulationList[choice]()
                        correct_answer = correctAnswerList[choice]
                        robot.say(game3, 1)
                        while not flagDict['gameAnswerFlag'] and not flagDict['menuFlag']\
                                and not flagDict['startGameFlag']:
                            sentence = robot.fake_asr()
                            if sentence == '':
                                pass
                            else:
                                words = sentence.split()
                                if any(w == correct_answer for w in words):
                                    flagDict['gameAnswerFlag'] = True
                                    flagDict['gameCorrectAnswer'] = correct_answer
                                    robot.say(random.choice(gameCorrectAnswer), 1)
                                else:
                                    robot.say(random.choice(gameWrongAnswer), 1)
                            if flagDict['repeatGameFlag']:
                                flagDict['repeatGameFlag'] = False
                                simulationList[choice]()
                        if flagDict['gameAnswerFlag']:
                            robot.say(game10, 1)
                        flagDict['gameAnswerFlag'] = False
                        if flagDict['menuFlag']:
                            break
                if flagDict['menuFlag']:
                    resetFlags(flagDict)
                    continue

            # QUIT INTERACTION
            if flagDict['quitFlag']:
                resetFlags(flagDict)
                robot.say(bye, 1)
                flagDict['interactionFlag'] = False
                break

    # CLOSING APPLICATION
    robot.quit()


if __name__ == '__main__':
    main()
