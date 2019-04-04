from django.test import Client, RequestFactory, TestCase

class SimpleTest(TestCase):
    def setUp(self):
        self.client = Client()
