# Azure Migrate Import And Dependency Workflow

This guide explains the practical workflow when you want to use an RVTools-style Excel import and also preserve application relationships.

## Short answer

Application dependency mapping is not directly importable into Azure Migrate through the RVTools Excel import path.

Supported import behavior today:

- Azure Migrate accepts VMware inventory import in RVTools-style XLSX format.
- Azure Migrate does not use custom overlay sheets as an application-topology import schema.
- Dependency maps inside Azure Migrate come from discovery and dependency analysis, not from extra workbook tabs.

## Recommended workflow

1. Prepare the RVTools-style workbook

Use one of these as the import-safe source:

- `azure_migrate_vmware_rvtools_strict_sample.xlsx`
- `azure_migrate_vmware_enterprise_import_sample.xlsx`
- `healthcare_payor_provider_vmware_import_sample.xlsx`

These contain only the expected RVTools tabs.

1. Import the workbook into Azure Migrate

In Azure Migrate:

- Create or open the migration project.
- Go to discovery and assessment.
- Choose custom import.
- Select the VMware inventory RVTools XLSX option.
- Upload the RVTools-style workbook.

1. Use the relationship workbook as the planning companion

Use one of these copies during architecture and migration-wave planning:

- `azure_migrate_vmware_enterprise_import_sample_with_app_relationships.xlsx`
- `healthcare_payor_provider_vmware_import_sample_with_app_relationships.xlsx`
- `azure_migrate_vmware_enterprise_sql_sap_citrix_workshop.xlsx`

These preserve the RVTools tabs and add planning-only sheets:

- `ServerApplicationMap`
- `ApplicationTopology`
- `ClusterRelationships`
- `ApplicationDependencies`
- `WorkloadGroupsForAzureMigrate`

The workshop workbook also adds focused sheets for SQL, SAP, and Citrix workshop use.

1. Build groups in Azure Migrate using the planning workbook

Use `WorkloadGroupsForAzureMigrate` to manually define migration groups.

Suggested manual grouping pattern:

- Create one Azure Migrate group per application or per migration wave.
- Use the `all_members` column to select machines that belong together.
- Use the `tier_membership` column to check that web, app, and db tiers are complete.
- Use `ApplicationDependencies` to keep coupled applications in the same wave if needed.

1. Turn on Azure Migrate dependency analysis for actual in-product maps

If you want dependency visualization inside Azure Migrate, do one of the following after the import:

- Deploy the Azure Migrate appliance and enable agentless dependency analysis.
- Use agent-based dependency analysis where deeper process and connection details are needed.

This is the supported route for generating dependency views within the Azure Migrate project itself.

## What the new workbook sheets are for

### WorkloadGroupsForAzureMigrate

Purpose:

- Manual copy/paste helper for forming Azure Migrate groups and migration waves.

Useful columns:

- `application_name`
- `criticality`
- `vm_count`
- `tier_membership`
- `all_members`

### ClusterRelationships

Purpose:

- Human-readable cluster semantics not present in RVTools import.

Examples:

- SQL Always On / AG pair
- SQL cluster / AG pair
- IIS web farm / load-balanced front end
- SAP application server cluster
- Citrix worker pool / session hosts

### ApplicationDependencies

Purpose:

- Companion planning map for source and target tier relationships.

Use it to:

- decide migration waves
- validate cross-tier completeness
- identify where test plans need app-level coordination

## Best-practice guidance

- Use the RVTools-only workbook as the actual import artifact whenever possible.
- Treat the enriched copies as planning and documentation overlays.
- Do not assume Azure Migrate will ingest custom dependency sheets as application topology.
- For the cleanest demo, import the RVTools workbook first, then show the relationship workbook in parallel, then enable Azure Migrate dependency discovery to compare the two views.

## Practical answer to the import question

If the goal is an easy one-step import of both server inventory and full application dependency mapping into Azure Migrate, the platform does not currently provide that through the RVTools Excel import route.

The closest workable pattern is:

- Excel import for inventory
- relationship workbook for planning
- Azure Migrate dependency discovery for native dependency views

That is the supported and realistic approach.
