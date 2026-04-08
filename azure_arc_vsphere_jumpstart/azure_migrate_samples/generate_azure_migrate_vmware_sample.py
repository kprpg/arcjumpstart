from __future__ import annotations

import csv
import json
from pathlib import Path

import xlsxwriter

BASE_DIR = Path(__file__).parent
WORKBOOK_PATH = BASE_DIR / "azure_migrate_vmware_rvtools_plus_app_inventory_sample.xlsx"
APP_JSON_PATH = BASE_DIR / "app_inventory_sample.json"
DEPENDENCY_CSV_PATH = BASE_DIR / "dependency_map_sample.csv"
TECH_CSV_PATH = BASE_DIR / "technology_inventory_sample.csv"

VMS = [
    {
        "vm": "vm-prd-web-01",
        "uuid": "4201b9cc-0001-4000-a001-000000000001",
        "power": "poweredOn",
        "cpus": 4,
        "memory_mib": 16384,
        "provisioned_mib": 262144,
        "in_use_mib": 148320,
        "os": "Microsoft Windows Server 2019 (64-bit)",
        "host": "esx-prod-01",
        "cluster": "cluster-prod-a",
        "datacenter": "dc-primary",
        "app": "contoso-commerce",
        "tier": "web",
        "env": "prod",
        "business_criticality": "high",
        "owner": "digital-commerce",
        "wave": "wave-1",
        "migration_target": "Azure VMware Solution",
        "technologies": ["IIS 10", ".NET Framework 4.8", "Windows Server 2019"],
    },
    {
        "vm": "vm-prd-web-02",
        "uuid": "4201b9cc-0002-4000-a001-000000000002",
        "power": "poweredOn",
        "cpus": 4,
        "memory_mib": 16384,
        "provisioned_mib": 262144,
        "in_use_mib": 142280,
        "os": "Microsoft Windows Server 2019 (64-bit)",
        "host": "esx-prod-02",
        "cluster": "cluster-prod-a",
        "datacenter": "dc-primary",
        "app": "contoso-commerce",
        "tier": "web",
        "env": "prod",
        "business_criticality": "high",
        "owner": "digital-commerce",
        "wave": "wave-1",
        "migration_target": "Azure VMware Solution",
        "technologies": ["IIS 10", ".NET Framework 4.8", "Windows Server 2019"],
    },
    {
        "vm": "vm-prd-app-01",
        "uuid": "4201b9cc-0003-4000-a001-000000000003",
        "power": "poweredOn",
        "cpus": 8,
        "memory_mib": 24576,
        "provisioned_mib": 393216,
        "in_use_mib": 211770,
        "os": "Microsoft Windows Server 2019 (64-bit)",
        "host": "esx-prod-01",
        "cluster": "cluster-prod-a",
        "datacenter": "dc-primary",
        "app": "contoso-commerce",
        "tier": "app",
        "env": "prod",
        "business_criticality": "high",
        "owner": "digital-commerce",
        "wave": "wave-1",
        "migration_target": "Azure VMware Solution",
        "technologies": ["Tomcat 9", "Java 11", "Windows Server 2019"],
    },
    {
        "vm": "vm-prd-db-01",
        "uuid": "4201b9cc-0004-4000-a001-000000000004",
        "power": "poweredOn",
        "cpus": 16,
        "memory_mib": 65536,
        "provisioned_mib": 1048576,
        "in_use_mib": 734003,
        "os": "Microsoft Windows Server 2019 (64-bit)",
        "host": "esx-prod-03",
        "cluster": "cluster-prod-a",
        "datacenter": "dc-primary",
        "app": "contoso-commerce",
        "tier": "database",
        "env": "prod",
        "business_criticality": "high",
        "owner": "data-platform",
        "wave": "wave-2",
        "migration_target": "Azure SQL Managed Instance candidate",
        "technologies": ["SQL Server 2019", "SSIS", "Windows Server 2019"],
    },
    {
        "vm": "vm-prd-api-01",
        "uuid": "4201b9cc-0005-4000-a001-000000000005",
        "power": "poweredOn",
        "cpus": 8,
        "memory_mib": 16384,
        "provisioned_mib": 196608,
        "in_use_mib": 90544,
        "os": "Ubuntu Linux (64-bit)",
        "host": "esx-prod-02",
        "cluster": "cluster-prod-a",
        "datacenter": "dc-primary",
        "app": "order-api",
        "tier": "api",
        "env": "prod",
        "business_criticality": "medium",
        "owner": "integration-platform",
        "wave": "wave-2",
        "migration_target": "Azure VMs",
        "technologies": ["Nginx", "Node.js 18", "Ubuntu 22.04"],
    },
    {
        "vm": "vm-prd-rpt-01",
        "uuid": "4201b9cc-0006-4000-a001-000000000006",
        "power": "poweredOn",
        "cpus": 8,
        "memory_mib": 32768,
        "provisioned_mib": 524288,
        "in_use_mib": 310112,
        "os": "Microsoft Windows Server 2016 (64-bit)",
        "host": "esx-prod-03",
        "cluster": "cluster-prod-a",
        "datacenter": "dc-primary",
        "app": "finance-reporting",
        "tier": "reporting",
        "env": "prod",
        "business_criticality": "medium",
        "owner": "finance-it",
        "wave": "wave-3",
        "migration_target": "Azure VMware Solution",
        "technologies": ["SSRS", "SQL Server 2016", "Windows Server 2016"],
    },
    {
        "vm": "vm-dev-jenkins-01",
        "uuid": "4201b9cc-0007-4000-a001-000000000007",
        "power": "poweredOn",
        "cpus": 4,
        "memory_mib": 8192,
        "provisioned_mib": 131072,
        "in_use_mib": 60218,
        "os": "CentOS 7 (64-bit)",
        "host": "esx-dev-01",
        "cluster": "cluster-dev-a",
        "datacenter": "dc-secondary",
        "app": "devops-shared",
        "tier": "ci-cd",
        "env": "dev",
        "business_criticality": "low",
        "owner": "platform-engineering",
        "wave": "wave-1",
        "migration_target": "Azure VMs",
        "technologies": ["Jenkins", "Docker", "CentOS 7"],
    },
    {
        "vm": "vm-prd-bastion-01",
        "uuid": "4201b9cc-0008-4000-a001-000000000008",
        "power": "poweredOn",
        "cpus": 2,
        "memory_mib": 8192,
        "provisioned_mib": 65536,
        "in_use_mib": 22190,
        "os": "Microsoft Windows Server 2022 (64-bit)",
        "host": "esx-prod-02",
        "cluster": "cluster-prod-a",
        "datacenter": "dc-primary",
        "app": "shared-platform",
        "tier": "management",
        "env": "prod",
        "business_criticality": "medium",
        "owner": "platform-engineering",
        "wave": "wave-0",
        "migration_target": "Azure Virtual Machine",
        "technologies": ["Remote Desktop Services", "Windows Server 2022"],
    },
]

