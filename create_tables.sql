CREATE TABLE `Role` (
  `role_id` int NOT NULL,
  `role_name` varchar(255) NOT NULL,
  `description` varchar(255),
  PRIMARY KEY (`role_id`)
);

CREATE TABLE `User` (
  `user_id` int NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `role_id` int NOT NULL,
  `student_id` int,
  `teacher_id` int,
  PRIMARY KEY (`user_id`),
  FOREIGN KEY (`role_id`) REFERENCES `Role` (`role_id`)
);

CREATE TABLE `ResourceType` (
  `type_id` int NOT NULL,
  `type_name` varchar(255) NOT NULL,
  `description` varchar(255),
  PRIMARY KEY (`type_id`)
);

CREATE TABLE `Resource` (
  `resource_id` int NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` varchar(255),
  `location` varchar(255),
  `capacity` int,
  `status` varchar(50),
  `type_id` int NOT NULL,
  PRIMARY KEY (`resource_id`),
  FOREIGN KEY (`type_id`) REFERENCES `ResourceType` (`type_id`)
);

CREATE TABLE `Reservation` (
  `reservation_id` int NOT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `resource_id` int NOT NULL,
  `status` varchar(50),
  `description` varchar(255) NOT NULL,
  `public` boolean NOT NULL,
  PRIMARY KEY (`reservation_id`),
  FOREIGN KEY (`resource_id`) REFERENCES `Resource` (`resource_id`)
);

CREATE TABLE `UsageRecord` (
  `record_id` int NOT NULL,
  `user_id` int NOT NULL,
  `reservation_id` int NOT NULL,
  `primary` boolean NOT NULL,
  `start_time` datetime,
  `end_time` datetime,
  PRIMARY KEY (`record_id`),
  FOREIGN KEY (`user_id`) REFERENCES `User` (`user_id`),
  FOREIGN KEY (`reservation_id`) REFERENCES `Reservation` (`reservation_id`)
);

CREATE TABLE `Tag` (
  `tag_id` int NOT NULL,
  `reservation_id` int,
  `user_id` int,
  `resource_id` int,
  `resource_type_id` int,
  `key` varchar(255) NOT NULL,
  `value` varchar(255) NOT NULL,
  PRIMARY KEY (`tag_id`),
  FOREIGN KEY (`reservation_id`) REFERENCES `Reservation` (`reservation_id`),
  FOREIGN KEY (`user_id`) REFERENCES `User` (`user_id`),
  FOREIGN KEY (`resource_id`) REFERENCES `Resource` (`resource_id`),
  FOREIGN KEY (`resource_type_id`) REFERENCES `ResourceType` (`type_id`)
);

