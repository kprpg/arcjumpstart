# Azure Virtual Desktop Production Resilience & Reliability Checklist

A deep operational guide to harden, monitor, and rapidly recover Azure Virtual Desktop (AVD) in production.

## Related Documents
- Cost optimization playbook: [`avd-cost-optimization.md`](./avd-cost-optimization.md)
- Hosts & host pools resiliency FAQ: [`avd-hosts-hostpools-resiliency-faq.md`](./avd-hosts-hostpools-resiliency-faq.md)

## 1. How To Use
- Frequency: Run full review quarterly; lightweight score weekly.
- Scoring: 0 = Not in place, 1 = Partial / ad hoc, 2 = Implemented & documented, 3 = Automated + continuously verified.
- Target: Average category score ≥2.5; any critical item <2 flagged for remediation sprint.
- Evidence: Capture links (Dashboards, Policy assignments, Runbook repos) next to each item.

---

## 2. Quick Scorecard (Copy/Paste Table Into Ops Wiki)

| Category | Score (0–3) | Notes / Evidence / Owner | Next Action |
|----------|-------------|--------------------------|-------------|
| Architecture & Redundancy | | | |
| Capacity & Autoscale | | | |
| Session Host Image Lifecycle | | | |
| User Profiles & FSLogix | | | |
| Identity & Access | | | |
| Networking | | | |
| Storage | | | |
| Monitoring & Observability | | | |
| Security & Compliance | | | |
| Resilience Testing & Chaos | | | |
| Operations & Change Mgmt | | | |
| Cost vs Resilience Balance | | | |

---

## 3. Comprehensive Checklist (Detailed)

### 3.1 Architecture & Redundancy
- Paired Region Strategy documented; warm or cold standby classification defined.
- Availability Zones used (where supported) or justified exception.
- Separate host pools by persona / workload (task, knowledge, graphics, privileged).
- Defined capacity headroom (≥10–15% free) with monitoring alert.
- Secondary region image replicas in Shared Image Gallery (SIG).
- Region failover runbook tested in last 6 months.
- Dependency map (Identity, Profile storage, App services, Licensing) maintained.

### 3.2 Capacity & Autoscale
- Scaling Plans assigned to all pooled and personal host pools (no manual snowflakes).
- Baseline (min %) validated against morning login analytics.
- Start VM on Connect enabled where latency impact acceptable.
- MaxSessionLimit set and aligned with sizing perf tests.
- Autoscale action logs monitored; alert on consecutive failed scale events.
- Capacity forecast model (Workbook / exported data) reviewed monthly.

### 3.3 Session Host Image & Lifecycle
- Image pipeline (Azure Image Builder / Packer) source controlled & versioned.
- Staged rings: Dev → Pilot (5–10%) → Prod, with automated health gates.
- Rollback procedure (prior SIG version) tested.
- Image drift detection (compare session hosts vs golden image extensions/agents).
- Time to patch critical CVE defined SLA (e.g., ≤14 days).
- GPU pools image includes validated graphics driver baseline.

### 3.4 User Profiles & FSLogix
- FSLogix profile + ODFC separation (if Office heavy).
- Premium Files / Azure NetApp Files chosen via documented perf numbers.
- Profile share capacity <80% used (alert threshold 75%).
- Exclusions & redirections tuned; bloated profiles >10GB flagged automatically.
- Profile mount failure rate tracked (Kusto query) with SLO (e.g., <0.5%).
- Regular snapshots / backup schedule with retention policy documented.
- SMB multichannel / encryption settings validated (where applicable).

### 3.5 Identity & Access
- Conditional Access policies: MFA + compliant/Hybrid join enforced.
- Least privilege RBAC: separate image builders, scaling automation, support engineers.
- Local admin on session hosts removed; Just-In-Time (JIT) process defined.
- Service principals / managed identities rotated / reviewed quarterly.
- Break-glass accounts tested.

### 3.6 Networking
- Hub-spoke or Virtual WAN standard pattern implemented & documented.
- NSGs / Azure Firewall egress restricted to required AVD endpoints list.
- Latency dashboards (User→Host; Host→Profile Storage; Host→App DB) exist.
- DNS hybrid resolution health checks (test queries) scheduled.
- Bandwidth capacity modeled vs concurrent session count (margin ≥20%).

