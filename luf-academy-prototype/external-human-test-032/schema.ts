import {sqliteTable,text,integer,primaryKey,index} from 'drizzle-orm/sqlite-core';
export const control=sqliteTable('ht032_control',{userId:text('user_id').primaryKey(),epoch:integer('epoch').notNull().default(0),revoked:integer('revoked').notNull().default(0)});
export const state=sqliteTable('ht032_state',{userId:text('user_id').primaryKey(),revision:integer('revision').notNull().default(0),value:text('value').notNull(),writeId:text('write_id')});
export const history=sqliteTable('ht032_history',{userId:text('user_id').notNull(),revision:integer('revision').notNull(),value:text('value').notNull(),createdAt:text('created_at').notNull()},t=>[primaryKey({columns:[t.userId,t.revision]})]);
export const session=sqliteTable('ht032_session',{hash:text('hash').primaryKey(),userId:text('user_id').notNull(),epoch:integer('epoch').notNull(),expires:integer('expires').notNull()},t=>[index('ht032_session_user').on(t.userId)]);
export const feedback=sqliteTable('ht032_feedback',{userId:text('user_id').primaryKey(),value:text('value').notNull(),updatedAt:text('updated_at').notNull()});
