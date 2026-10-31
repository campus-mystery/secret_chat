from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory message store (resets on server restart)
messages = []


@app.route('/')
def index():
  return render_template('index.html')


@socketio.on('send_message')
def handle_message(data):
  msg_data = {
      'username': data.get('username'),
      'message': data.get('message'),
      'time': data.get('time'),
  }
  messages.append(msg_data)
  emit('receive_message', msg_data, broadcast=True)


@socketio.on('connect')
def handle_connect():
  # Send existing chat history to the newly connected client
  emit('load_history', messages)


if __name__ == '__main__':
  socketio.run(app, debug=True, port=5000)