### 3.7 Storage
- Disk tier selection based on measured IOPS / session (documented baseline).
- OS disks ephemeral where permissible (non-persistent state).
- SIG replication count ≥2 per region (for scale & speed).
- Profile share encryption in place (platform-managed or CMK).
- Storage account soft delete & point-in-time restore configured (Azure Files).

### 3.8 Monitoring & Observability
- Log Analytics + AVD Insights enabled across all host pools.
- Core SLO metrics: Logon duration (P95), Connection success rate, Profile mount errors, Session host CPU/RAM.
- Alerts actionable (≤10% noise); runbooks linked from alert descriptions.
- Synthetic connection probe (Service Principal / test account) runs hourly.
- Dashboards: NOC board with red/amber/green status for each category.
- Diagnostics retention aligned with audit / forensic requirements (e.g., 90/180 days).

### 3.9 Security & Compliance
- Defender for Cloud recommendations backlog (e.g., <10 open high severities).
- Defender for Endpoint sensor healthy across hosts (coverage metric).
- OS baseline (CIS / organizational) applied & drift scanned.
- RDP Shortpath usage evaluated / implemented (if network quality).
- Secrets & config parameters stored in Key Vault; no plaintext credentials.

### 3.10 Resilience Testing & Chaos
- Planned chaos event schedule (quarterly) with declared scope.
- Scenarios tested: Remove 15% hosts, Profile share outage simulation, Region failover dry-run, Image regression rollback.
- Post-chaos review documenting MTTR and improvement backlog.
- Automated smoke test (launch app, open file, save) after each image deployment.

### 3.11 Operations & Change Management
- Change freeze windows defined (fiscal year events, month-end).
- Incident severity matrix (SEV1–SEV4) + escalation ladder current.
- Runbooks centrally indexed, version controlled, last review date tracked.
- KPIs: MTTD, MTTR, Change Failure Rate.
- Tagging standards: host with imageVersion, ring, workload, owner.

### 3.12 Cost vs Resilience Balance
- Documented rationale where cost optimizations increase cold start risk.
- Reserved Instances / Savings Plans applied to baseline only.
- Spot usage limited to non-critical pools with eviction handling script.
- Continuous rightsizing review integrates performance + cost data.
- Tradeoff register (decisions with explicit risk acceptance) maintained.

---

## 4. Validation & Diagnostic Command Examples

```powershell
# Host pool list & health
az desktopvirtualization hostpool list -g <rg> -o table

# Session host utilization snapshot
az desktopvirtualization session-host list -g <rg> --host-pool-name <pool> -o json

# Active connections (Kusto - sample predicate)
AzureDiagnostics
| where ResourceType == "HOSTPOOL" and OperationName == "Connect"
| summarize count() by bin(TimeGenerated, 5m)

# FSLogix Errors (local - last 2h)
Get-WinEvent -FilterHashtable @{LogName='Application'; ProviderName='Microsoft-FSLogix-Apps'; StartTime=(Get-Date).AddHours(-2)} |
  Where-Object {$_.LevelDisplayName -eq 'Error'}

# Autoscale action audit
az monitor activity-log list --status Succeeded --resource-group <rg> --max-events 50 |
  Select-String "ScalingPlan"
```

---

## 5. Automation Opportunities
- Scheduled workbook export comparing capacity vs forecast.
- Event-driven remediation: On profile mount error spike, trigger script to recycle hosts gracefully.
- Drift scan: Daily script enumerates extensions, FSLogix registry keys; posts diff.
- Auto-tagging: Upon image deployment, apply `imageVersion` tag to new hosts.

---

## 6. Key Metrics & Target Ranges (Illustrative)

| Metric | Target | Rationale |
|--------|--------|-----------|
| Logon Duration P95 | < 30s | User experience baseline |
| Connection Success Rate | > 99.5% | Reliability SLO |
| Profile Mount Failure Rate | < 0.5% | Stability of FSLogix layer |
| Autoscale Failed Actions | 0 per day | Operational health |
| Host CPU P95 | 70–80% peak | Efficient but not saturated |
| Unplanned Host Loss Capacity Impact | < 10% | Redundancy buffer |

