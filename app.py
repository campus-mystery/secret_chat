import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from supabase import create_client, Client

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Supabase client
SUPABASE_URL = "https://oymqwovofxphcaxnhbpx.supabase.co"
SUPABASE_KEY = "sb_publishable_-A_HLSE2qGpReaw9voxx1w_eQ-2WVVZ"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Special usernames that get full history access
ALLOWED_FULL_ACCESS = {'wife', 'hubby', 'sai'}


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

    # 1. Insert message into Supabase DB
    supabase.table('messages').insert(msg_data).execute()

    # 2. Broadcast to all active clients
    emit('receive_message', msg_data, broadcast=True)


@socketio.on('request_history')
def handle_history_request(data):
    user_name = (data.get('username') or '').strip().lower()

    # If username is 'wife', 'hubby', or 'sai', fetch ALL messages
    if user_name in ALLOWED_FULL_ACCESS:
        response = (
            supabase.table('messages')
            .select('username, message, time')
            .order('id', desc=False)
            .execute()
        )
        chat_history = response.data
    else:
        # Otherwise, fetch only the last 20 messages
        response = (
            supabase.table('messages')
            .select('username, message, time')
            .order('id', desc=True)
            .limit(20)
            .execute()
        )
        # Reverse to display in chronological order (oldest to newest)
        chat_history = response.data[::-1]

    emit('load_history', chat_history)


if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
