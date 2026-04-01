# Technical Reference: Azure BCDR Strategy for UAE Geopolitical Risk

## Scope

This reference is for Azure workloads currently hosted in UAE and requiring protection from:

1. Loss of a single datacenter or availability zone.
2. Loss of an entire Azure region in UAE.
3. Loss of UAE as an operating geography due to conflict, physical damage, or prolonged disruption.

## Design Principle

Use different controls for different blast radii. A single technical pattern does not solve all three scenarios.

## Architecture Objectives

- No single-instance production dependencies.
- Clear recovery time objective and recovery point objective by application tier.
- Cross-region recovery for critical stateful services.
- Cross-geography survivability for high-risk geopolitical scenarios.
- Regular test failover and operational runbooks.

## Reference Architecture

### Layer 1: In-Region Resilience

- Use availability zones wherever the service and SKU support them.
- Deploy at least two compute instances across zones.
- Use zone-redundant storage and data services where available.
- Avoid nonzonal production components unless explicitly justified.

### Layer 2: Cross-Region Recovery

- Maintain a secondary region with precreated networking, identity dependencies, observability, and security controls.
- Replicate stateful services using native geo-replication or Azure Site Recovery depending on the workload.
- Front applications with Azure Front Door or Traffic Manager for failover orchestration.
- Keep deployment artifacts, secrets, and configuration available in both locations.

### Layer 3: Cross-Geography Survivability

- Maintain a second geography outside UAE for mission-critical applications.
- Keep infrastructure-as-code, backup metadata, and recovery runbooks outside UAE.
- Ensure recovery operations do not depend on a single office, local ISP, or locally held credentials.

## Workload Patterns

### VM-Based Applications

- Use Azure Site Recovery for Azure VM replication between regions.
- Define recovery plans for boot order and dependency sequencing.
- Test non-disruptive failover regularly.
- Pre-stage network mappings, NSGs, route tables, and load balancer design in the target region.

### App Service and Web Applications

- Use multi-instance deployment within a zone-aware region where supported.
- Deploy a second application instance in the recovery region.
- Externalize state into replicated data services.
- Use Front Door or Traffic Manager for health-based routing.

### AKS and Containerized Platforms

- Create a separate AKS cluster or landing environment in the recovery geography.
- Replicate container images through Azure Container Registry patterns suitable for multi-region use.
- Keep manifests, Helm charts, and GitOps state in a neutral control location.
- Separate platform failover from data failover and validate both independently.

### Serverless and Integration Services

- Review each service for regionality and failover behavior.
- Duplicate workflows, app settings, identities, and integration endpoints in the recovery region.
- Do not assume automatic recovery across regions unless the service documentation explicitly provides it and the design has been tested.

## Data Layer Strategy

### Azure SQL

- Use failover groups or active geo-replication depending on workload and tier.
- Predefine application failover behavior and DNS cutover process.

### Azure Storage

- Use GRS or GZRS where appropriate.
- Do not treat Microsoft-managed failover as the primary DR plan.
- Plan for application-level cutover, validation, and potential data consistency handling.

### Azure Cosmos DB

- Use multi-region replication.
- Evaluate multi-write only where business value justifies the added consistency complexity.

### PostgreSQL and MySQL

- Use the service-specific cross-region replica and promotion capabilities that apply to the chosen service tier.
- Validate promotion process, expected lag, and application connection behavior.

### Key Vault and Configuration Services

- Duplicate or restore these dependencies in the recovery region.
- Ensure the failover plan includes certificates, secrets, private endpoints, DNS dependencies, and identity assignment.

## Backup Strategy

- Use immutable backups for critical datasets.
- Store backup policies and recovery procedures outside the primary UAE dependency chain.
- Test restore operations, not just backup job success.

## Networking and Identity

- Prebuild VNets, subnets, private DNS, firewall rules, and private endpoints in the recovery region.
- Validate Entra ID dependency paths, conditional access implications, and break-glass administration.
- Ensure DNS failover and client routing can be executed outside the affected geography.

## Operating Models

### Active-Passive

- Lower cost.
- Simpler operational model.
- Preferred default for most enterprise workloads.

### Active-Active

- Higher cost and operational complexity.
- Appropriate only for workloads that justify continuous dual-site operations and data consistency design.

## Suggested Service Tiers by Criticality

### Tier 1

- RPO: near-zero to minutes.
- RTO: less than 1 hour.
- Pattern: warm or hot standby in another geography.

### Tier 2

- RPO: less than 1 hour.
- RTO: 4 to 8 hours.
- Pattern: warm standby with tested cutover.

### Tier 3

- RPO: daily or scheduled.
- RTO: 24 hours or more.
- Pattern: backup and restore.

## Migration Sequence for Leaving UAE

1. Inventory all workloads and classify them by criticality and compliance.
2. Select the target geography based on regulation first.
3. Validate region service availability and quota before committing.
4. Recreate landing zone controls in the target geography.
5. Enable data replication first.
6. Stand up application components in the target geography.
7. Validate failover through testing.
8. Cut over stateless services.
9. Cut over stateful services in a controlled window.
10. Run a formal post-migration DR exercise.

## Residual Risk Statement

If primary production and all recoverable data remain only inside UAE, the organization retains residual exposure to a country-level disruption. That risk should be explicitly accepted by business leadership rather than treated as a technical gap alone.
