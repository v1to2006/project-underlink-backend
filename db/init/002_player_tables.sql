DROP TABLE IF EXISTS `player_opened_airports`;
DROP TABLE IF EXISTS `player_route_airports`;
DROP TABLE IF EXISTS `players`;

CREATE TABLE `players` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `progress_index` int(11) NOT NULL DEFAULT 0,
  `completed` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `player_route_airports` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `player_id` bigint(20) NOT NULL,
  `airport_ident` varchar(40) NOT NULL,
  `order_index` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_player_route_order` (`player_id`,`order_index`),
  UNIQUE KEY `uq_player_route_airport` (`player_id`,`airport_ident`),
  KEY `airport_ident` (`airport_ident`),
  CONSTRAINT `player_route_airports_ibfk_1` FOREIGN KEY (`player_id`) REFERENCES `players` (`id`) ON DELETE CASCADE,
  CONSTRAINT `player_route_airports_ibfk_2` FOREIGN KEY (`airport_ident`) REFERENCES `airport` (`ident`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `player_opened_airports` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `player_id` bigint(20) NOT NULL,
  `airport_ident` varchar(40) NOT NULL,
  `opened_at` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_player_opened_airport` (`player_id`,`airport_ident`),
  KEY `airport_ident` (`airport_ident`),
  CONSTRAINT `player_opened_airports_ibfk_1` FOREIGN KEY (`player_id`) REFERENCES `players` (`id`) ON DELETE CASCADE,
  CONSTRAINT `player_opened_airports_ibfk_2` FOREIGN KEY (`airport_ident`) REFERENCES `airport` (`ident`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;