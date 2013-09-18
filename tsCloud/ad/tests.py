"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.utils import simplejson

from tsCloud.ctauth.middleware import username_field, token_field

import models

client = Client()

class UpdateTest(TestCase):
    username = '18910975586'
    token = 'abcdefghijklmnopqrst'

    def test_update_user_category(self):
        """
        Tests that 1 + 1 always equals 2.
        """

        # =================================================
        # Preparation
        # =================================================

        # Create user for testing
        response = client.post(
            reverse('tsCloud.ad.api.set_category'),
            {
                username_field: self.username,
                token_field: self.token,
                'category_id': 2,
            }
        )

        # Test response messages.
        json = simplejson.loads(response.content)

        # Test user category exist
        category = models.Category.objects.filter(
            user__username = self.username
        )

        # =================================================
        # Checking
        # =================================================

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json['res'], 0)
        self.assertEqual(category[0].pk, 2)
