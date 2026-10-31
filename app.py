from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from supabase import create_client, Client

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Supabase client
SUPABASE_URL = "https://oymqwovofxphcaxnhbpx.supabase.co"
SUPABASE_KEY = "sb_publishable_-A_HLSE2qGpReaw9voxx1w_eQ-2WVVZ"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/")
def index():
  return render_template("index.html")


@socketio.on("send_message")
def handle_message(data):
  msg_data = {
      "username": data.get("username"),
      "message": data.get("message"),
      "time": data.get("time"),
  }

  # Insert message into Supabase table
  try:
    supabase.table("messages").insert(msg_data).execute()
  except Exception as e:
    print(f"Error saving to Supabase: {e}")

  emit("receive_message", msg_data, broadcast=True)


@socketio.on("connect")
def handle_connect():
  # Fetch existing chat history from Supabase (ordered by oldest to newest)
  try:
    response = (
        supabase.table("messages")
        .select("username, message, time")
        .order("id", desc=False)
        .execute()
    )
    messages = response.data
  except Exception as e:
    print(f"Error fetching from Supabase: {e}")
    messages = []

  emit("load_history", messages)


if __name__ == "__main__":
  socketio.run(app, debug=True, port=5000)
