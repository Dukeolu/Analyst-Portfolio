-- Q1. Baseline: overall auth log volume and failure rate, over the 30-day window.
SELECT
  COUNT(*) AS total_events,
  SUM(CASE WHEN event_type = 'login_failed' THEN 1 ELSE 0 END) AS failed_events,
  SUM(CASE WHEN event_type = 'login_success' THEN 1 ELSE 0 END) AS success_events,
  ROUND(100.0 * SUM(CASE WHEN event_type = 'login_failed' THEN 1 ELSE 0 END) / COUNT(*), 1) AS failure_rate_pct,
  COUNT(DISTINCT source_ip) AS distinct_source_ips,
  COUNT(DISTINCT username) AS distinct_usernames
FROM auth_events;

-- Q2. The security team's CURRENT rule, approximated in SQL: source IPs with
-- 5+ failed logins inside any fixed 10-minute bucket. (This buckets on
-- calendar-aligned 10-minute windows rather than a true rolling window --
-- close enough to reproduce the loud, bursty attacks; the Python analysis
-- implements the exact rolling-window version and is the one actually used
-- for the recall/false-positive numbers reported in the README.)
WITH failed AS (
  SELECT source_ip, timestamp,
    strftime('%Y-%m-%d %H:', timestamp) || printf('%02d', (CAST(strftime('%M', timestamp) AS INTEGER) / 10) * 10) AS bucket_10min
  FROM auth_events
  WHERE event_type = 'login_failed'
)
SELECT source_ip, bucket_10min, COUNT(*) AS fails_in_bucket
FROM failed
GROUP BY source_ip, bucket_10min
HAVING fails_in_bucket >= 5
ORDER BY fails_in_bucket DESC;

-- Q3. The proposed rule's core signal: distinct FAILED usernames per source
-- IP per day, plus that IP's overall failure rate that day. High
-- distinct-failed-usernames + high failure rate = credential-stuffing
-- signature. High distinct-usernames alone (ignoring failure rate) would
-- also flag the shared office NAT IP -- shown here for comparison.
SELECT
  date(timestamp) AS log_date,
  source_ip,
  COUNT(DISTINCT username) AS distinct_usernames_total,
  COUNT(DISTINCT CASE WHEN event_type = 'login_failed' THEN username END) AS distinct_usernames_failed,
  ROUND(100.0 * SUM(CASE WHEN event_type = 'login_failed' THEN 1 ELSE 0 END) / COUNT(*), 1) AS failure_rate_pct,
  COUNT(*) AS total_attempts
FROM auth_events
GROUP BY log_date, source_ip
HAVING distinct_usernames_total >= 15
ORDER BY distinct_usernames_failed DESC;

-- Q4. Firewall corroboration: which source IPs show port-scanning /
-- blocked-connection activity against non-VPN ports, and do they overlap
-- with the IPs already flagged for suspicious auth behavior?
SELECT
  f.source_ip,
  GROUP_CONCAT(DISTINCT f.port) AS scanned_ports,
  SUM(f.connection_count) AS blocked_connection_attempts,
  COUNT(DISTINCT a.username) AS distinct_usernames_targeted_in_auth_log,
  SUM(CASE WHEN a.event_type = 'login_failed' THEN 1 ELSE 0 END) AS failed_auth_attempts
FROM firewall_events f
LEFT JOIN auth_events a ON a.source_ip = f.source_ip
WHERE f.blocked = 1
GROUP BY f.source_ip
ORDER BY blocked_connection_attempts DESC;

-- Q5. Coarse account-compromise signal: usernames with 3+ total failed
-- attempts AND at least one success on record. (This ignores the actual
-- order of events -- a username could have failed after succeeding, which
-- wouldn't be suspicious. The Python analysis implements the exact
-- temporally-ordered "success within 24h of 3+ recent fails" version and is
-- the one used for the reported detection results.)
SELECT
  username,
  SUM(CASE WHEN event_type = 'login_failed' THEN 1 ELSE 0 END) AS total_fails,
  SUM(CASE WHEN event_type = 'login_success' THEN 1 ELSE 0 END) AS total_successes,
  COUNT(DISTINCT source_ip) AS distinct_source_ips
FROM auth_events
GROUP BY username
HAVING total_fails >= 3 AND total_successes >= 1
ORDER BY total_fails DESC;
