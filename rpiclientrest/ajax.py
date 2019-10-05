from flask import Flask, render_template, jsonify



application = Flask(__name__)
application.secret_key = 'some_secret'
async_mode = None




def home():
    return render_template('ajax.html')

application.add_url_rule('/', view_func=home)


@application.route('/test', methods=['POST'])
def test():
    return jsonify({'text': 'value'})


if __name__ == '__main__':
    application.run()
