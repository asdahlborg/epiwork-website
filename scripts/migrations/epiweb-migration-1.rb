#!/usr/bin/ruby

require "rubygems"
require "dbi"

epi_old = DBI.connect("DBI:Mysql:epiweb_old:localhost", "old_joomla_db", "password")

users_all = epi_old.select_all("SELECT id, username, name, email, password, lastvisitDate, registerDate FROM jos_users WHERE lastvisitDate > 0")

users_del_m = epi_old.select_all("SELECT memberuid FROM ag_familiar")
users_del_u = epi_old.select_all("SELECT useruid FROM ag_familiar")

epi_old.disconnect

users_del_m.flatten!.uniq!
users_del_u.flatten!.uniq!
users_del = users_del_m - users_del_u

users = users_all

users.each do |user|
	users_del.each do |user_del|
		if user_del == user[0]
			user.clear
		end
	end
end

users[0].clear

epi_new = DBI.connect("DBI:Mysql:epiweb:localhost", "new_django_db", "password")

insert_users = epi_new.prepare("INSERT INTO auth_user (id, username, first_name, email, password, last_login, date_joined, is_active) VALUES(?, ?, ?, ?, ?, ?, ?, ?)")

users.each do |user|
	if !user.empty?
		insert_users.execute(user[0], user[1], user[2], user[3], user[4], user[5], user[6], 1)
	end
end

insert_users.finish

epi_new.disconnect
