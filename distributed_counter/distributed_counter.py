import boto3
from botocore.exceptions import ClientError

KEY_COLUMN_NAME = 'key'
VALUE_COLUMN_NAME = 'counter_value'


class DistributedCounter(object):
    """
    This class interacts with AWS DynamoDB for interacting with an atomic counter.
    Instance variables:
    table_name - dynamoDB table name string this object uses
    session - boto3 Session object
    dynamodb - boto3 DynamoDB ServiceResource object
    table - boto3 dynamodb Table object
    available - boolean on whether or not the table is immediately available.
        Set to False when the user creates the table.
    """
    def __init__(self, table_name, config=None, endpoint_url=None, *args, **kwargs):
        self.table_name = table_name
        self.session = boto3.session.Session(*args, **kwargs)
        self.dynamodb = self.session.resource('dynamodb', endpoint_url=endpoint_url, config=config)
        self.table = self.dynamodb.Table(self.table_name)
        self.available = True

    def create_table(self, read_capacity_units=1, write_capacity_units=1, raise_created_exception=False):
        """
        Create the table in dynamodDB. The next call to use the table will auto wait until the table is created.
        :param read_capacity_units: integer read capacity
        :param write_capacity_units: integer write capacity
        :param raise_created_exception: if True, this will raise an exception if the table already exists.
        """
        try:
            self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {
                        'AttributeName': KEY_COLUMN_NAME,
                        'KeyType': 'HASH',
                    },
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': KEY_COLUMN_NAME,
                        'AttributeType': 'S',
                    },
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': read_capacity_units,
                    'WriteCapacityUnits': write_capacity_units,
                }
            )
            self.available = False
        except ClientError as e:
            if raise_created_exception:
                raise
            if e.response['Error']['Code'] != 'ResourceInUseException':
                # error is not table already exists error
                raise

    def _wait_for_table_to_exist_if_created(self):
        """If the user called create_table, this function will be ran on the next dynamoDB API call to wait for
        the server to come up."""
        if not self.available:
            self.table.wait_until_exists()
        self.available = True

    def increment(self, key, count, default=None):
        """Atomically increment the count for key by count.
        :param default: if key does not exist, put the default first, then increment.
        """
        self._wait_for_table_to_exist_if_created()
        try:
            return self.table.update_item(
                Key={
                    KEY_COLUMN_NAME: key
                },
                UpdateExpression='SET {0} = {0} + :incr'.format(VALUE_COLUMN_NAME),
                ExpressionAttributeValues={':incr': count},
                ReturnValues='UPDATED_NEW',
            )['Attributes'][VALUE_COLUMN_NAME]
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationException':  # likely because row doesn't exist
                if default is not None:
                    self.put(key, count + default)
                    return count + default
            raise

    def decrement(self, key, count, default=None):
        """Atomically decrement the count for key by count.
        :param default: if key does not exist, put the default first, then decrement."""
        self._wait_for_table_to_exist_if_created()
        return self.increment(key, -count, default)

    def get(self, key):
        """
        Retrieve the count for a key.
        Raises ResourceNotFoundException if table does not exist. Catch using botocore.ClientError.
        :return: integer response
        """
        self._wait_for_table_to_exist_if_created()
        response = self.table.get_item(
            Key={
                KEY_COLUMN_NAME: key
            },
            AttributesToGet=[
                KEY_COLUMN_NAME, VALUE_COLUMN_NAME,
            ]
        )
        if 'Item' not in response:  # row with key does not exist
            return None
        if VALUE_COLUMN_NAME not in response['Item']:  # row is missing count attribute for some reason
            return None
        return response['Item'][VALUE_COLUMN_NAME]

    def put(self, key, count):
        """
        Store a key and count. Overwrites existing count if the key already exists.
        """
        self._wait_for_table_to_exist_if_created()
        self.table.put_item(
            Item={
                KEY_COLUMN_NAME: key,
                VALUE_COLUMN_NAME: int(count),
            }
        )
