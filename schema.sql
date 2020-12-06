CREATE DATABASE slack_reaction_gater DEFAULT CHARACTER SET utf8;

use slack_reaction_gater;

CREATE TABLE reactions (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `channel` varchar(255),
  `ts` varchar(255),
  `user` varchar(255),
  `reactions` json DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE channels (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `channel_id` varchar(255),
  `channel_name` varchar(255),
  `read_flg` tinyint(1),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE users (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(255),
  `real_name` varchar(255),
  `display_name` varchar(255),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