DEPENDENCIES = [
    [
        "contoso-commerce:web",
        "contoso-commerce:app",
        "HTTPS",
        443,
        "synchronous",
        "high",
    ],
    [
        "contoso-commerce:app",
        "contoso-commerce:database",
        "TDS",
        1433,
        "synchronous",
        "critical",
    ],
    ["order-api:api", "contoso-commerce:app", "HTTPS", 8443, "synchronous", "medium"],
    [
        "finance-reporting:reporting",
        "contoso-commerce:database",
        "TDS",
        1433,
        "scheduled",
        "medium",
    ],
    ["devops-shared:ci-cd", "order-api:api", "HTTPS", 443, "scheduled", "low"],
]

APP_INVENTORY = [
    {
        "application_name": "contoso-commerce",
        "business_owner": "VP Digital Commerce",
        "technical_owner": "Digital Commerce Engineering",
        "environment": "prod",
        "criticality": "tier-1",
        "sla": "99.95%",
        "compliance": "PCI",
        "target_pattern": "AVS first, database modernization later",
        "notes": "Keep app tier close to current architecture for initial exit; modernize database after cutover stability.",
    },
    {
        "application_name": "order-api",
        "business_owner": "Head of Integration",
        "technical_owner": "API Platform Team",
        "environment": "prod",
        "criticality": "tier-2",
        "sla": "99.9%",
        "compliance": "internal",
        "target_pattern": "Azure VMs then App Service/AKS review",
        "notes": "Likely modernization candidate after initial rehost based on Node runtime and stateless behavior.",
    },
    {
        "application_name": "finance-reporting",
        "business_owner": "Finance Controller",
        "technical_owner": "Finance IT",
        "environment": "prod",
        "criticality": "tier-2",
        "sla": "99.5%",
        "compliance": "SOX",
        "target_pattern": "AVS or Azure VM",
        "notes": "Watch licensing and SSRS compatibility; reporting batches are latency-sensitive overnight.",
    },
    {
        "application_name": "devops-shared",
        "business_owner": "Director of Engineering",
        "technical_owner": "Platform Engineering",
        "environment": "dev",
        "criticality": "tier-3",
        "sla": "best effort",
        "compliance": "internal",
        "target_pattern": "Azure VM or PaaS replacement",
        "notes": "Good early-wave candidate to validate networking and identity patterns.",
    },
]


