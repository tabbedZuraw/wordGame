#!/usr/bin/python
from flask import Flask, render_template, request, redirect,  url_for, session
from operator import itemgetter
import random
import time
import pickle

app = Flask(__name__)


def getWord():
    words = [line.strip() for line in open('wordsLow.txt')]
    randWord = (random.choice(words))
    return randWord


def allUnique(x):
    seen = set()
    return not any(i in seen or seen.add(i) for i in x)


def containsAll(s_word, word):

	s_charlist = list(s_word)

	for c in word:
		if c in s_charlist:
			s_charlist.remove(c)
		else:
			return False
	return True


@app.route('/')
def main_Screen():
    sessionId = random.randrange(1,1000)
    return render_template('gameWindow.html',
                           sessionId = sessionId)


@app.route('/gameStart', methods=['POST'])
def game_start():
    sessionId = request.form['sessionId']
    session['time'] = time.time()
    passCon = 0
    while (passCon  < 1):
        session['mainWord'] = getWord()
        if len(session['mainWord']) >= 7:
            passCon = 2
    return render_template('newGame.html',
                           title='Welcome',
                           header="Your word is: " + session['mainWord'],
                           time = session['time'],
                           value= session['mainWord'],
                           sessionId = sessionId)


@app.route('/calculate', methods=['POST'])
def calculate_data():
    errors = []
    errorList = []
    sessionId = request.form['sessionId']
    wordList = request.form.getlist('field[]')
    session['score'] = time.time() - float(session['time'])
    result = [s for s in wordList if not s.strip(session['mainWord'])]
    if not result:
        an_item = dict(typeOfError='Letters used are not in the source word: ', cause=' '.join(result))
        errors.append(an_item)


    for word in wordList:
        if containsAll(session['mainWord'],word) == False:
            an_item = dict(typeOfError='Letters used are not in the source word: ', cause= word)
            errors.append(an_item)


    for element in wordList:
        if not len(element) >= 3:
            an_item = dict(typeOfError='Word entered is too short:', cause = element)
            errors.append(an_item)


    words = [line.strip() for line in open('wordsLow.txt')]
    if not(set(wordList) <= set(words)) == True:
        error = (set(wordList)-set(words))
        an_item = dict(typeOfError='Words entered are not valid :', cause = ' '.join(error))
        errors.append(an_item)


    wordSet = set(wordList)
    if session['mainWord'] in wordSet:
        an_item = dict(typeOfError='One or more words entered are same as the source word: ', cause = session['mainWord'])
        errors.append(an_item)


    if allUnique(wordList) == False:
        an_item = dict(typeOfError='Not all entered words are unique', cause= ' ')
        errors.append(an_item)


    if not errors:
        return redirect(url_for('list_result',
                                sessionId = sessionId,
                                time = session['score']))

    else:
        return render_template('errors.html',
                                title='Unlucky',
                                header= 'List of errors',
                                errors = errors,
                                sessionId = sessionId)


@app.route('/result')
def list_result():
    sessionId= request.args.get('sessionId', '')
    try:
        session['scoreBoard'] = pickle.load(open("scores.pickle","rb"))

    except EOFError:
        w=1


    session['scoreBoard'].append((' ',session['score']))
    session['scoreBoard'] = sorted(session['scoreBoard'], key=itemgetter(1))
    playerData = [x for x, y in enumerate(session['scoreBoard']) if y[1] == session['score']]
    session['rank'] = playerData[0] +1
    playerData = session['scoreBoard'][int(playerData[0])]
    if playerData in session['scoreBoard'][:10]:
        return render_template('enterName.html',
                                title='Congratulations',
                                header='You have made it to the TOP10',
                                time = session['score'],
                                rank = session['rank'],
                                sessionId = sessionId)

    else:
         return render_template('enterName.html',
                                title='Unlucky',
                                header='Unfortunelly, this time have not made it to the top',
                                time = session['score'],
                                rank = session['rank'],
                                sessionId = sessionId)


@app.route('/scoreBoard', methods=['POST'])
def list_scores():
    items = []
    sessionId = request.form['sessionId']
    playerName = request.form['name']
    playerIndex = [x for x, y in enumerate(session['scoreBoard']) if y[1] == session['score']]
    playerData = session['scoreBoard'].pop(int(playerIndex[0]))
    fullPlayerData = (playerName, playerData[1])
    session['scoreBoard'].append(fullPlayerData)
    session['scoreBoard'] = sorted(session['scoreBoard'], key=itemgetter(1))
    with open('scores.pickle', 'wb') as handle:
        pickle.dump(session['scoreBoard'] , handle)


    for i in range(len(session['scoreBoard'] )):
        temp = session['scoreBoard'] [i]
        an_item = dict(name=temp[0], score=temp[1])
        items.append(an_item)


    return render_template('result.html',
                            items=items,
                            sessionId = sessionId)


app.secret_key = 'thisismysecretsecretsecretkey'


if __name__ == '__main__':
    app.run(debug=True)
