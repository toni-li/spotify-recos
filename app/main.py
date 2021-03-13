# from flask import Flask
# app= Flask(__name__)
# @app.route('/')
# def index():
#   return "<h1>Welcome to CodingX</h1>"


from flask import Flask, render_template, request
from .process_data import process


app = Flask(__name__)


@app.route("/")
def home():
    return render_template('web-app.html')


@app.route('/get_data', methods=['POST'])
def get_data():
    username = request.form['user-name']
    song = request.form['song']

    print("Spotify Username: " + username)
    print("URL of the song you want to recommend: " + song)

    message = process_data.process(username, song)

    return render_template('success.html', message=message)


# if __name__ == "__main__":
#     app.run(port=5000, debug=True)





































