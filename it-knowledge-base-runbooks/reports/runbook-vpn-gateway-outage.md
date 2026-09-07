# Runbook: VPN Gateway Outage (Site-Wide)

**Audience:** IT Support technicians (Tier 1 and Tier 2)
**Trigger:** 3+ independent VPN connection-failure tickets within 15 minutes, OR the automated gateway health check alert fires
**Severity:** P2 (all remote/hybrid employees blocked from internal systems) — escalate to P1 if it coincides with a scheduled remote-heavy event (month-end close, a planned WFH day)
**Target time to first update:** 10 minutes from trigger
**Target time to resolution:** 60 minutes

This runbook exists because "Can't connect to VPN" (a single-user issue) and "VPN gateway is down" (a site-wide outage) look identical from the first ticket — the job of steps 1–2 is telling them apart fast, so a Tier 1 tech doesn't spend 20 minutes troubleshooting one laptop while the real problem is the gateway.

---

## Step 1 — Confirm scope (target: 3 minutes)

- [ ] Check the internal status dashboard for the VPN gateway's health check (green/yellow/red).
- [ ] Check the ticket queue: are multiple tickets, from different users, in different locations, arriving in a short window? A single user's issue almost never generates this pattern.
- [ ] Attempt your own test connection from a technician account, if you have VPN access from your current network.

**If the health check is green and it's one user:** this is not a gateway outage — close this runbook, handle as a standard individual ticket (see KB-01: Connecting to the Office VPN).

**If the health check is red, or 3+ independent users are affected:** continue to Step 2.

## Step 2 — Declare and communicate (target: 10 minutes from trigger)

- [ ] Post to the **#it-status** channel: *"Investigating a possible VPN gateway outage affecting remote connectivity. Update in 15 minutes."*
- [ ] Update the internal status page to "Investigating."
- [ ] Page the on-call network engineer if the gateway health check is red (this is outside Tier 1 scope past this point).

**Do not** promise a fix time in the first update — only confirm you're investigating. A wrong ETA in the first message causes more frustration than no ETA.

## Step 3 — Diagnose (target: 20 minutes, network engineer)

Check in this order — each check rules out a category, so don't skip ahead:

1. **Is the gateway host itself reachable?** (ping/SSH from the internal management network) — if not, this is a hardware/hypervisor problem, escalate to infrastructure on-call immediately, skip to Step 5.
2. **Is the VPN service running on the gateway?** (`systemctl status` or vendor-equivalent) — if the service crashed, attempt a service restart per the vendor runbook; log the crash for root-cause review regardless of whether the restart works.
3. **Is the gateway's internet-facing interface up and passing traffic?** — if the service is running but no traffic is reaching it, this is likely upstream (ISP, firewall rule change, DDoS) — check the firewall change log for anything applied in the last 2 hours first, since a same-day config change is the most common cause of a sudden outage.
4. **Is authentication succeeding but sessions dropping?** — if users can authenticate but get disconnected within minutes, this points to a certificate expiration or a licensing/session-limit issue, not a network problem — check the gateway's session log for the specific rejection reason.

## Step 4 — Resolve

- Apply the fix identified in Step 3.
- Confirm resolution with a test connection from an external network (not the office network — that would falsely show "resolved" if a laptop on-site connects fine but there is still an issue for a remote user).
- Ask 1–2 of the users who filed tickets to confirm they can now connect, before declaring it resolved broadly.

## Step 5 — Communicate resolution and close out

- [ ] Post to **#it-status**: what happened, in plain language, and that it's resolved.
- [ ] Update the status page to "Resolved."
- [ ] Close all tickets tagged to this outage with a note linking to this incident, not individually diagnosed.
- [ ] File a one-paragraph post-incident note: root cause, time to detect, time to resolve, and whether this runbook's steps matched what actually happened (update the runbook if not).

## Escalation contacts

| Role | When to page | Contact |
|---|---|---|
| Network engineer (on-call) | Gateway health check is red, or Step 3 isn't resolving it in 20 min | see on-call schedule |
| Infrastructure on-call | Gateway host itself is unreachable (Step 3.1) | see on-call schedule |
| IT Director | Outage exceeds 60 minutes, or coincides with month-end close | see on-call schedule |
