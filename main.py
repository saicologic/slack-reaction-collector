import configparser
import fire
import csv

from slack_reaction_collector import SlackReactionCollector
from tabulate import tabulate

class Commander():
    def __init__(self):
        config_ini = configparser.ConfigParser()
        config_ini.read('config.ini', encoding='utf-8')
        self.srg = SlackReactionCollector(config_ini['DEFAULT'])

    def setup(self):
        self.create_users()
        self.create_channels()

    def create_users(self):
        self.srg.create_users()
        print('Done: create_users')

    def create_channels(self):
        self.srg.create_channels()
        print('Done: create_channels')

    def create_reactions(self, start_date):
        channels = self.srg.get_all_channels()
        for channel in channels:
            self.srg.create_reactions_by_channel(start_date, channel['id'])

    def create_reactions_by_channel(self, start_date, channel_id):
        self.srg.create_reactions_by_channel(start_date, channel_id)

    def get_channels(self):
        channels = self.srg.get_all_channels()
        channel_table = []
        headers = ['channel_id', 'channel_name']
        for channel in channels:
            channel_table.append([channel['id'], channel['name']])
        print(tabulate(channel_table, headers, tablefmt="fancy_grid"))

    def get_user_reaction_ranking(self, output='no'):
        ranking_table = self.srg.get_user_reaction_ranking()
        headers = ['rank', 'count', 'user_name']
        print(tabulate(ranking_table, headers, tablefmt="fancy_grid"))

        if output == 'yes':
            file_path = 'output/user_reaction_ranking.csv'
            with open(file_path, 'w') as f:
                for row in ranking_table:
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                    writer = csv.writer(f)
                    writer.writerow(row)

            print("write: %s" % (file_path))

    def get_reaction_ranking(self, limit=100, output='no'):
        ranking_table = self.srg.get_reaction_ranking(limit)
        headers = ['reaction_name', 'count']
        print(tabulate(ranking_table, headers, tablefmt="fancy_grid"))


if __name__ == '__main__':
    fire.Fire(Commander)
