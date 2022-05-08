from global_ import flagDict
from flask import Flask, render_template, request, Response, redirect, url_for
from utils import streamVideo, streamVideoRec, insertUser, readDatabase, readMenu, searchOrder, updateDatabase


class FlaskApp(object):
    def __init__(self, host='127.0.0.1', port=5000, debug=False):
        self.debug = debug
        self.port = port
        self.host = host
        self.app = Flask(__name__)

        # INDEX ROUTE
        self.app.add_url_rule(rule='/', endpoint='index',
                              view_func=self.index, methods=['GET'])
        # SERVICES ROUTE
        self.app.add_url_rule(rule='/services', endpoint='services',
                              view_func=self.services, methods=['GET', 'POST'])
        self.app.add_url_rule(rule='/menu', endpoint='menu',
                              view_func=self.menu, methods=['POST'])

        # FACE REGISTRATION ROUTES
        self.app.add_url_rule(rule='/video_feed', endpoint='video_feed',
                              view_func=self.video_feed, methods=['GET'])
        self.app.add_url_rule(rule='/faceRegistration', endpoint='faceRegistration',
                              view_func=self.faceRegistration, methods=['GET', 'POST'])
        self.app.add_url_rule(rule='/userRegistration', endpoint='userRegistration',
                              view_func=self.userRegistration, methods=['GET', 'POST'])
        self.app.add_url_rule(rule='/confirmData', endpoint='confirmData',
                              view_func=self.confirmData, methods=['POST'])

        # FACE RECOGNITION ROUTES
        self.app.add_url_rule(rule='/video_feed_rec', endpoint='video_feed_rec',
                              view_func=self.video_feed_rec, methods=['GET'])
        self.app.add_url_rule(rule='/faceRecognition', endpoint='faceRecognition',
                              view_func=self.faceRecognition, methods=['POST'])
        self.app.add_url_rule(rule='/getRecognitionFlags', endpoint='getRecognitionFlags',
                              view_func=self.getRecognitionFlags, methods=['GET', 'POST'])
        self.app.add_url_rule(rule='/confirmIdentity', endpoint='confirmIdentity',
                              view_func=self.confirmIdentity, methods=['POST'])

        # ORDER ROUTES
        self.app.add_url_rule(rule='/order', endpoint='order',
                              view_func=self.order, methods=['GET', 'POST'])
        self.app.add_url_rule(rule='/getLastOrder', endpoint='getLastOrder',
                              view_func=self.getLastOrder, methods=['GET'])
        self.app.add_url_rule(rule='/confirmOrder', endpoint='confirmOrder',
                              view_func=self.confirmOrder, methods=['POST'])

        # GAME ROUTES
        self.app.add_url_rule(rule='/game', endpoint='game',
                              view_func=self.game, methods=['GET', 'POST'])
        self.app.add_url_rule(rule='/gameServices', endpoint='gameServices',
                              view_func=self.gameServices, methods=['GET', 'POST'])
        self.app.add_url_rule(rule='/gameAnswer', endpoint='gameAnswer',
                              view_func=self.gameAnswer, methods=['GET'])

        # SHUTDOWN ROUTE
        self.app.add_url_rule(rule='/shutdown', endpoint='shutdown',
                              view_func=self.shutdown, methods=['POST'])

    def run(self):
        self.app.config['TEMPLATES_AUTO_RELOAD'] = True
        self.app.run(host=self.host, port=self.port,
                     threaded=True, debug=self.debug)

    # VARIOUS
    def index(self):
        return render_template("index.html")

    def services(self):
        if request.method == 'POST':
            flagDict['interactionFlag'] = True
            return render_template("services.html")
        elif request.method == 'GET':
            if flagDict['faceRegistrationFlag']:
                return 'faceReg'
            elif flagDict['faceRecognitionFlag']:
                return 'faceRec'
            elif flagDict['orderFlag']:
                return 'order'
            elif flagDict['gameFlag']:
                return 'game'
            else:
                return 'false'

    def menu(self):
        flagDict['menuFlag'] = True
        if flagDict['name']:
            name = flagDict['name']
        else:
            name = None
        return render_template('services.html', name=name)

    def shutdown(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        print("Shutting down the server...")
        return redirect(url_for('index'))

    # FACE REGISTRATION
    def video_feed(self):
        return Response(streamVideo(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    def faceRegistration(self):
        if request.method == 'POST':
            flagDict['faceRegistrationFlag'] = True
            return render_template("faceRegistration.html")
        elif request.method == 'GET':
            flagDict['photoTakenFlag'] = True
            return 'photoTaken'

    def userRegistration(self):
        if request.method == 'POST':
            flagDict['photoConfirmedFlag'] = True
            return render_template('userRegistration.html')
        elif request.method == 'GET':
            if flagDict['nameFlag'] and not flagDict['surnameFlag']:
                return flagDict['name']
            elif flagDict['nameFlag'] and flagDict['surnameFlag']:
                return flagDict['surname']
            else:
                return ""

    def confirmData(self):
        insertUser(flagDict)
        flagDict['dataConfirmedFlag'] = True
        return render_template('services.html')

    # FACE RECOGNITION
    def video_feed_rec(self):
        return Response(streamVideoRec(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    def faceRecognition(self):
        if request.method == 'POST':
            flagDict['faceRecognitionFlag'] = True
            return render_template('faceRecognition.html')

    def getRecognitionFlags(self):
        if request.method == 'GET':
            if flagDict['faceMatchedFlag']:
                return 'faceMatch'
            else:
                return ""
        if request.method == 'POST':
            flagDict['faceRetryFlag'] = True
            return 'faceRetry'

    def confirmIdentity(self):
        flagDict['faceConfirmedFlag'] = True
        return render_template("services.html", name=flagDict['name'])

    # ORDER
    def order(self):
        if request.method == 'POST':
            flagDict['orderFlag'] = True
            return render_template('order.html', name=flagDict['name'])
        if request.method == 'GET':
            menu = readMenu()
            tmp = ""
            for elem in menu:
                tmp += elem + "/"
            tmp = tmp[:-1]
            return tmp

    def getLastOrder(self):
        if flagDict['name']:
            database = readDatabase()
            key = flagDict['name'] + flagDict['surname']
            lastOrder = searchOrder(database, key)
            if lastOrder == 'None':
                return ""
            else:
                menu = readMenu()
                lastOrder = lastOrder.split("/")
                indexList = ""
                for elem in lastOrder:
                    indexList += str(menu.index(elem)) + "-"
                indexList = indexList[:-1]
                return indexList
        else:
            return ""

    def confirmOrder(self):
        if flagDict['name']:
            menu = readMenu()
            dishes = request.form.getlist('dish')
            lastOrder = ""
            for elem in dishes:
                tmp = menu[int(elem)]
                lastOrder += tmp + "/"
            lastOrder = lastOrder[:-1]
            updateDatabase(flagDict['name'], flagDict['surname'], lastOrder)
        flagDict['orderConfirmedFlag'] = True
        return render_template("services.html", name=flagDict['name'])

    # GAME
    def game(self):
        if request.method == 'POST':
            flagDict['gameFlag'] = True
            return render_template('game.html')
        else:
            return ""

    def gameServices(self):
        if request.method == 'POST':
            flagDict['repeatGameFlag'] = True
            return ""
        if request.method == 'GET':
            flagDict['startGameFlag'] = True
            return ""

    def gameAnswer(self):
        if request.method == 'GET':
            if flagDict['gameAnswerFlag']:
                return flagDict['gameCorrectAnswer']
            else:
                return ''
        else:
            return ''

