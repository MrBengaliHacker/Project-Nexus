from flask_socketio import SocketIO, emit

socketio = SocketIO(cors_allowed_origins="*")

# --- SocketIO event handlers ---

def register_socketio_events(app):
    @socketio.on('connect')
    def handle_connect():
        emit('connected', {'message': 'Connected to live feed!'})

    # Broadcast new post
    @socketio.on('new_post')
    def handle_new_post(data):
        emit('broadcast_new_post', data)

    # Broadcast new comment
    @socketio.on('new_comment')
    def handle_new_comment(data):
        emit('broadcast_new_comment', data)

    # Broadcast like
    @socketio.on('like_post')
    def handle_like_post(data):
        emit('broadcast_like_post', data)

    # Broadcast report
    @socketio.on('report_content')
    def handle_report_content(data):
        emit('broadcast_report_content', data)

    # You can add more events as needed

    socketio.init_app(app)
