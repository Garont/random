CREATE TABLE `ipv4base` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ruleid` int(11) NOT NULL,
  `table` enum('raw','mangle','nat','filter') NOT NULL DEFAULT 'filter',
  `chain` enum('INPUT','FORWARD','OUTPUT','PREROUTING','POSTROUTING') NOT NULL DEFAULT 'OUTPUT',
  `rule` varchar(1000) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1 

CREATE TABLE `ipv4extra` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ruleid` int(11) NOT NULL,
  `host` varchar(255) NOT NULL DEFAULT 'example.com',
  `table` enum('raw','mangle','nat','filter') NOT NULL DEFAULT 'filter',
  `chain` enum('INPUT','FORWARD','OUTPUT','PREROUTING','POSTROUTING') NOT NULL DEFAULT 'OUTPUT',
  `rule` varchar(1000) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1
