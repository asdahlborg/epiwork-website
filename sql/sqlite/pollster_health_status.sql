DROP VIEW IF EXISTS pollster_health_status;
CREATE VIEW pollster_health_status AS
SELECT id as pollster_results_weekly_id,
       case 1
       when QN1_0 then 'NO-SYMPTOMS'
       when QN5 == 0 and (QN1_1 or QN1_11 or QN1_8 or QN1_9) and (QN1_6 or QN1_6 or QN1_7) then 'ILI'
       when QN5 == 1 and (QN1_4 or QN1_5 or QN1_6 or QN1_7) then 'COMMON-COLD'
       when QN1_15 or QN1_16 or QN1_17 and QN1_18 then 'GASTROINTESTINAL'
       else 'NON-INFLUENZA'
       end as status
  FROM pollster_results_weekly;
