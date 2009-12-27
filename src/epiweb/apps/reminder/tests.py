import unittest
from datetime import datetime, timedelta, date

from django.contrib.auth.models import User

from mock import Mock, patch, patch_object

from epiweb.apps.reminder import send
from epiweb.apps.reminder.models import Reminder

class Base(unittest.TestCase):
    def _createUser(self, *args):
        for item in args:
            user = User()
            user.username = item
            user.email = '%s@example.com' % item
            user.password = 'password'
            user.save()

    def _removeUser(self, *args):
        for item in args:
            user = User.objects.get(username=item)
            user.delete()

    def _update(self, user, **kwargs):
        reminder = Reminder.objects.filter(user__username=user)[0]
        
        for key in kwargs:
            setattr(reminder, key, kwargs[key])

        reminder.save()

    def tearDown(self):
        items = User.objects.all()
        for item in items:
            item.delete()

        items = Reminder.objects.all()
        for item in items:
            item.delete()

class InsertTriggerTestCase(Base):
    def setUp(self):
        self._createUser('user01')

    def testReminder(self):
        items = Reminder.objects.filter(user__username='user01')
        self.assertEqual(len(items), 1)

class DeleteTriggerTestCase(Base):
    def setUp(self):
        self._createUser('user01')

    def testReminder(self):
        users = User.objects.all()
        reminders = Reminder.objects.all()
        nusers = len(users)
        nreminders = len(reminders)
        self.assertEqual(nusers, nreminders)

        user = User.objects.filter(username='user01')[0]
        user.delete()

        users = User.objects.all()
        reminders = Reminder.objects.all()
        self.assertEqual(len(reminders), len(users))

        self.assertEqual(len(reminders), nreminders-1)

class JustCreatedTestCase(Base):
    def setUp(self):
        self._createUser('user01')

    def testReminder(self):
        mock = Mock()
        @patch_object(send, 'send_mail', mock)
        def test():
            send.send_reminder()
        test()

        self.assertFalse(mock.called)

class OneWeekTestCase(Base):
    def setUp(self):
        now = datetime.now()

        self._createUser('user01')
        self._update('user01', 
                     last_reminder=now - timedelta(days=7),
                     next_reminder=now)

    def testReminder(self):
        mock = Mock()
        @patch_object(send, 'send_mail', mock)
        def test():
            send.send_reminder()
        test()

        self.assertTrue(mock.called)

        emails = mock.call_args[0][3]
        self.assertEqual(emails, ('user01@example.com',))

        reminder = Reminder.objects.filter(user__username='user01')[0]

        now = date.today()

        next = now + timedelta(days=7)
        self.assertEqual(reminder.next_reminder, next)

        # only compare the date
        last = reminder.last_reminder
        self.assertEqual(last.year, now.year)
        self.assertEqual(last.month, now.month)
        self.assertEqual(last.day, now.day)

class FiveDaysTestCase(Base):
    def setUp(self):
        now = datetime.now()

        self._createUser('user01')
        self._update('user01', 
                     last_reminder=now - timedelta(days=5),
                     next_reminder=now + timedelta(days=2))

    def testReminder(self):
        mock = Mock()
        @patch_object(send, 'send_mail', mock)
        def test():
            send.send_reminder()
        test()

        self.assertFalse(mock.called)

class LateReminderTestCase(Base):
    def setUp(self):
        now = datetime.now()

        self._createUser('user01')
        self._update('user01', 
                     wday=(now - timedelta(days=3)).weekday(),
                     last_reminder=now - timedelta(days=10),
                     next_reminder=now - timedelta(days=3))

    def testReminder(self):
        mock = Mock()
        @patch_object(send, 'send_mail', mock)
        def test():
            send.send_reminder()
        test()

        self.assertTrue(mock.called)

        emails = mock.call_args[0][3]
        self.assertEqual(emails, ('user01@example.com',))

        reminder = Reminder.objects.filter(user__username='user01')[0]

        now = date.today()

        next = now + timedelta(days=4)
        self.assertEqual(reminder.next_reminder, next)

        # only compare the date
        last = reminder.last_reminder
        self.assertEqual(last.year, now.year)
        self.assertEqual(last.month, now.month)
        self.assertEqual(last.day, now.day)

class InactiveReminderTestCase(Base):
    def setUp(self):
        now = datetime.now()

        self._createUser('user01')
        self._update('user01', 
                     last_reminder=now - timedelta(days=7),
                     next_reminder=now,
                     active=False)

    def testReminder(self):
        mock = Mock()
        @patch_object(send, 'send_mail', mock)
        def test():
            send.send_reminder()
        test()

        self.assertFalse(mock.called)


