import subprocess

from user import User


def test_display():
    try:
        user = User(name='test_user', email='test_email@domain.com', password='test_password')
        print()
        user.display()
        assert True
    except:
        assert False


def test_edit():
    try:
        user = User(email='test_email@domain.com', password='test_password')
        user.edit(name='new_name', email='new_email@domain.com', password='new_password')
        assert user.name == 'new_name'
        assert user.email == 'new_email@domain.com'
        assert user.password == 'new_password'
    except:
        assert False


def teardown_module():
    subprocess.call('python dbsetup.py', shell=True)
