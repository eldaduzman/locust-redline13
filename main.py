import os

import click
import gevent

from locustfile_sqs import SQSUser
from locust.env import Environment
from locust.html import get_html_report
from locust.env import Environment
from locust.stats import stats_printer, stats_history


@click.option(
    "--number-of-users",
    help="how many locust users to simulate",
    type=click.INT,
    required=True,
)
@click.option(
    "--duration-in-seconds",
    help="Duration of execution - if not provided, execution will run infinitely",
    type=click.INT,
    default=-1,
    required=False,
)
@click.option(
    "--output-path",
    help="path to output report",
    type=click.STRING,
    default="report.html",
    required=False,
)
def main(
    number_of_users,
    duration_in_seconds,
    output_path: str = "report.html",
):
    env = Environment(user_classes=[SQSUser])
    env.create_local_runner()
    assert env.runner, "must have a runner"
    try:

        gevent.spawn(stats_printer(env.stats))
        gevent.spawn(stats_history, env.runner)

        env.runner.start(number_of_users, spawn_rate=1)
        if duration_in_seconds > -1:
            gevent.spawn_later(duration_in_seconds, env.runner.quit)
        env.runner.greenlet.join()
    except KeyboardInterrupt:
        pass
    finally:

        dir_path = os.path.dirname(os.path.abspath(output_path))
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(output_path, "w", encoding="utf-8") as html_file:
            html_file.write(get_html_report(environment=env))


dispatch = click.command()(main)  # make pylint happy
if __name__ == "__main__":
    dispatch()
