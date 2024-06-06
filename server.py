from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

cors = CORS(app, resources={r"/": {"origins": "*"}}) 
socketio = SocketIO(app, cors_allowed_origins="*") 

@socketio.on('connect')
def test_connect():
    emit('response', {'data': 'Connected'}, broadcast=True, headers={"Access-Control-Allow-Origin": "*"})

queue = []  # Переменная для хранения очереди

@app.route('/')
def index():
    return render_template('index.html', queue=queue)

@socketio.on('enqueue')
def handle_enqueue(data):
    name = data['name']
    queue.append(name)
    emit('queue_update', queue, broadcast=True)

@socketio.on('dequeue')
def handle_dequeue():
    if queue:
        first_user = queue.pop(0)
        queue.append(first_user)
        emit('queue_update', queue, broadcast=True)
        emit('play_sound', broadcast=True)  # Отправить команду на проигрывание звука всем клиентам

@socketio.on('remove')
def handle_remove(data):
    user_to_remove = data['name']
    if user_to_remove in queue:
        queue.remove(user_to_remove)
        emit('queue_update', queue, broadcast=True)

@socketio.on('get_queue')
def handle_get_queue():
    emit('queue_update', queue)  # Отправить текущее состояние очереди при запросе

if __name__ == '__main__':
     socketio.run(app, host='0.0.0.0', port=5001, debug=True)
