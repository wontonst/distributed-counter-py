[![Build Status](https://travis-ci.org/wontonst/distributed-counter-py.svg?branch=initial)](https://travis-ci.org/wontonst/distributed-counter-py)
[![Documentation Status](https://readthedocs.org/projects/distributed-counter-py/badge/?version=latest)](http://distributed-counter-py.readthedocs.io/en/latest/?badge=latest)

# Overview

`distributed_counter` is a python package for maintaining counters across clusters of computers.
It leverages [AWS DynamoDB](https://aws.amazon.com/dynamodb) for storage and atomicity of the counter.

# Installation

`distributed_counter` is compatible with `python2` and `python3`.
Simply use `pip` to install.

```
pip install distributed_counter
```

You'll also want to set up your [aws configurations](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html).

# Usage

The interface for `distributed_counter` is very simple.
Everything is done through the `DistributedCounter` class.
To instantiate:

```
from distributed_counter import DistributedCounter

counter = DistributedCounter('my_dynamo_table_name')
```

You can pass anything kwargs to DistributedCounter and they will be propagated to the boto3 Session, e.g.

```
counter = DistributedCounter('mytable', region_name='us-west-1', aws_access_key_id='somekey',
                             aws_secret_access_key='somesecret')
```

The dynamodb table has one HASH key called `key`. You can create the table yourself, or you can use `create_table`.

```
counter.create_table()
```

`distributed_counter` is smart enough to wait for the table to finish creation on your next call to the table.

Next, you can set a key using `put` and get it with `get`:

```
counter.put('mykey', 0)
counter.get('mykey')
0
```

Finally, you can `increment`/`decrement`.

```
counter.increment('mykey', 10)
10
counter.increment('mykey', 5)
15
counter.decrement('mykey', 14)
1
```

Note that the returned value is the new value.

You can use `increment`/`decrement` with a default.
This is the same as doing a `put` then an `increment`/`decrement`.

```
counter.increment('nonexistantkey', 0, 0)
0
counter.increment('someotherkey', 0, 10)
10
counter.increment('yetanotherkey', 1, 10)
11
```

## Example Use

Let's say we want to run a function every 100 calls to an API.
In your API, you can put:

```
if not counter.increment('mykey', 1) % 100:
    run_function()
    counter.decrement('mykey', 100)
```

This guarantees that no matter how many servers you have, every 100 calls to your API will run your function.
