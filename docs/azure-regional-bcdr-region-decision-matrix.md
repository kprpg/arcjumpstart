# Region Decision Matrix for US East 2 Azure Relocation and Disaster Recovery

## Objective

This matrix helps select the right Azure target region or disaster recovery region for workloads currently hosted in US East 2.

## Summary View

- US East 2 only: Best for lowest latency and minimum change. Strength is the simplest operating model. Weakness is poor resilience against regional and wider East Coast disruption. Recommendation: not sufficient for this scenario.
- US East 2 plus Central US: Best for conventional paired-region DR. Strength is alignment with Azure region-pair guidance and balanced latency. Weakness is that it is still weaker than an east-plus-west design for a broad coastal event. Recommendation: default option.
- US East 2 plus South Central US: Best for moderate separation with lower latency. Strength is more separation than staying in one region. Weakness is no paired-region benefit and less separation than West US 2 or West US 3. Recommendation: acceptable compromise.
- US East 2 plus West US 2: Best for a strong cross-US geographic hedge. Strength is meaningful distance from the East Coast with broad service support. Weakness is higher latency and more operational overhead. Recommendation: use when stronger separation is required.
- US East 2 plus West US 3: Best for a strong cross-US geographic hedge. Strength is strong geographic separation and a modern region footprint. Weakness is higher latency and more operational overhead. Recommendation: use when stronger separation is required.
- Central US primary plus US East 2 secondary: Best for reducing East Coast concentration. Strength is balanced central placement with a paired-region relationship. Weakness is higher migration impact than simply adding DR. Recommendation: strong option if relocating the primary.

## Decision Criteria

### Regulatory and Data Residency

- If the customer must keep workloads in the continental United States, all recommended options remain viable.
- If only some datasets are restricted, use data classification to move less-sensitive tiers sooner.

### Latency

- If the main user base is on the US East Coast, Central US usually offers the best balance during failover.
- If failover is a rare event and resilience matters more than failover latency, West US 2 or West US 3 are stronger answers.

### Service Availability

- Validate required Azure services and SKUs in the target region.
- Validate quota and capacity before committing to migration.

### Operational Simplicity

- Central US usually offers the cleanest long-term DR operating model because it is paired with US East 2.
- Wider east-plus-west designs improve resilience but add cost, latency, and operational complexity.

## Recommended Decision Logic

### Option A: Maximum Resilience

Choose West US 2 or West US 3 if:

- The customer is explicitly planning for a wide East Coast event.
- The customer wants the strongest hedge against a concentrated eastern US disruption.
- The application can tolerate the additional failover latency and operating complexity.

### Option B: Balanced Resilience and Latency

Choose Central US as DR while keeping US East 2 primary if:

- East Coast hosting is still desired for primary user proximity.
- The customer accepts some latency increase during disaster mode.
- The customer wants meaningful separation without jumping to an east-plus-west design immediately.

### Option C: Near-Region Continuity

Choose South Central US if:

- Lower latency is materially more important than maximum geographic separation.
- The customer accepts that this is a compromise rather than the strongest hedge.

### Option D: Paired-Region Default

Choose US East 2 plus Central US if:

- The customer wants the default Azure-aligned DR design for US East 2.
- The customer understands that this addresses regional failure better than a broader East Coast event.

## Default Recommendation

For most customers facing the scenario described, the default recommendation is:

1. Keep US East 2 primary if East Coast user proximity still matters.
2. Stand up DR in Central US as the default baseline.
3. Add West US 2 or West US 3 when the threat model requires a wider geographic hedge.

## Customer Questions to Resolve Before Final Selection

1. Must production and recovery stay within specific US jurisdictions or business zones?
2. What are the required RTO and RPO values for each workload?
3. Which Azure services and SKUs are mandatory for the application?
4. What latency is acceptable in normal operation and disaster mode?
5. Is the customer willing to fund a warm or hot standby environment?
6. Does the operating model support regular DR testing and failover drills?
