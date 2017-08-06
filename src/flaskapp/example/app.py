from flask import Flask
application = Flask(__name__)

from .db import Database
db = Database()


@application.route('/')
def index():
    print('Hit on /')
    return 'Hello World!'

@application.route('/<name>')
def greet(name):
    print('Hit on /<name> name={}'.format(name))
    db.set('name', name)
    return 'Hello {}!'.format(db.get('name'))

if __name__ == '__main__':
    application.run(host='0.0.0.0', port='8080')
