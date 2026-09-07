"""
Computes standard incident-response timing metrics from the tabletop
timeline: time-to-detect, time-to-contain, time-to-eradicate, time-to-
recover, and data loss window — the numbers a real post-incident report
leads with.
"""
import csv

with open("data/raw/tabletop_timeline.csv") as f:
    events = list(csv.DictReader(f))

phase_first_hour = {}
for e in events:
    phase = e["phase"]
    hour = float(e["elapsed_hours"])
    if phase not in phase_first_hour:
        phase_first_hour[phase] = hour

initial_access = phase_first_hour["Initial Access"]
detection = phase_first_hour["Detection"]
containment = phase_first_hour["Containment"]
eradication = phase_first_hour["Eradication"]
recovery = phase_first_hour["Recovery"]

time_to_detect = detection - initial_access
time_to_contain = containment - detection
time_to_eradicate = eradication - containment
time_to_recover = recovery - eradication
total_incident_duration = phase_first_hour["Post-Incident"] - initial_access

# Encryption began during Discovery & Lateral Movement (event 5, hour 18) and was stopped
# at full containment (event 9, hour 29) — that's the window ransomware was actively spreading
encryption_start = 18.0
containment_complete = 29.0
active_encryption_window = containment_complete - encryption_start

print("=" * 78)
print("INCIDENT TIMELINE — RANSOMWARE VIA PHISHING-COMPROMISED VPN ACCOUNT")
print("=" * 78)
print(f"Time to detect (initial access -> detection):        {time_to_detect:.1f} hours")
print(f"Time to contain (detection -> containment):           {time_to_contain:.1f} hours")
print(f"Time to eradicate (containment -> eradication):       {time_to_eradicate:.1f} hours")
print(f"Time to recover (eradication -> recovery):            {time_to_recover:.1f} hours")
print(f"Total incident duration (access -> post-incident):    {total_incident_duration:.1f} hours")
print(f"\nActive encryption window (staging -> full containment): {active_encryption_window:.1f} hours")
print("Volumes affected: 2 of 6 shared-drive volumes")
print("Data loss window (time since last good backup): 4 hours")

with open("data/raw/timeline_metrics.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["metric", "hours"])
    writer.writerow(["time_to_detect", round(time_to_detect, 1)])
    writer.writerow(["time_to_contain", round(time_to_contain, 1)])
    writer.writerow(["time_to_eradicate", round(time_to_eradicate, 1)])
    writer.writerow(["time_to_recover", round(time_to_recover, 1)])
    writer.writerow(["total_incident_duration", round(total_incident_duration, 1)])
    writer.writerow(["active_encryption_window", round(active_encryption_window, 1)])
    writer.writerow(["data_loss_window", 4.0])
    writer.writerow(["volumes_affected", 2])
    writer.writerow(["volumes_total", 6])

print("\nWrote data/raw/timeline_metrics.csv")
