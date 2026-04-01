# Executive Memo: Azure Workload Relocation and BCDR Options for US East 2 Risk Scenarios

## Purpose

This memo provides executive guidance for customers that host Azure workloads in US East 2 and want to reduce exposure to severe disruption, including the loss of a single datacenter, an entire Azure region, or a broader East Coast operating disruption.

## Executive Summary

A US East 2-only Azure design is not sufficient if the threat model includes prolonged loss of US East 2 or a broader East Coast disruption. Azure availability zones and paired-region concepts improve resiliency, but they do not by themselves provide an adequate hedge against a wide-area operating disruption. The customer should design for three separate failure scopes:

1. Datacenter or availability-zone failure.
2. Regional failure affecting US East 2.
3. A wider East Coast disruption affecting the surrounding geography, network dependencies, or operating model.

For the third scenario, the recommended hedge is a second geography outside the eastern United States.

## Recommended Position

The customer should adopt a three-layer resilience posture:

1. Multi-zone resilience inside the primary region.
2. Cross-region recovery for regional outages.
3. Cross-geography recovery outside the East Coast blast radius.

If legal and regulatory constraints allow workloads to move elsewhere in the United States, the default recommendation is to establish a secondary geography in Central US for conventional disaster recovery and evaluate West US 2 or West US 3 when the objective is a stronger hedge against an East Coast event.

If business or application constraints require primary production to remain in US East 2, then the customer should keep production there, strengthen paired-region disaster recovery with Central US, and explicitly decide whether an additional western US recovery location is needed for wider geographic separation.

## Recommended Target Models

### Model 1: Highest Resilience

- Primary production remains in US East 2 with a hot or warm secondary in West US 2 or West US 3.
- Central US can still be used for service-level paired-region capabilities where needed.
- Appropriate for customers who prioritize stronger geographic separation from an East Coast event.

### Model 2: Balanced Model

- Primary production in US East 2.
- Warm or hot secondary environment in Central US.
- Appropriate for customers who want a balanced model with paired-region benefits and lower operational change.

### Model 3: Residency-Constrained Model

- Primary in US East 2.
- Secondary in Central US, with immutable backups and recovery artifacts stored outside the East Coast blast radius.
- Appropriate when the customer wants conventional regional DR without the cost of a full east-plus-west design.

## Region Recommendation

### Preferred Secondary Regions

- Central US
- West US 2
- West US 3

Central US is the paired region for US East 2 and is the default choice for conventional DR. West US 2 or West US 3 provide stronger geographic separation when the threat model includes a broad East Coast event.

### Nearer Operational Option

- South Central US

South Central US can be a reasonable compromise when the customer wants US-based separation with lower latency than a far-west design, but it does not carry the same paired-region benefits as Central US.

### Paired-Region Disaster Recovery

- US East 2
- Central US

This improves resilience to a single-region event and aligns with Azure paired-region guidance, but it is still weaker than an east-plus-west design for a wider East Coast disruption.

## Decision Guidance

### If resilience is top priority

Keep disaster recovery outside the East Coast immediately and evaluate whether a westward secondary region is required in addition to Central US.

### If latency and operational simplicity matter

Keep US East 2 primary and run a warm or hot secondary in Central US.

### If the customer wants the strongest hedge against East Coast disruption

Use West US 2 or West US 3 as the secondary geography and document the cost and operational tradeoff relative to Central US.

## Required Customer Actions

1. Confirm legal and policy constraints on where data and recovery environments can reside.
2. Define target recovery time objective and recovery point objective by workload tier.
3. Select a secondary region based on Azure service fit first, then recovery objective, then latency.
4. Fund a real DR environment rather than relying only on backups.
5. Test failover and executive decision processes regularly.

## Key Message for Leadership

If the planning assumption is that US East 2 or the broader East Coast could become unavailable as an operating environment, then another zone in US East 2 is not enough. The hedge is another geography.
