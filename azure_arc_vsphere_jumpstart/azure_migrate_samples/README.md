# Azure Migrate VMware sample package

This folder contains a realistic sample for VMware-to-Azure migration planning.

## What Azure Migrate can import from file

Officially, Azure Migrate supports VMware file import through an RVTools XLSX workbook.
That workbook is primarily for discovered VM inventory and infrastructure metadata.

Supported import pattern:

- XLSX file type
- RVTools-style sheets such as `vInfo`, `vHost`, `vDatastore`, `vSnapshot`, `vPartition`, `vMemory`, `vDisk`, `vCD`, `vUSB`, `vNetwork`, and `dvPort`

## What Azure Migrate does not import from file

Azure Migrate does not use custom file-import fields to create dependency maps, application topology, or installed technology intelligence inside the migration project.
Those richer views come from:

- Azure Migrate appliance discovery
- Agentless or agent-based dependency analysis
- Assessment grouping and business-case workflows
- External CMDB / app portfolio artifacts you manage separately

## Files in this folder

- `azure_migrate_vmware_rvtools_plus_app_inventory_sample.xlsx`
  - Includes the required RVTools-style sheets.
  - Also includes extra sheets named `AppInventory`, `Dependencies`, `TechnologyStack`, and `ReadMe`.
  - Only the RVTools-style sheets should be considered import candidates for Azure Migrate.

- `azure_migrate_vmware_rvtools_strict_sample.xlsx`
  - Strict RVTools-only workbook with only the expected import tabs.
  - Use this when you want the cleanest possible Azure Migrate import sample.

- `azure_migrate_vmware_enterprise_import_sample.xlsx`
  - Larger mock enterprise VMware inventory for Azure Migrate import testing.
  - Currently generated as a 200-VM estate with broader variation and more realistic workload patterns.

- `enterprise_app_inventory_sample.json`
  - Mock enterprise application portfolio mapped to the imported VM estate.

- `enterprise_dependency_map_sample.csv`
  - Multi-application dependency sample to support migration-wave planning outside Azure Migrate import.

- `enterprise_technology_inventory_sample.csv`
  - VM-to-technology mapping for the larger estate.

- `enterprise_workload_groups_sample.csv`
  - Application grouping summary for business and technical planning.

- `healthcare_payor_provider_vmware_import_sample.xlsx`
  - Healthcare-aligned import sample for a fictional pediatric research hospital and payor-provider environment.

- `healthcare_payor_provider_app_inventory_sample.json`
  - Healthcare application inventory with clinical, research, payer, and support workloads.

- `healthcare_payor_provider_dependency_map_sample.csv`
  - Dependency map for the healthcare-aligned scenario.

- `healthcare_payor_provider_technology_inventory_sample.csv`
  - VM-to-technology mapping for the healthcare scenario.

- `healthcare_payor_provider_workload_groups_sample.csv`
  - Workload grouping summary for the healthcare scenario.

- `azure_migrate_vmware_enterprise_import_sample_with_app_relationships.xlsx`
  - Enterprise planning copy that preserves the RVTools tabs and adds overlay sheets for application mapping, dependencies, workload groups, and a portal-ready Azure Migrate checklist.

- `healthcare_payor_provider_vmware_import_sample_with_app_relationships.xlsx`
  - Healthcare planning copy with the same enriched overlay sheets and checklist support.

- `azure_migrate_vmware_enterprise_sql_sap_citrix_workshop.xlsx`
  - Workshop-focused workbook with additional SQL, SAP, and Citrix summary sheets for high-attention migration patterns.

- `enterprise_azure_migrate_group_checklist.csv`
  - Portal-ready list of recommended Azure Migrate group names, member sets, waves, and notes for the enterprise scenario.

- `enterprise_azure_migrate_group_members.csv`
  - VM-level export for manual Azure Migrate group building in the enterprise scenario.

- `healthcare_azure_migrate_group_checklist.csv`
  - Portal-ready list of recommended Azure Migrate group names for the healthcare scenario.

- `healthcare_azure_migrate_group_members.csv`
  - VM-level export for manual Azure Migrate group building in the healthcare scenario.

- `azure_migrate_sql_sap_citrix_group_checklist.csv`
  - Workshop-oriented group checklist focused on SQL, SAP, and Citrix-heavy patterns.

- `azure_migrate_sql_sap_citrix_group_members.csv`
  - Workshop-oriented VM member export for targeted technical sessions.

- `azure_migrate_dependency_discovery_variations_sample.xlsx`
  - Synthetic Azure Migrate dependency-discovery style output with summary, observed processes, observed connections, and a variation guide.

