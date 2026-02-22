from flask import Flask, render_template

app = Flask(__name__)

@app.route('/chat')
def chat():
    return "Chat endpoint"

@app.route('/audio/<filename>")
def audio(filename):
    return "Audio endpoint for: " + filename

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()