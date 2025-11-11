# Azure Virtual Desktop: Hosts, Host Pools, and Resiliency FAQ

This FAQ explains AVD session hosts, host pools, and practical reliability/resiliency options for both compute and profile storage layers.

## Related Documents
- Cost optimization playbook: [`avd-cost-optimization.md`](./avd-cost-optimization.md)
- Resilience & reliability checklist: [`avd-resilience-checklist.md`](./avd-resilience-checklist.md)

---

## 1) What is a “host” in AVD?
- A session host is a VM that users actually sign into via AVD.
- It runs Windows 10/11 Enterprise multi-session (many users per VM), Windows Server (RDS-style), or single-session for personal desktops.
- Prefer multiple moderately sized VMs over a single large VM to improve scaling, reduce blast radius, and simplify maintenance.

## 2) What is a host pool?
- A logical group of session host VMs that serve the same users and applications.
- Types:
  - Pooled: users land on any available host (shared capacity, higher density).
  - Personal: 1:1 user-to-VM desktop.
- Load balancing for pooled:
  - Breadth-first (spread users evenly) or
  - Depth-first (fill one host to its session limit, then move on).
- App groups (RemoteApps/Desktops) attach to a host pool and control user access.
- Scaling plans tie to host pools to schedule/dynamically start/stop capacity.

## 3) Resiliency/Reliability Options
### a) Single host (VM)
- Avoid single-host reliance: keep ≥2 hosts in production pools.
- Distribute hosts across Availability Zones (where supported) to survive zonal failures.
- Use drain mode (AllowNewSessions = false) for patching or retiring a host without disrupting active users.
- Maintain a golden image (Shared Image Gallery) for quick reimage/rollback; keep core agents current (AVD agents, Defender, monitoring).
- Keep headroom: don’t operate hosts near saturation; monitor CPU/RAM and session limits.

### b) Entire host pool
- Zone-spread the pool and maintain 10–15% capacity buffer to absorb host loss or sudden demand.
- Attach a scaling plan with a minimum baseline and pre-peak ramp; consider Start VM on Connect if acceptable for your latency profile.
- Multi-region strategy: warm standby with image + FSLogix data replicated and hosts scaled to 0 off-hours; fail over during regional incidents.
- Segment pools by persona/workload to limit blast radius and simplify rollback (promote/demote via app group assignment).
- Monitor SLOs (e.g., logon P95, connection success rate) with actionable alerts and tested runbooks.

## 4) Reliability/Resiliency for Profile Storage and User Data
FSLogix is the profile technology; the backing storage is typically Azure Files Premium or Azure NetApp Files (ANF).

### a) FSLogix on Azure Files
- Use Azure Files Premium (FileStorage) for predictable performance.
- Choose ZRS (where available) for zonal redundancy; pair with snapshots and Azure Backup for Azure Files for fast restore.
- FSLogix Cloud Cache can write to multiple endpoints (e.g., two Azure Files shares or Azure Files + ANF) to tolerate transient storage/network issues; requires local cache capacity and adds some logon I/O.
- Tune FSLogix exclusions/redirections and monitor profile size; keep share utilization <80% and alert at ~75%.

### b) Azure NetApp Files (ANF)
- Enterprise-grade SMB/NFS with very low latency and high throughput—well-suited for large or IO-heavy pools.
- Built-in snapshots and ANF Backup for point-in-time recovery; Cross-Region Replication (CRR) for DR and reduced RPO.
- Right-size capacity pools with throughput headroom; test restore/CRR failover procedures.

---

## Quick Recommendations
- Compute: multiple moderate-size hosts per pool, zone distribution, scaling plan with buffer, golden image pipeline and tested rollback.
- Storage: Azure Files Premium with ZRS or ANF; enable snapshots/backup; consider FSLogix Cloud Cache for higher resilience.
- Operations: monitor logon P95, connection success, FSLogix mount errors; keep runbooks for host drain/reimage and storage failover.