def write_sheet(worksheet, headers, rows):
    header_format = WORKBOOK.add_format(
        {"bold": True, "bg_color": "#D9EAF7", "border": 1}
    )
    cell_format = WORKBOOK.add_format({"border": 1})
    wrap_format = WORKBOOK.add_format({"border": 1, "text_wrap": True})

    for col_idx, header in enumerate(headers):
        worksheet.write(0, col_idx, header, header_format)
        worksheet.set_column(col_idx, col_idx, max(14, min(32, len(header) + 4)))

    for row_idx, row in enumerate(rows, start=1):
        for col_idx, value in enumerate(row):
            fmt = (
                wrap_format
                if isinstance(value, str) and len(value) > 40
                else cell_format
            )
            worksheet.write(row_idx, col_idx, value, fmt)

    worksheet.freeze_panes(1, 0)


def build_rvtools_workbook():
    global WORKBOOK
    WORKBOOK = xlsxwriter.Workbook(WORKBOOK_PATH)

    vinfo_headers = [
        "VM",
        "VM UUID",
        "Powerstate",
        "CPUs",
        "Memory",
        "Provisioned MiB",
        "In use MiB",
        "OS according to the configuration file",
    ]
    vinfo_rows = [
        [
            vm["vm"],
            vm["uuid"],
            vm["power"],
            vm["cpus"],
            vm["memory_mib"],
            vm["provisioned_mib"],
            vm["in_use_mib"],
            vm["os"],
        ]
        for vm in VMS
    ]
    write_sheet(WORKBOOK.add_worksheet("vInfo"), vinfo_headers, vinfo_rows)

    vhost_headers = [
        "Host",
        "Cluster",
        "Datacenter",
        "Config status",
        "in Maintenance Mode",
        "in Quarantine Mode",
        "CPU Model",
        "Speed",
        "#CPU",
        "Cores per CPU",
        "# Cores",
        "CPU usage %",
        "# Memory",
        "Memory usage %",
        "VM Used memory",
        "VM Memory Swapped",
        "VM Memory Ballooned",
        "#NICs",
        "# vCPUs",
        "vRAM",
        "ESX Version",
        "Vendor",
        "Model",
        "Object ID",
        "UUID",
    ]
    vhost_rows = [
        [
            "esx-prod-01",
            "cluster-prod-a",
            "dc-primary",
            "green",
            "false",
            "false",
            "Intel Xeon Gold 6338",
            2000,
            2,
            32,
            64,
            61,
            524288,
            72,
            180224,
            0,
            0,
            8,
            48,
            131072,
            "8.0.2",
            "Dell",
            "PowerEdge R760",
            "host-101",
            "host-uuid-101",
        ],
        [
            "esx-prod-02",
            "cluster-prod-a",
            "dc-primary",
            "green",
            "false",
            "false",
            "Intel Xeon Gold 6338",
            2000,
            2,
            32,
            64,
            58,
            524288,
            69,
            166200,
            0,
            0,
            8,
            42,
            114688,
            "8.0.2",
            "Dell",
            "PowerEdge R760",
            "host-102",
            "host-uuid-102",
        ],
        [
            "esx-prod-03",
            "cluster-prod-a",
            "dc-primary",
            "green",
            "false",
            "false",
            "Intel Xeon Gold 6338",
            2000,
            2,
            32,
            64,
            64,
            524288,
            76,
            228112,
            0,
            0,
            8,
            24,
            98304,
            "8.0.2",
            "Dell",
            "PowerEdge R760",
            "host-103",
            "host-uuid-103",
        ],
        [
            "esx-dev-01",
            "cluster-dev-a",
            "dc-secondary",
            "green",
            "false",
            "false",
            "Intel Xeon Silver 4314",
            2400,
            2,
            16,
            32,
            41,
            262144,
            55,
            60218,
            0,
            0,
            4,
            4,
            8192,
            "7.0.3",
            "HPE",
            "ProLiant DL360",
            "host-201",
            "host-uuid-201",
        ],
    ]
    write_sheet(WORKBOOK.add_worksheet("vHost"), vhost_headers, vhost_rows)

    vdatastore_headers = [
        "Name",
        "Object ID",
        "Type",
        "Hosts",
        "Capacity MiB",
        "Provisioned MiB",
        "In Use MiB",
    ]
    vdatastore_rows = [
        [
            "vsan-prod-a",
            "ds-101",
            "vsan",
            "esx-prod-01;esx-prod-02;esx-prod-03",
            6291456,
            3538944,
            2420096,
        ],
        ["vmfs-dev-a", "ds-201", "vmfs", "esx-dev-01", 1048576, 262144, 131072],
    ]
    write_sheet(
        WORKBOOK.add_worksheet("vDatastore"), vdatastore_headers, vdatastore_rows
    )

    vsnapshot_headers = [
        "VM",
        "VM UUID",
        "Powerstate",
        "Size MiB (vmsn)",
        "Size MiB (total)",
        "Quiesced",
        "Datacenter",
        "Cluster",
        "Host",
    ]
    vsnapshot_rows = [
        [
            "vm-prd-db-01",
            "4201b9cc-0004-4000-a001-000000000004",
            "poweredOn",
            512,
            16384,
            "true",
            "dc-primary",
            "cluster-prod-a",
            "esx-prod-03",
        ],
        [
            "vm-dev-jenkins-01",
            "4201b9cc-0007-4000-a001-000000000007",
            "poweredOn",
            256,
            2048,
            "false",
            "dc-secondary",
            "cluster-dev-a",
            "esx-dev-01",
        ],
    ]
    write_sheet(WORKBOOK.add_worksheet("vSnapshot"), vsnapshot_headers, vsnapshot_rows)

    vpartition_headers = ["VM", "VM UUID", "Capacity MiB", "Consumed MiB"]
    vpartition_rows = [
        [vm["vm"], vm["uuid"], vm["provisioned_mib"], vm["in_use_mib"]] for vm in VMS
    ]
    write_sheet(
        WORKBOOK.add_worksheet("vPartition"), vpartition_headers, vpartition_rows
    )

    vmemory_headers = ["VM", "VM UUID", "Size MiB", "Reservation"]
    vmemory_rows = [[vm["vm"], vm["uuid"], vm["memory_mib"], 0] for vm in VMS]
    write_sheet(WORKBOOK.add_worksheet("vMemory"), vmemory_headers, vmemory_rows)

    vdisk_headers = ["VM", "VM UUID", "Shared Bus", "Controller"]
    vdisk_rows = [[vm["vm"], vm["uuid"], "noSharing", "LSI Logic SAS"] for vm in VMS]
    write_sheet(WORKBOOK.add_worksheet("vDisk"), vdisk_headers, vdisk_rows)

    vcd_headers = ["VM", "VM UUID", "Powerstate", "Device Type", "Connected"]
    vcd_rows = [
        [vm["vm"], vm["uuid"], vm["power"], "CD/DVD drive", "false"] for vm in VMS
    ]
    write_sheet(WORKBOOK.add_worksheet("vCD"), vcd_headers, vcd_rows)

    vusb_headers = ["VM", "VM UUID", "Powerstate", "Device Type", "Connected"]
    vusb_rows = [
        [vm["vm"], vm["uuid"], vm["power"], "USB controller", "false"] for vm in VMS
    ]
    write_sheet(WORKBOOK.add_worksheet("vUSB"), vusb_headers, vusb_rows)

    vnetwork_headers = ["VM", "VM UUID", "Switch", "Connected"]
    vnetwork_rows = [
        [
            vm["vm"],
            vm["uuid"],
            "dvSwitch-prod" if "prod" in vm["env"] else "vSwitch-dev",
            "true",
        ]
        for vm in VMS
    ]
    write_sheet(WORKBOOK.add_worksheet("vNetwork"), vnetwork_headers, vnetwork_rows)

    dvport_headers = [
        "Object ID",
        "Port",
        "Switch",
        "Type",
        "VLAN",
        "Allow Promiscuous",
        "Mac changes",
        "Forged Transmits",
    ]
    dvport_rows = [
        [
            "dvport-1001",
            "1001",
            "dvSwitch-prod",
            "distributed",
            120,
            "false",
            "false",
            "false",
        ],
        [
            "dvport-1002",
            "1002",
            "dvSwitch-prod",
            "distributed",
            130,
            "false",
            "false",
            "false",
        ],
        [
            "dvport-2001",
            "2001",
            "vSwitch-dev",
            "standard",
            220,
            "false",
            "false",
            "false",
        ],
    ]
    write_sheet(WORKBOOK.add_worksheet("dvPort"), dvport_headers, dvport_rows)

    app_headers = [
        "application_name",
        "business_owner",
        "technical_owner",
        "environment",
        "criticality",
        "sla",
        "compliance",
        "target_pattern",
        "notes",
    ]
    app_rows = [[item[key] for key in app_headers] for item in APP_INVENTORY]
    write_sheet(WORKBOOK.add_worksheet("AppInventory"), app_headers, app_rows)

    dep_headers = [
        "source",
        "target",
        "protocol",
        "port",
        "interaction_type",
        "criticality",
    ]
    write_sheet(WORKBOOK.add_worksheet("Dependencies"), dep_headers, DEPENDENCIES)

    tech_headers = [
        "vm",
        "application_name",
        "tier",
        "technologies",
        "suggested_target",
        "migration_wave",
    ]
    tech_rows = [
        [
            vm["vm"],
            vm["app"],
            vm["tier"],
            "; ".join(vm["technologies"]),
            vm["migration_target"],
            vm["wave"],
        ]
        for vm in VMS
    ]
    write_sheet(WORKBOOK.add_worksheet("TechnologyStack"), tech_headers, tech_rows)

    notes_sheet = WORKBOOK.add_worksheet("ReadMe")
    notes = [
        [
            "Purpose",
            "Sample VMware inventory workbook for Azure Migrate import testing plus extra sheets for application-level planning.",
        ],
        [
            "Importable by Azure Migrate",
            "Required RVTools-style sheets only: vInfo, vHost, vDatastore, vSnapshot, vPartition, vMemory, vDisk, vCD, vUSB, vNetwork, dvPort.",
        ],
        [
            "Not imported by Azure Migrate",
            "AppInventory, Dependencies, TechnologyStack, and ReadMe sheets are for planning only.",
        ],
        [
            "Important",
            "Azure Migrate dependency analysis and app dependency grouping come from appliance or agent discovery, not from these custom sheets.",
        ],
    ]
    write_sheet(notes_sheet, ["key", "value"], notes)

    WORKBOOK.close()


def write_json_and_csv_sidecars():
    with APP_JSON_PATH.open("w", encoding="utf-8") as handle:
        json.dump(
            {"applications": APP_INVENTORY, "virtual_machines": VMS}, handle, indent=2
        )

    with DEPENDENCY_CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["source", "target", "protocol", "port", "interaction_type", "criticality"]
        )
        writer.writerows(DEPENDENCIES)

    with TECH_CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "vm",
                "application_name",
                "tier",
                "business_criticality",
                "owner",
                "technologies",
                "suggested_target",
                "migration_wave",
            ]
        )
        for vm in VMS:
            writer.writerow(
                [
                    vm["vm"],
                    vm["app"],
                    vm["tier"],
                    vm["business_criticality"],
                    vm["owner"],
                    "; ".join(vm["technologies"]),
                    vm["migration_target"],
                    vm["wave"],
                ]
            )


def main():
    build_rvtools_workbook()
    write_json_and_csv_sidecars()
    print(f"Created {WORKBOOK_PATH}")
    print(f"Created {APP_JSON_PATH}")
    print(f"Created {DEPENDENCY_CSV_PATH}")
    print(f"Created {TECH_CSV_PATH}")


if __name__ == "__main__":
    main()