---

## 7. Incident Runbook Templates

### Legend
- T+0 = Detection timestamp.
- Roles: IM (Incident Manager), PE (Platform Engineer), NE (Network Engineer), SA (Storage Admin), SEC (Security).

#### 7.1 Profile Share Outage / Degradation
- Detection: Spike FSLogix mount errors; logon delays > threshold.
- Immediate (T+0–5m): Declare SEV; verify storage/ANF; check Service Health.
- Containment: Drain affected hosts; user comms.
- Diagnosis: Throttling? Recent permission change? Capacity?
- Recovery: Failover or scale tier; recycle subset of hosts.
- Validation: Test logon within baseline +10%.
- Post: Root cause doc; capacity model adjust.

#### 7.2 Host Pool Capacity Exhaustion
- Detection: Queued connections; high CPU; autoscale warnings.
- Immediate: Manually start hosts or lower MaxSessionLimit.
- Diagnosis: Autoscale failure, quota, RBAC change.
- Recovery: Correct RBAC; request quota; adjust thresholds.
- Validation: CPU <80% P95; success rate normal.
- Preventive: Update forecast.

#### 7.3 Golden Image Regression
- Detection: App failures/logon latency after rollout.
- Immediate: Halt pipeline; drain new hosts.
- Recovery: Reassign previous SIG version; reimage.
- Validation: Synthetic app test passes.
- Post: Expand test suite.

#### 7.4 Control Plane / Regional Degradation
- Detection: Service Health advisory; broker errors.
- Immediate: Confirm multi-tenant; comms; consider failover.
- Recovery: Scale standby region; redirect users.
- Validation: Synthetic logon + app open success.
- Post: Gap analysis.

#### 7.5 Autoscale Malfunction
- Detection: Missed schedule actions.
- Immediate: Start baseline manually.
- Diagnosis: Role removal, API throttle, config change.
- Recovery: Reapply RBAC; reassign scaling plan.
- Validation: Next event success.
- Preventive: RBAC compliance check.

#### 7.6 Security Event (Compromised Host)
- Detection: High severity Defender alert.
- Immediate: Isolate host (NSG, drain).
- Forensics: Snapshot disk; collect logs.
- Recovery: Reimage; verify no lateral movement.
- Validation: Alerts cleared.
- Post: Hardening improvements.

---

## 8. Region Failover High-Level Runbook
1. Criteria: Outage >30m or critical advisory.
2. Pre-Check: Profile replication current; image replicas fresh.
3. Actions: Scale standby; update assignments; user comms.
4. Validation: Synthetic end-to-end test.
5. Repatriation: Reverse when stable; document deltas.
6. Metrics: TTD, TTF, TTR, impacted users.

---

## 9. Change Management Workflow
Submit → Review → Pipeline Build → Pilot Deploy → Health Gate → Approval → Broad Deploy.
Auto rollback: Logon P95 > baseline+40% for 10m OR profile errors >1%.

---

## 10. Appendix: Kusto Query Starters

Logon Duration (P95):
```
WVDConnections
| where TimeGenerated > ago(1d)
| summarize P95=percentile(LogonDuration,95) by bin(TimeGenerated, 30m)
```

Profile Mount Failures:
```
AzureDiagnostics
| where Category == "FSLogix" and Level == "Error"
| summarize count() by bin(TimeGenerated, 15m)
```

Autoscale Events:
```
AzureActivity
| where OperationNameValue contains "Microsoft.DesktopVirtualization/scalingPlans"
| project TimeGenerated, OperationNameValue, ActivityStatusValue, CorrelationId
```

---

## 11. Continuous Improvement Backlog Ideas
- Dynamic baseline adjustments (rolling 4-week peak).
- Anomaly detection for logon duration.
- Runbook “last exercised” badge in dashboard.

---

## 12. References
- Azure Virtual Desktop Reliability Guidance
- Azure Well-Architected Framework
- FSLogix Performance Tuning Documentation
- Shared Image Gallery / Image Builder docs

---

## 13. Revision History

| Date | Author | Change |
|------|--------|--------|
| YYYY-MM-DD | <name> | Initial version |
