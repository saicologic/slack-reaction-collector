import os
import json

from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from sqlalchemy import create_engine

class SlackReactionCollector():

    def __init__(self, config):
        self.slack_client = self.new_slack_client(config['SLACK_TOKEN'])
        self.db = self.create_engine(config)

    def new_slack_client(self, token):
        try:
            return WebClient(token=token)
        except SlackApiError as e:
            print(f"Got an error: {e.response['error']}")

    def create_engine(self, config):
        database = 'mysql+mysqlconnector://%s:%s@%s/%s?charset=utf8' % (
            config["MYSQL_USER"],
            config["MYSQL_PASSWORD"],
            config["MYSQL_HOST"],
            config["MYSQL_DBNAME"],
        )

        return create_engine(
            database,
            encoding = "utf-8",
            connect_args={'auth_plugin': 'mysql_native_password'}
        )

    def create_users(self):
        users = self.slack_client.users_list(exclude_archived=1)

        with self.db.connect() as con:
            for user in users['members']:
                if user['is_bot'] == False and user['deleted'] == False and user['is_app_user'] == False:
                    sql = "insert into users(user_id, real_name, display_name) values(%s, %s, %s)"
                    con.execute(
                        sql,
                        user['id'],
                        user['profile']['real_name'],
                        user['profile']['display_name']
                    )

    def create_channels(self):
        channels = self.slack_client.conversations_list(
            limit=1000,
            exclude_archived=1
            )['channels']

        with self.db.connect() as con:
            for channel in channels:
                sql = "insert into channels(channel_id, channel_name, read_flg) values(%s, %s, %s)"
                con.execute(
                    sql,
                    channel['id'],
                    channel['name'],
                    0
                )

    def get_reply_reactions(self, channe_id, history_message):
        replies = self.slack_client.conversations_replies(
            channel=channe_id,
            ts=history_message['thread_ts'],
        )

        return replies

    def insert_reaction(self, channel, history_message):

        with self.db.connect() as con:
            sql = "insert into reactions(channel, user, ts, reactions) values(%s, %s, %s, %s)"
            # print(history_message['user'], history_message['ts'], history_message['reactions'])

            con.execute(
                sql,
                channel,
                history_message['user'],
                history_message['ts'],
                json.dumps(history_message['reactions'])
            )

    def create_reactions_by_channel(self, start_date, channel_id):
        oldest = datetime.strptime(start_date, "%Y-%m-%d").timestamp()
        histories = self.slack_client.conversations_history(
                    channel=channel_id,
                    oldest=oldest,
                )

        for history_message in histories['messages']:
            insert_reactions = []

            # https://api.slack.com/events/message
            if 'subtype' in history_message:
                continue

            if 'reply_count' in history_message:
                if history_message['reply_count'] != 0:
                    replies = self.get_reply_reactions(channel_id, history_message)
                    # print(replies)
                    for reply_message in replies['messages']:
                        for reaction in reply_message['reactions']:
                            insert_reactions.append({
                                'user': reply_message['user'],
                                'ts': reply_message['ts'],
                                'reactions': reaction
                            })

            for reaction in insert_reactions:
                # print(reaction['reactions'])
                self.insert_reaction(channel_id, reaction)

    def get_all_channels(self):
        return self.slack_client.conversations_list(
            limit=1000,
            exclude_archived=1
            )['channels']

    def get_user_reaction_ranking(self):

        with self.db.connect() as con:
            sql = """
            SELECT
                t2.cnt,
                users.display_name
            FROM
            (
                SELECT
                t.user,
                SUM(count) as cnt
                FROM
                    (
                    SELECT
                        user,
                        JSON_EXTRACT(reactions, '$.count') as count
                    FROM
                        reactions
                    ORDER BY
                        count DESC
                    ) AS t
                GROUP BY user
            ) AS t2 INNER JOIN users ON (t2.user = users.user_id)
            ORDER BY cnt DESC
            """

            results = con.execute(sql).fetchall()

            rank = 1
            ranking_table = []
            for result in results:
                count = result[0]
                user_name = result[1]
                ranking_table.append([str(rank), str(count), user_name])
                rank += 1

        return ranking_table

    def get_reaction_ranking(self, limit):
        with self.db.connect() as con:
            sql = """
            SELECT
                JSON_UNQUOTE(JSON_EXTRACT(reactions, '$.name')) as reaction_name,
                SUM(JSON_EXTRACT(reactions, '$.count')) as count
            FROM
                reactions
            GROUP BY
                JSON_UNQUOTE(JSON_EXTRACT(reactions, '$.name'))
            ORDER BY
                count desc
            LIMIT
                %s
            """ % limit

            results = con.execute(sql).fetchall()
            table = []
            for result in results:
                reaction_name = result[0]
                count = result[1]
                table.append([reaction_name, count])

            return results

