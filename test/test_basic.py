import unittest
import uuid
from decimal import Decimal

from botocore.exceptions import ClientError

from distributed_counter import DistributedCounter


class TestDistributedCounter(unittest.TestCase):
    def setUp(self):
        self.counter = DistributedCounter(str(uuid.uuid1()), debug=True, region_name='us-west-1',
                                          aws_access_key_id='somekey', aws_secret_access_key='somesecret')
        self.counter.create_table()

    def test_basic(self):
        self.counter.put('test', 10)
        self.assertEqual(self.counter.get('test'), 10)
        self.assertEqual(self.counter.increment('test', 3), 13)
        self.assertEqual(self.counter.get('test'), 13)
        self.assertEqual(self.counter.decrement('test', 10), 3)
        self.assertEqual(self.counter.get('test'), 3)

    def test_table_dne(self):
        counter = DistributedCounter('nonexistanttable', debug=True, region_name='us-west-1',
                                     aws_access_key_id='somekey', aws_secret_access_key='somesecret')
        with self.assertRaises(ClientError):
            counter.get('somekey')

    def test_get_dne(self):
        self.assertIsNone(self.counter.get('nonexistantkey'))

    def test_put_dne(self):
        self.counter.put('test', 10)
        self.assertEqual(self.counter.get('test'), 10)

    def test_increment(self):
        self.assertEqual(self.counter.increment('test1', 3, 0), 3)
        self.assertEqual(self.counter.get('test1'), 3)
        self.assertEqual(self.counter.increment('test2', 3, 10), 13)
        self.assertEqual(self.counter.get('test2'), 13)

    def test_increment_dne(self):
        with self.assertRaises(ClientError):
            self.counter.increment('test2', 3)

    def test_increment_default(self):
        self.assertEqual(self.counter.increment('test', 0, 10), 10)
        self.assertEqual(self.counter.increment('test2', 5, 10), 15)

    def test_decrement_default(self):
        self.assertEqual(self.counter.decrement('test', 0, 10), 10)
        self.assertEqual(self.counter.decrement('test2', 5, 10), 5)

    def test_bad_input(self):
        self.counter.put('test', 10)
        with self.assertRaises(ClientError):
            self.counter.increment('test', 'abc')

    def test_decimal(self):
        self.counter.put('test', Decimal('10.0'))
        self.assertEqual(self.counter.increment('test', 4), 14)
        self.assertEqual(self.counter.increment('test', Decimal('.4')), Decimal('14.4'))
