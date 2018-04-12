import unittest
import uuid
from multiprocessing import Pool

from distributed_counter import DistributedCounter

KEY_NAME = 'test'
TABLE_NAME = str(uuid.uuid1())
NUM_THREADS = 30
ITERATIONS_PER_THREAD = 150


def _thread(val):
    counter = DistributedCounter(TABLE_NAME, debug=True, region_name='us-west-1', aws_access_key_id='somekey',
                                 aws_secret_access_key='somesecret')
    for _ in range(ITERATIONS_PER_THREAD):
        result = counter.increment(KEY_NAME, 1)
        if result == 100:
            counter.decrement(KEY_NAME, 100)
            val += 1
    return val


def test_thread_safety():
    """
    Call increment 1 (NUM_THREADS * ITERATIONS_PER_THREAD) times.
    When it hits 100, decrement by 100 and add to the thread's own counter. Validate the sum of these counters,
    make sure decrement worked.
    """
    counter = DistributedCounter(TABLE_NAME, debug=True, region_name='us-west-1', aws_access_key_id='somekey',
                                 aws_secret_access_key='somesecret')
    counter.create_table()
    counter.put(KEY_NAME, 0)
    pool = Pool(NUM_THREADS)
    res = pool.map(_thread, [0] * NUM_THREADS)
    assert NUM_THREADS * ITERATIONS_PER_THREAD / 100 == sum(res)
    assert 0 == counter.get(KEY_NAME)