- `dependency_discovery_observed_connections_sample.csv`
  - Connection-level sample showing steady-state, burst, batch-window, failover, and external-edge traffic patterns.

- `dependency_discovery_observed_processes_sample.csv`
  - Process and listening-port sample aligned to the discovered dependency views.

- `dependency_discovery_summary_sample.csv`
  - Rollup summary by scenario and application for dependency-review workshops.

- `dependency_discovery_variation_notes_sample.json`
  - Metadata describing how to use the synthetic dependency-discovery sample.

- `azure_migrate_vmware_sample_walkthrough.pptx`
  - Short walkthrough deck that explains how to use the import workbook, enriched copies, checklist exports, workshop workbook, and dependency-discovery sample together.

- `azure_migrate_import_and_dependency_workflow.md`
  - Step-by-step explanation of the practical workflow: RVTools import for inventory, enriched workbook for planning, and Azure Migrate dependency discovery for native maps.

- `azure_migrate_vmware_target_placement_import_sample.xlsx`
  - Import-oriented VMware inventory workbook paired with a target-placement sample.

- `workload_placement_decision_matrix_sample.csv`
  - Sample decision matrix showing where workloads initially fit: AVS, Azure VMs, or modernization candidate paths.

- `workload_placement_notes_sample.json`
  - Decision factors and notes for the placement sample.

- `app_inventory_sample.json`
  - Sample app portfolio view with owners, criticality, compliance, and target patterns.

- `dependency_map_sample.csv`
  - Sample application dependency map.

- `technology_inventory_sample.csv`
  - Sample VM-to-technology stack mapping.

- `generate_azure_migrate_vmware_sample.py`
  - Regenerates the workbook and sidecar files.

- `generate_azure_migrate_vmware_extended_samples.py`
  - Generates the strict import sample, the 200-VM enterprise sample set, the healthcare-aligned sample set, and the AVS-versus-Azure-VM placement sample.

## Practical recommendation

If your goal is to mimic a full application inventory with dependencies and technologies involved, use a two-artifact model:

1. Use the RVTools-compatible XLSX for Azure Migrate import.
2. Keep the app/dependency/technology files alongside it for architecture, wave planning, and stakeholder review.

That mirrors how Azure Migrate actually works today.

## Recommended use of the new samples

1. `azure_migrate_vmware_rvtools_strict_sample.xlsx`

Use for direct portal import testing with the least ambiguity.

1. `azure_migrate_vmware_enterprise_import_sample.xlsx` plus the `enterprise_*` files

Use when you want a larger mock dataset with portfolio, dependency, and technology context.

Use `azure_migrate_vmware_enterprise_import_sample_with_app_relationships.xlsx` and the `enterprise_azure_migrate_group_*.csv` exports when you want to walk a team through application grouping and portal-based assessment setup.

1. `healthcare_payor_provider_vmware_import_sample.xlsx` plus the `healthcare_*` files

Use when you want a realistic healthcare payor-provider and pediatric research hospital style portfolio for migration workshops.

Use `healthcare_payor_provider_vmware_import_sample_with_app_relationships.xlsx` and the `healthcare_azure_migrate_group_*.csv` exports when the workshop needs explicit clinical application grouping and cutover-wave planning.

1. `azure_migrate_vmware_target_placement_import_sample.xlsx` plus the placement files

Use when you want to discuss why some workloads land on AVS first while others should move toward Azure VMs or modernization targets.

1. `azure_migrate_vmware_enterprise_sql_sap_citrix_workshop.xlsx`

Use when the discussion is centered on clustered SQL, SAP application landscapes, Citrix worker pools, and other technically sensitive migration patterns.

1. `azure_migrate_dependency_discovery_variations_sample.xlsx` plus the `dependency_discovery_*` files

Use when you need to show what Azure Migrate dependency discovery is likely to surface after appliance-based discovery is enabled, including external dependencies, batch windows, bursty sessions, and HA traffic.

1. `azure_migrate_vmware_sample_walkthrough.pptx`

Use when you want a concise presentation that explains how all of the sample artifacts fit together.

## Official references

- VMware import with RVTools XLSX:
  <https://learn.microsoft.com/azure/migrate/tutorial-import-vmware-using-rvtools-xlsx>
- VMware migration entry point:
  <https://learn.microsoft.com/azure/migrate/start-here-vmware>
- Dependency analysis:
  <https://learn.microsoft.com/azure/migrate/concepts-dependency-visualization?view=migrate&context=/azure/migrate/context/vmware-context>
