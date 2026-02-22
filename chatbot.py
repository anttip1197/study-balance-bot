from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route('/')
def serve_index():
    return send_from_directory('', 'index.html')

# Add your existing routes here

if __name__ == '__main__':
    app.run()