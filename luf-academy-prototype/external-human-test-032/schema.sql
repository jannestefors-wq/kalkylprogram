CREATE TABLE `ht032_control` (
	`user_id` text PRIMARY KEY NOT NULL,
	`epoch` integer DEFAULT 0 NOT NULL,
	`revoked` integer DEFAULT 0 NOT NULL
);
--> statement-breakpoint
CREATE TABLE `ht032_feedback` (
	`user_id` text PRIMARY KEY NOT NULL,
	`value` text NOT NULL,
	`updated_at` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `ht032_history` (
	`user_id` text NOT NULL,
	`revision` integer NOT NULL,
	`value` text NOT NULL,
	`created_at` text NOT NULL,
	PRIMARY KEY(`user_id`, `revision`)
);
--> statement-breakpoint
CREATE TABLE `ht032_session` (
	`hash` text PRIMARY KEY NOT NULL,
	`user_id` text NOT NULL,
	`epoch` integer NOT NULL,
	`expires` integer NOT NULL
);
--> statement-breakpoint
CREATE INDEX `ht032_session_user` ON `ht032_session` (`user_id`);--> statement-breakpoint
CREATE TABLE `ht032_state` (
	`user_id` text PRIMARY KEY NOT NULL,
	`revision` integer DEFAULT 0 NOT NULL,
	`value` text NOT NULL,
	`write_id` text
);
