import sys

from loguru import logger
from jira import JIRA, exceptions
import ujson


def lambda_handler(event, context):
    logger.remove()
    logger.add(sys.stderr, level="INFO")

    try:
        main(event, context.log_stream_name, 'jira-project-id')
    except exceptions.JIRAError as err:
        message = 'failed create issue to jira.'
        logger.warning(message)
        logger.exception(err)
        return {'message': message, 'status': False}
    else:
        return {'message': 'succeed update jira ticket', 'status': True}


def main(event, log_stream_name: str, project_id: str) -> None:
    """
    TODO
        - create message with markdown formatting -> not work what i expected
        - add exception using raise
    """
    basic_auth = ('username@email.com', 'secret key')
    server_url = 'https://your-jira-server-name.atlassian.net/'

    for record in event['Records']:
        message = ujson.loads(record['Sns']['Message'])
        # subject = event['Sns']['Subject']
        alarm_name = message['AlarmName']
        timestamp = record['Sns']['Timestamp']
        message['Log Stream Name'] = log_stream_name

        jira = JIRA(
            server=server_url,
            basic_auth=basic_auth,
        )

        new_issue = jira.create_issue(
            project=project_id,
            summary=f'{alarm_name} at {timestamp}',
            description=f'```json{ujson.dumps(message, indent=4, sort_keys=True)}```',
            issuetype={'name': 'Bug'},
        )

        logger.debug(new_issue)
