# Slide Deck: Azure UAE Relocation and BCDR Strategy

## Slide 1: Title

Azure UAE Relocation and BCDR Strategy

Planning for datacenter, regional, and geopolitical disruption

## Slide 2: Why This Matters

- The threat model is not a routine outage.
- The customer is planning for physical destruction or prolonged unavailability of a UAE datacenter, region, or operating environment.
- A UAE-only resilience strategy is not enough for that scenario.

## Slide 3: The Three Failure Scopes

1. Single datacenter or availability-zone failure.
2. Single-region failure in UAE.
3. UAE-wide geopolitical or sovereign disruption.

Each requires a different control set.

## Slide 4: The Core Message

- Availability zones help with facility-level failures.
- Paired-region concepts help with some regional recovery scenarios.
- Neither is a complete answer to the loss of UAE as a geography.
- The hedge against that scenario is another geography.

## Slide 5: Recommended Strategy

1. Multi-zone resilience inside the primary region.
2. Cross-region recovery for regional outages.
3. Cross-geography recovery outside UAE for geopolitical disruption.

## Slide 6: What Good Looks Like

- No single-instance production services.
- DR environment exists before the crisis, not after.
- Data services replicate across regions.
- Application entry point supports controlled failover.
- Runbooks and recovery artifacts are available outside the primary geography.

## Slide 7: Region Options

- UAE North plus UAE Central: best for UAE-only DR.
- Qatar Central or Saudi Arabia Central: lower-latency compromise.
- North Europe or West Europe: strongest default hedge.
- Switzerland North: governance-oriented specialized option.

## Slide 8: Recommendation by Scenario

### If data can leave UAE

Use North Europe or West Europe as the DR geography now. Consider moving the primary there if resilience is the main objective.

### If data must remain in UAE

Use UAE North and UAE Central where supported, and formally document residual country-level risk.

## Slide 9: Technical Pattern

- Azure Front Door or Traffic Manager for failover routing.
- Azure Site Recovery for VM-based workloads.
- Native geo-replication for PaaS data services.
- Secondary landing zone with networking, identity, logging, and secrets prebuilt.
- Immutable backups and tested restore procedures.

## Slide 10: What Not to Assume

- Region pairing is not automatic DR.
- Microsoft-managed storage failover is not a full application recovery plan.
- Backups alone are not a business continuity strategy.
- A second UAE location does not fully hedge a UAE-wide disruption.

## Slide 11: Decision Matrix

| Option                                  | Position                           |
| --------------------------------------- | ---------------------------------- |
| UAE North only                          | Not sufficient                     |
| UAE North plus UAE Central              | Good only for UAE-only constraints |
| UAE plus Qatar or Saudi DR              | Reasonable compromise              |
| UAE plus North Europe or West Europe DR | Recommended default                |
| Europe primary plus UAE secondary       | Best overall if regulation allows  |

## Slide 12: Recommended Next Steps

1. Confirm data residency constraints.
2. Define RTO and RPO by workload tier.
3. Select the target DR geography.
4. Validate region service availability and quota.
5. Build the secondary landing zone.
6. Implement replication and failover.
7. Run a real DR exercise.

## Slide 13: Leadership Decision Required

The business must choose between:

- Maximum resilience with a cross-geography design.
- Lower latency with a compromise design.
- UAE-only compliance with accepted residual geopolitical risk.

## Slide 14: Closing Statement

If the organization is truly planning for the loss of UAE as an operating location, the correct hedge is another geography, not just another datacenter in UAE.

## Speaker Notes

### Notes for presenter

- Emphasize that this is not standard high availability planning.
- Distinguish datacenter failure, regional outage, and geopolitical loss.
- Use Europe as the default recommendation unless regulation or latency clearly overrides it.
- State residual risk plainly when the customer insists on UAE-only hosting.
