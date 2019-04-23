DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS contents;
DROP TABLE IF EXISTS users;
-- DROP TABLE IF EXISTS annotator;
DROP TABLE IF EXISTS contributors;


CREATE TABLE `users` (
	`id` INTEGER PRIMARY KEY AUTOINCREMENT,
	`username` TEXT NOT NULL UNIQUE,
	`password` TEXT NOT NULL,
	`user_type` TEXT NOT NULL,
	`is_alive` INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE `projects` (
	`id` INTEGER PRIMARY KEY AUTOINCREMENT,
	`create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`client_id` INTEGER NOT NULL,
	`title` TEXT NOT NULL,
	`description` TEXT NOT NULL,
	`due_date_time` DATETIME NOT NULL,
	`label_count` INTEGER NOT NULL,
	`label_list` TEXT NOT NULL,
	`annotator_count` INTEGER NOT NULL,
	`annotator_id_list` TEXT NOT NULL,
	`status` TEXT NOT NULL DEFAULT 'Not Uploaded',
	`sample_size` INTEGER NOT NULL DEFAULT 0,
	`is_alive` INTEGER NOT NULL DEFAULT 1,

    FOREIGN KEY (client_id) REFERENCES users (id)
);


CREATE TABLE `contributors` (
	`id` INTEGER PRIMARY KEY AUTOINCREMENT,
	`user_id` INTEGER NOT NULL,
	`project_id` INTEGER NOT NULL,
	`is_alive` INTEGER NOT NULL DEFAULT 1,

    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (project_id) REFERENCES projects (id)
);

CREATE TABLE `contents` (
	`id` INTEGER PRIMARY KEY AUTOINCREMENT,
	`project_id` INTEGER NOT NULL,
	`content_element` TEXT NOT NULL,
	`status` TEXT NOT NULL DEFAULT 'Not Annotated',
	`label` TEXT NOT NULL DEFAULT '*',
	`is_alive` INTEGER NOT NULL DEFAULT 1,

    FOREIGN KEY (project_id) REFERENCES projects (id)
);

-- ALTER TABLE `projects` ADD CONSTRAINT `projects_fk0` FOREIGN KEY (`client_id`) REFERENCES `users`(`id`);
--
-- ALTER TABLE `annotators` ADD CONSTRAINT `annotators_fk0` FOREIGN KEY (`annotator_id`) REFERENCES `users`(`id`);
--
-- ALTER TABLE `annotators` ADD CONSTRAINT `annotators_fk1` FOREIGN KEY (`project_id`) REFERENCES `projects`(`id`);
--
-- ALTER TABLE `contents` ADD CONSTRAINT `contents_fk0` FOREIGN KEY (`project_id`) REFERENCES `projects`(`id`);
