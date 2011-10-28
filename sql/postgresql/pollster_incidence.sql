-- support function and table for days
CREATE OR REPLACE FUNCTION calendar(date, date) RETURNS SETOF date AS  $$
        SELECT $1 + s.a as days
          FROM generate_series(0,($2 - $1)::int) as s(a)
$$ LANGUAGE SQL;

DROP TABLE IF EXISTS pollster_calendar;
CREATE TABLE pollster_calendar (
    p_day            date,
    p_week           date,
    p_month          date,
    p_quarter        date,
    p_year           date,
    p_week_month     int8,
    p_week_year      int8,
    p_quarter_year   int8,

    PRIMARY KEY (p_day)
);

INSERT INTO pollster_calendar
SELECT day,
       date_trunc('week',day),
       date_trunc('month',day),
       date_trunc('quarter',day),
       date_trunc('year',day),
       to_char(day,'w')::int8,
       to_char(day,'ww')::int8,
       to_char(day,'Q')::int8
FROM (SELECT calendar('1999-1-1','2020-12-31') as day) A;


-- returns the global_id for active users in a given date
CREATE OR REPLACE FUNCTION pollster_active_users (
    date -- $1 current day
) RETURNS TABLE (
    global_id text
) AS $body$ 
SELECT global_id
  FROM (
        -- extract the time of the first submission, the time of
        -- the last one and the number of submitted symptoms surveys
        SELECT W.global_id,
               min(W.timestamp) AS first,
               max(W.timestamp) AS latest,
               count(*) AS rate
          FROM pollster_results_weekly W
         GROUP BY W.global_id
       ) AS ranges
       -- to be considered active an user needs at least 4 filled survey
 WHERE rate > 4
       -- the first compiled survey should be at least one day old
   AND date_trunc('day', first) + '1 day' < date_trunc('day', $1)
       -- the last compilation should not be after the current date
   AND date_trunc('day', $1) <= date_trunc('day', latest)
$body$ LANGUAGE 'sql';

-- returns the global_id for active users with ILI onset on a given date
CREATE OR REPLACE FUNCTION pollster_ili_users (
  date -- $1 current day
) RETURNS TABLE (
  global_id text
)
AS $body$
SELECT DISTINCT A.global_id
      FROM pollster_health_status S,
           pollster_results_weekly W,
           pollster_active_users($1) A
     WHERE S.pollster_results_weekly_id = W.id
       AND W.global_id = A.global_id
       -- consider only user which set the onset date as the current date or
       -- take the submission date as the onset date
       AND date_trunc('day', COALESCE(W."Q3_0_open", W.timestamp)) = date_trunc('day', $1)
       -- filter only ILI-related symptoms
       AND S.status = 'ILI'
$body$
LANGUAGE 'sql';

-- returns the incidence ratio for a time period
CREATE OR REPLACE FUNCTION pollster_ili_incidence (
  date, -- $1 first day
  date  -- $2 last day
) RETURNS TABLE (
  "Day"         date,
  "Incidence"   float
)
AS $body$
SELECT p_day AS "Day", CASE active WHEN 0 THEN 0 ELSE ili::float/active END AS "Incidence"
  FROM (
    SELECT p_day,
          (SELECT count(*) FROM pollster_active_users(p_day)) AS active,
          (SELECT count(*) FROM pollster_ili_users(p_day)) AS ili
      FROM pollster_calendar
     WHERE p_day BETWEEN $1 AND $2
     ) AS incidence;
$body$
LANGUAGE 'sql';

-- return zip_code_key, color and counters to display the illness
-- status on nearby postal code areas
SELECT zip_code_key,
       CASE true
       WHEN count(ili) > 0 THEN '#FF0000'
       ELSE '#0000FF' END AS color,
       count(ili) AS "Malati di influenza",
       count(not_ili) AS "Non malati di influenza"
  FROM (
SELECT I."Q3" AS zip_code_key,
       NULLIF(S.status = 'ILI', false) AS ili,
       NULLIF(S.status != 'ILI', false) AS not_ili
  FROM pollster_health_status AS S,
       pollster_results_intake AS I,
       -- get the last weekly submitted for each user and
       -- ensure that is not older than 7 days
      (SELECT DISTINCT ON (global_id) *
         FROM pollster_results_weekly
        WHERE timestamp BETWEEN 'today'::date-7 AND 'today'
        ORDER BY global_id, timestamp DESC) AS W
     WHERE S.pollster_results_weekly_id = W.id
       AND W.global_id = I.global_id
       ) AS statuses
  GROUP BY zip_code_key
