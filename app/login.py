from flask_login import LoginManager

a = mapped_column()

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    pass

