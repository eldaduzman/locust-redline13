import os
import time
import sys
import json
from itertools import count
from locust import User, between, task

import boto3
from boto3.exceptions import Boto3Error

REGION = os.environ.get("REGION")
ACCESS_KEY = os.environ.get("ACCESS_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY")
QUEUE_NAME = os.environ.get("QUEUE_NAME")


assert (
    REGION and ACCESS_KEY and SECRET_KEY and QUEUE_NAME
), "One or more of the following environment variables is missing [REGION | ACCESS_KEY | SECRET_KEY | QUEUE_NAME]"

USER_NUMBERS = count(1)


def get_queue():
    """get boto3 sqs queue object"""
    return boto3.resource(
        "sqs",
        region_name=REGION,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    ).get_queue_by_name(QueueName=QUEUE_NAME)


class SQSUser(User):
    wait_time = between(120, 130)

    def __init__(self, *args, **kwargs):
        self._user_number = next(USER_NUMBERS)
        self._queue = get_queue()
        super().__init__(*args, **kwargs)

    @task
    def send_sqs_message(self):
        """sends a message to SQS"""
        time_start = time.time() * 1000

        try:
            aws_response = self._queue.send_message(
                MessageBody=json.dumps({"user_id": self._user_number})
            )
            time_end = time.time() * 1000
            self.environment.events.request_success.fire(
                request_type="SQS",
                name="queue",
                response_time=(time_end - time_start),
                response_length=sys.getsizeof(aws_response),
            )
        except Boto3Error as ex:
            time_end = time.time() * 1000
            self.environment.events.request_failure.fire(
                request_type="SQS",
                name="queue",
                response_time=(time_end - time_start),
                exception=ex,
                response_length=0,
            )
