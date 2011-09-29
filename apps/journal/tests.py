"""
Tests for the journal app
"""

import datetime

from django.test import TestCase

from .models import Entry, published_filter
from .navigation import get_nodes

class EntryTest(TestCase):
    def setUp(self):
        self.today = datetime.datetime.today()
        self.yesterday = self.today - datetime.timedelta(days=1)
        self.tomorrow = self.today + datetime.timedelta(days=1)
        
    def tearDown(self):
        pass

        
    def test_unpublished(self):
        """
            Test if unpublished items are hidden by default
        """
        unpublished = Entry.objects.create(
            title='Unpublished Entry',
            slug='unpublished-entry',
            is_published=False,
            pub_date=self.yesterday,
        )
        self.assertEquals(published_filter(Entry.objects).count(), 0)
        unpublished.is_published = True
        unpublished.save()
        self.assertEquals(published_filter(Entry.objects).count(), 1)
        unpublished.is_published = False
        unpublished.save()
        self.assertEquals(published_filter(Entry.objects).count(), 0)
        
        unpublished.delete()
        
    def test_future_published(self):
        """
            Tests that items with a future published date are hidden
        """
        future_published = Entry.objects.create(
            title='Future published entry',
            slug='future-published-entry',
            is_published=True,
            pub_date=self.tomorrow,
        )
        self.assertEquals(published_filter(Entry.objects).count(), 0)
        future_published.pub_date = self.yesterday
        future_published.save()
        self.assertEquals(published_filter(Entry.objects).count(), 1)
        future_published.pub_date = self.tomorrow
        future_published.save()
        self.assertEquals(published_filter(Entry.objects).count(), 0)
        
    def test_navigation(self):
        """
            Tests if the navigation build by navigation.get_nodes is correct
        """
        pass
