import app.roles as roles
import pytest


# Sample classes
class User(roles.Role):
    def __init__(self, username):
        self.username = username


class Admin(User):
    pass


# Sample users
u = User('CiccioGamer89')
a = Admin('Zeb89')

current_user = None

# Role manager
role_manager = roles.RoleManager()
role_manager.set_role_loader(lambda: current_user)


def callback():
    print(' Not authorized!')


@role_manager.roles(User, unauthorized_callback=callback)
def user_only():
    print('User only function!')


@role_manager.roles(Admin, unauthorized_callback=callback)
def admin_only():
    print('Admin only function!')


def test_correctness():
    global current_user
    current_user = u
    user_only()
    current_user = a
    user_only()
    admin_only()


def test_unauthorized():
    global current_user
    current_user = None
    user_only()
    current_user = u
    admin_only()
