# Azure Virtual Desktop Cost Optimization Playbook

A crisp, practical guide to reduce AVD spend primarily by shutting down and right‑sizing session hosts without impacting user experience.

## Related Documents
- Resilience checklist: [`avd-resilience-checklist.md`](./avd-resilience-checklist.md)
- Hosts & host pools resiliency FAQ: [`avd-hosts-hostpools-resiliency-faq.md`](./avd-hosts-hostpools-resiliency-faq.md)

## Core Levers
- Autoscale: use AVD Scaling Plans to power off/deallocate hosts outside demand.
- Start VM on Connect: keep hosts off; first user wakes one up.
- Session limits: disconnect/logoff idle/disconnected sessions so autoscale can drain and stop hosts.
- Right-size baseline: keep minimal “always‑on” capacity; burst only during peaks.

## Recommended Setup (Pooled Host Pools)
- Scaling method:
  - Prefer Power management scaling plan (GA) for most pools.
  - Dynamic autoscale (preview) is strong for image‑based pools that support it.
- Schedules: Define ramp‑up, peak, ramp‑down, off‑peak with:
  - Minimum percentage of hosts (baseline)
  - Capacity threshold (for example, 70–80% sessions per host)
  - Load‑balancing algorithm and burst behavior
- Start VM on Connect: Enable so baseline can be near‑zero off‑hours without blocking the first user.
- Session limits: Set `MaxSessionLimit` and enforce policies to disconnect/logoff idle/disconnected users.

## Prerequisites (Autoscale Permissions)
Assign the following built‑in roles to the Azure Virtual Desktop service principal at subscription scope for each subscription that contains your host pools and session hosts:
- `Desktop Virtualization Power On Off Contributor`
- `Desktop Virtualization Virtual Machine Contributor` (required for dynamic autoscale)

```powershell
# Replace with your subscription ID
$sub="/subscriptions/<SUBSCRIPTION_ID>"
$avdAppId = "9cdead84-a844-4324-93f2-b2e6bb768d07"  # Azure Virtual Desktop service principal appId

az account set --subscription $sub.Split('/')[-1]

az role assignment create \
  --assignee $avdAppId \
  --role "Desktop Virtualization Power On Off Contributor" \
  --scope $sub

az role assignment create \
  --assignee $avdAppId \
  --role "Desktop Virtualization Virtual Machine Contributor" \
  --scope $sub
```

## Enable Start VM on Connect
```powershell
# Requires Az.DesktopVirtualization module
Update-AzWvdHostPool -ResourceGroupName <rg> -Name <hostPoolName> -StartVMOnConnect:$true
```

## Create and Assign a Scaling Plan
- Portal: Azure Virtual Desktop > Scaling plans > Create.
- Choose pooled/personal, create weekday and weekend schedules.
  - Off‑peak: min % hosts = 0–10% (or 0 with Start VM on Connect)
  - Peak: higher min % and capacity threshold ~70–80%
  - Ramp‑down: enable force logoff at end‑of‑day with a grace period

Quick CLI checks:
```powershell
# Requires az desktopvirtualization extension
az desktopvirtualization scaling-plan list -g <rg> -o table
az desktopvirtualization scaling-plan update -g <rg> -n <planName> --friendly-name "<name>"
```

## Personal Host Pools
- Use autoscale for personal: power down when user is signed out/disconnected.
- Hibernation can reduce cold‑start cost, but don’t enable if using FSLogix or MSIX App Attach (unsupported with hibernate).

## Tuning Tips
- Baseline capacity: Keep just enough “always‑on” to avoid long morning logins; verify with Insights.
- Use Windows 11 multi‑session to increase session density and reduce VM count.
- VM size: Right‑size CPU/RAM; prefer Premium SSD v2 or Standard SSD where IOPS allow.
- Deallocate, don’t only Stop inside the OS: only deallocated VMs stop compute billing (disks still bill).
- Dev/Test: Consider Spot VMs for non‑critical pooled hosts; expect evictions.

## Policy & Timeouts (Intune or GPO)
- Idle disconnect: 15–30 minutes.
- Logoff disconnected: 30–60 minutes after disconnect.
- End‑of‑day logoff: 5–10 minute grace.

## Monitoring & Validation
- Enable AVD Insights; monitor:
  - Session distribution per host
  - Average sign‑in time
  - Autoscale actions and errors
- After one week, reduce min % or raise the capacity threshold if utilization is low.

## Cost & Tradeoffs
- Biggest savings from deallocating off‑peak; maximize Start VM on Connect + minimal baseline.
- Tradeoff: Potential cold‑start latency for first users; mitigate with a small baseline and ramp‑up schedule.
- Ongoing: Storage still billed for OS/data disks; right‑size disk SKUs and capacity.

## Fast Implementation Checklist
1) Assign autoscale roles to AVD service principal at subscription scope.
2) Enable Start VM on Connect on host pools.
3) Set non‑default `MaxSessionLimit` and enforce idle/disconnect policies.
4) Create scaling plan schedules for weekdays/weekends; assign to host pools.
5) Validate in Insights; iterate baseline and thresholds after one week.

## References
- AVD Autoscale (Scaling Plans): https://learn.microsoft.com/azure/virtual-desktop/autoscale-scaling-plan
- Assign roles to AVD service principal: https://learn.microsoft.com/azure/virtual-desktop/service-principal-assign-roles
- Start VM on Connect and host pool settings: https://learn.microsoft.com/azure/virtual-desktop/deploy-azure-virtual-desktop
- AVD cost optimization guidance (Well‑Architected): https://learn.microsoft.com/azure/well-architected/azure-virtual-desktop/business-continuity
