import unittest
import os
import json
import tempfile

import app



class BasicTestCase(unittest.TestCase):

    def test_index(self):
        """Ensure Flask is running"""
        tester = app.app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_database(self):
        """Ensure DB exists"""
        tester = os.path.exists('flaskr.db')
        self.assertTrue(tester)


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()
        app.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE'])

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    # Asserts
    def test_db_is_blank(self):
        """Ensure that the DB is blank when we start"""
        rv = self.app.get('/')
        assert b'No entries yet' in rv.data

    def test_login_logout_success(self):
        """Log in and log out with correct username and password"""
        rv = self.login(
            app.app.config['USERNAME'],
            app.app.config['PASSWORD']
        )
        assert b'You were logged in' in rv.data
        rv = self.logout()
        assert b'You were logged out' in rv.data

    def test_login_failure(self):
        """Log in with incorrect username and password"""
        rv = self.login(
            app.app.config['USERNAME'] + 'x',
            app.app.config['PASSWORD']
        )
        assert b'Invalid username' in rv.data
        rv = self.login(
            app.app.config['USERNAME'],
            app.app.config['PASSWORD'] + 'x'
        )
        assert b'Invalid password' in rv.data

    def test_user_can_post_messages(self):
        """Ensure that users can post messages"""
        self.login(
            app.app.config['USERNAME'],
            app.app.config['PASSWORD']
        )
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert b'No entries yet' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data

    def test_user_can_delete_message(self):
        """Ensure that messages can be deleted"""
        rv = self.app.get('/delete/1')
        data = json.loads((rv.data).decode('utf-8'))
        self.assertEqual(data['status'], 1)


if __name__ == '__main__':
    unittest.main()
