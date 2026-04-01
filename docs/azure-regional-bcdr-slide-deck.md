# Slide Deck: Azure US East 2 Relocation and BCDR Strategy

## Slide 1: Title

Azure US East 2 Relocation and BCDR Strategy

Planning for datacenter, regional, and wide-area East Coast disruption

## Slide 2: Why This Matters

- The scenario is not a routine outage.
- The customer is planning for loss of US East 2 or a wider East Coast operating disruption.
- A US East 2-only resilience strategy is not enough for that scenario.

## Slide 3: The Three Failure Scopes

1. Single datacenter or availability-zone failure.
2. Single-region failure in US East 2.
3. Wider East Coast disruption affecting operations, connectivity, or the regional dependency chain.

Each scenario requires a different control set.

## Slide 4: The Core Message

- Availability zones help with facility-level failures.
- Paired-region concepts help with some regional recovery scenarios.
- Neither is a complete answer to the loss of the East Coast operating geography.
- The appropriate hedge against that scenario is another geography.

## Slide 5: Recommended Strategy

1. Multi-zone resilience inside the primary region.
2. Cross-region recovery for regional outages.
3. Cross-geography recovery outside the East Coast blast radius.

## Slide 6: What Good Looks Like

- No single-instance production services.
- The disaster recovery environment exists before the crisis, not after.
- Data services replicate across regions.
- Application entry point supports controlled failover.
- Runbooks and recovery artifacts are available outside the primary geography.

## Slide 7: Region Options

- US East 2 plus Central US: default paired-region DR.
- US East 2 plus South Central US: lower-latency compromise.
- US East 2 plus West US 2 or West US 3: strongest default hedge.
- Central US primary plus US East 2 secondary: strong relocation option.

## Slide 8: Recommendation by Scenario

### If the customer wants conventional DR

Use Central US as the default disaster recovery region.

### If the customer wants a stronger East Coast hedge

Use West US 2 or West US 3 as the disaster recovery region and document the added latency and operating complexity.

## Slide 9: Technical Pattern

- Azure Front Door or Traffic Manager for failover routing.
- Azure Site Recovery for VM-based workloads.
- Native geo-replication for PaaS data services.
- Secondary landing zone with networking, identity, logging, and secrets prebuilt.
- Immutable backups and tested restore procedures.

## Slide 10: What Not to Assume

- Region pairing is not automatic DR.
- Platform-managed storage failover is not a full application recovery plan.
- Backups alone are not a business continuity strategy.
- A second east-side region does not fully hedge a wider East Coast disruption.

## Slide 11: Decision Matrix

- US East 2 only: not sufficient.
- US East 2 plus Central US: recommended default.
- US East 2 plus South Central US: reasonable compromise.
- US East 2 plus West US 2 or West US 3: recommended for stronger separation.
- Central US primary plus US East 2: strong relocation option.

## Slide 12: Recommended Next Steps

1. Confirm data residency constraints.
2. Define recovery time and recovery point targets by workload tier.
3. Select the target DR geography.
4. Validate region service availability and quota.
5. Build the secondary landing zone.
6. Implement replication and failover.
7. Run a real DR exercise.

## Slide 13: Leadership Decision Required

Leadership must choose between:

- A balanced paired-region design centered on Central US.
- A stronger east-plus-west design for wider separation.
- A future primary-region shift if East Coast concentration needs to be reduced further.

## Slide 14: Closing Statement

If the organization is planning for the loss of US East 2 or a wider East Coast operating disruption, the right hedge is another geography, not just another zone in US East 2.

## Speaker Notes

### Notes for presenter

- Emphasize that this is not standard high availability planning.
- Distinguish datacenter failure, regional outage, and wider East Coast disruption.
- Use Central US as the default recommendation unless the threat model requires wider separation.
- State residual risk plainly when the customer limits recovery to the eastern half of the United States.
