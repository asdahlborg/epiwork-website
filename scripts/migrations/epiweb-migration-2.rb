#!/usr/bin/ruby

require "rubygems"
require "dbi"

epi_old = DBI.connect("DBI:Mysql:epiweb_migration:localhost", "old_django_db", "password")

users = epi_old.select_all("SELECT id, username, first_name, last_name, email, password, is_staff, is_active, is_superuser, last_login, date_joined FROM auth_user")

survey_users = epi_old.select_all("SELECT survey_surveyuser.id, deleted, global_id, last_participation_id, last_participation_date, name, user_id FROM survey_surveyuser INNER JOIN survey_surveyuser_user ON survey_surveyuser.id = survey_surveyuser_user.surveyuser_id")

epi_old.disconnect

epi_new = DBI.connect("DBI:Pg:influweb_it:localhost", "new_django_db", "password")

insert_users = epi_new.prepare("INSERT INTO auth_user (id, username, first_name, last_name, email, password, is_staff, is_active, is_superuser, last_login, date_joined) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")

users.each do |user|
	if !user.empty?
		insert_users.execute(user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7], user[8], user[9], user[10])
	end
end

insert_users.finish

insert_survey_users = epi_new.prepare("INSERT INTO survey_surveyuser (id, global_id, last_participation_id, last_participation_date, name, deleted, user_id) VALUES(?, ?, ?, ?, ?, ?, ?)")

survey_users.each do |survey_user|
	if !survey_user.empty?
		insert_survey_users.execute(survey_user[0], survey_user[2], "NULL", survey_user[4], survey_user[5], survey_user[1], survey_user[6])
	end
end

insert_survey_users.finish

epi_new.disconnect
