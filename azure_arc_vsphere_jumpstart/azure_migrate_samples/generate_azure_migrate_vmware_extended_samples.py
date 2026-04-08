from __future__ import annotations

import csv
import json
from pathlib import Path

import xlsxwriter

BASE_DIR = Path(__file__).parent

STRICT_WORKBOOK = BASE_DIR / "azure_migrate_vmware_rvtools_strict_sample.xlsx"
ENTERPRISE_WORKBOOK = BASE_DIR / "azure_migrate_vmware_enterprise_import_sample.xlsx"
ENTERPRISE_APP_JSON = BASE_DIR / "enterprise_app_inventory_sample.json"
ENTERPRISE_DEP_CSV = BASE_DIR / "enterprise_dependency_map_sample.csv"
ENTERPRISE_TECH_CSV = BASE_DIR / "enterprise_technology_inventory_sample.csv"
ENTERPRISE_GROUPS_CSV = BASE_DIR / "enterprise_workload_groups_sample.csv"
HEALTHCARE_WORKBOOK = BASE_DIR / "healthcare_payor_provider_vmware_import_sample.xlsx"
HEALTHCARE_APP_JSON = BASE_DIR / "healthcare_payor_provider_app_inventory_sample.json"
HEALTHCARE_DEP_CSV = BASE_DIR / "healthcare_payor_provider_dependency_map_sample.csv"
HEALTHCARE_TECH_CSV = (
    BASE_DIR / "healthcare_payor_provider_technology_inventory_sample.csv"
)
HEALTHCARE_GROUPS_CSV = (
    BASE_DIR / "healthcare_payor_provider_workload_groups_sample.csv"
)
PLACEMENT_WORKBOOK = (
    BASE_DIR / "azure_migrate_vmware_target_placement_import_sample.xlsx"
)
PLACEMENT_MATRIX_CSV = BASE_DIR / "workload_placement_decision_matrix_sample.csv"
PLACEMENT_NOTES_JSON = BASE_DIR / "workload_placement_notes_sample.json"

RVTOOLS_SHEETS = [
    "vInfo",
    "vHost",
    "vDatastore",
    "vSnapshot",
    "vPartition",
    "vMemory",
    "vDisk",
    "vCD",
    "vUSB",
    "vNetwork",
    "dvPort",
]

VINFO_HEADERS = [
    "VM",
    "VM UUID",
    "Powerstate",
    "CPUs",
    "Memory",
    "Provisioned MiB",
    "In use MiB",
    "OS according to the configuration file",
]
VHOST_HEADERS = [
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
VDATASTORE_HEADERS = [
    "Name",
    "Object ID",
    "Type",
    "Hosts",
    "Capacity MiB",
    "Provisioned MiB",
    "In Use MiB",
]
VSNAPSHOT_HEADERS = [
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
VPARTITION_HEADERS = ["VM", "VM UUID", "Capacity MiB", "Consumed MiB"]
VMEMORY_HEADERS = ["VM", "VM UUID", "Size MiB", "Reservation"]
VDISK_HEADERS = ["VM", "VM UUID", "Shared Bus", "Controller"]
VCD_HEADERS = ["VM", "VM UUID", "Powerstate", "Device Type", "Connected"]
VUSB_HEADERS = ["VM", "VM UUID", "Powerstate", "Device Type", "Connected"]
VNETWORK_HEADERS = ["VM", "VM UUID", "Switch", "Connected"]
DVPORT_HEADERS = [
    "Object ID",
    "Port",
    "Switch",
    "Type",
    "VLAN",
    "Allow Promiscuous",
    "Mac changes",
    "Forged Transmits",
]


def make_uuid(index: int) -> str:
    return f"5201b9cc-{index:04d}-4000-a001-{index:012d}"


def write_sheet(workbook, worksheet, headers, rows):
    header_format = workbook.add_format(
        {"bold": True, "bg_color": "#D9EAF7", "border": 1}
    )
    cell_format = workbook.add_format({"border": 1})
    wrap_format = workbook.add_format({"border": 1, "text_wrap": True})

    for col_idx, header in enumerate(headers):
        worksheet.write(0, col_idx, header, header_format)
        worksheet.set_column(col_idx, col_idx, max(14, min(34, len(header) + 4)))

    for row_idx, row in enumerate(rows, start=1):
        for col_idx, value in enumerate(row):
            fmt = (
                wrap_format
                if isinstance(value, str) and len(value) > 42
                else cell_format
            )
            worksheet.write(row_idx, col_idx, value, fmt)

    worksheet.freeze_panes(1, 0)


def vm_to_vinfo_row(vm):
    return [
        vm["vm"],
        vm["uuid"],
        vm["power"],
        vm["cpus"],
        vm["memory_mib"],
        vm["provisioned_mib"],
        vm["in_use_mib"],
        vm["os"],
    ]


def build_host_rows(hosts):
    return [
        [
            host["host"],
            host["cluster"],
            host["datacenter"],
            "green",
            "false",
            "false",
            host["cpu_model"],
            host["speed"],
            host["socket_count"],
            host["cores_per_socket"],
            host["socket_count"] * host["cores_per_socket"],
            host["cpu_usage_pct"],
            host["memory_mib_total"],
            host["memory_usage_pct"],
            host["vm_used_memory_mib"],
            0,
            0,
            host["nics"],
            host["vcpus_allocated"],
            host["vram_allocated_mib"],
            host["esx_version"],
            host["vendor"],
            host["model"],
            host["object_id"],
            host["uuid"],
        ]
        for host in hosts
    ]


def build_rvtools_workbook(
    path: Path,
    vms: list[dict],
    hosts: list[dict],
    datastores: list[dict],
    networks: list[dict],
    snapshots: list[list],
):
    workbook = xlsxwriter.Workbook(path)
    write_sheet(
        workbook,
        workbook.add_worksheet("vInfo"),
        VINFO_HEADERS,
        [vm_to_vinfo_row(vm) for vm in vms],
    )
    write_sheet(
        workbook, workbook.add_worksheet("vHost"), VHOST_HEADERS, build_host_rows(hosts)
    )
    write_sheet(
        workbook,
        workbook.add_worksheet("vDatastore"),
        VDATASTORE_HEADERS,
        [
            [
                d["name"],
                d["object_id"],
                d["type"],
                d["hosts"],
                d["capacity_mib"],
                d["provisioned_mib"],
                d["in_use_mib"],
            ]
            for d in datastores
        ],
    )
    write_sheet(
        workbook, workbook.add_worksheet("vSnapshot"), VSNAPSHOT_HEADERS, snapshots
    )
    write_sheet(
        workbook,
        workbook.add_worksheet("vPartition"),
        VPARTITION_HEADERS,
        [[vm["vm"], vm["uuid"], vm["provisioned_mib"], vm["in_use_mib"]] for vm in vms],
    )
    write_sheet(
        workbook,
        workbook.add_worksheet("vMemory"),
        VMEMORY_HEADERS,
        [[vm["vm"], vm["uuid"], vm["memory_mib"], 0] for vm in vms],
    )
    write_sheet(
        workbook,
        workbook.add_worksheet("vDisk"),
        VDISK_HEADERS,
        [[vm["vm"], vm["uuid"], "noSharing", "LSI Logic SAS"] for vm in vms],
    )
    write_sheet(
        workbook,
        workbook.add_worksheet("vCD"),
        VCD_HEADERS,
        [[vm["vm"], vm["uuid"], vm["power"], "CD/DVD drive", "false"] for vm in vms],
    )
    write_sheet(
        workbook,
        workbook.add_worksheet("vUSB"),
        VUSB_HEADERS,
        [[vm["vm"], vm["uuid"], vm["power"], "USB controller", "false"] for vm in vms],
    )
    write_sheet(
        workbook,
        workbook.add_worksheet("vNetwork"),
        VNETWORK_HEADERS,
        [[vm["vm"], vm["uuid"], vm["switch"], "true"] for vm in vms],
    )
    write_sheet(
        workbook,
        workbook.add_worksheet("dvPort"),
        DVPORT_HEADERS,
        [
            [
                n["object_id"],
                n["port"],
                n["switch"],
                n["type"],
                n["vlan"],
                "false",
                "false",
                "false",
            ]
            for n in networks
        ],
    )
    workbook.close()


def base_hosts_small():
    return [
        {
            "host": "esx-prod-01",
            "cluster": "cluster-prod-a",
            "datacenter": "dc-primary",
            "cpu_model": "Intel Xeon Gold 6338",
            "speed": 2000,
            "socket_count": 2,
            "cores_per_socket": 32,
            "cpu_usage_pct": 61,
            "memory_mib_total": 524288,
            "memory_usage_pct": 72,
            "vm_used_memory_mib": 180224,
            "nics": 8,
            "vcpus_allocated": 48,
            "vram_allocated_mib": 131072,
            "esx_version": "8.0.2",
            "vendor": "Dell",
            "model": "PowerEdge R760",
            "object_id": "host-101",
            "uuid": "host-uuid-101",
        },
        {
            "host": "esx-prod-02",
            "cluster": "cluster-prod-a",
            "datacenter": "dc-primary",
            "cpu_model": "Intel Xeon Gold 6338",
            "speed": 2000,
            "socket_count": 2,
            "cores_per_socket": 32,
            "cpu_usage_pct": 58,
            "memory_mib_total": 524288,
            "memory_usage_pct": 69,
            "vm_used_memory_mib": 166200,
            "nics": 8,
            "vcpus_allocated": 42,
            "vram_allocated_mib": 114688,
            "esx_version": "8.0.2",
            "vendor": "Dell",
            "model": "PowerEdge R760",
            "object_id": "host-102",
            "uuid": "host-uuid-102",
        },
        {
            "host": "esx-prod-03",
            "cluster": "cluster-prod-a",
            "datacenter": "dc-primary",
            "cpu_model": "Intel Xeon Gold 6338",
            "speed": 2000,
            "socket_count": 2,
            "cores_per_socket": 32,
            "cpu_usage_pct": 64,
            "memory_mib_total": 524288,
            "memory_usage_pct": 76,
            "vm_used_memory_mib": 228112,
            "nics": 8,
            "vcpus_allocated": 24,
            "vram_allocated_mib": 98304,
            "esx_version": "8.0.2",
            "vendor": "Dell",
            "model": "PowerEdge R760",
            "object_id": "host-103",
            "uuid": "host-uuid-103",
        },
        {
            "host": "esx-dev-01",
            "cluster": "cluster-dev-a",
            "datacenter": "dc-secondary",
            "cpu_model": "Intel Xeon Silver 4314",
            "speed": 2400,
            "socket_count": 2,
            "cores_per_socket": 16,
            "cpu_usage_pct": 41,
            "memory_mib_total": 262144,
            "memory_usage_pct": 55,
            "vm_used_memory_mib": 60218,
            "nics": 4,
            "vcpus_allocated": 4,
            "vram_allocated_mib": 8192,
            "esx_version": "7.0.3",
            "vendor": "HPE",
            "model": "ProLiant DL360",
            "object_id": "host-201",
            "uuid": "host-uuid-201",
        },
    ]


def base_datastores_small():
    return [
        {
            "name": "vsan-prod-a",
            "object_id": "ds-101",
            "type": "vsan",
            "hosts": "esx-prod-01;esx-prod-02;esx-prod-03",
            "capacity_mib": 6291456,
            "provisioned_mib": 3538944,
            "in_use_mib": 2420096,
        },
        {
            "name": "vmfs-dev-a",
            "object_id": "ds-201",
            "type": "vmfs",
            "hosts": "esx-dev-01",
            "capacity_mib": 1048576,
            "provisioned_mib": 262144,
            "in_use_mib": 131072,
        },
    ]


def base_networks_small():
    return [
        {
            "object_id": "dvport-1001",
            "port": "1001",
            "switch": "dvSwitch-prod",
            "type": "distributed",
            "vlan": 120,
        },
        {
            "object_id": "dvport-1002",
            "port": "1002",
            "switch": "dvSwitch-prod",
            "type": "distributed",
            "vlan": 130,
        },
        {
            "object_id": "dvport-2001",
            "port": "2001",
            "switch": "vSwitch-dev",
            "type": "standard",
            "vlan": 220,
        },
    ]


def small_vms():
    raw = [
        (
            "vm-prd-web-01",
            1,
            "poweredOn",
            4,
            16384,
            262144,
            148320,
            "Microsoft Windows Server 2019 (64-bit)",
            "esx-prod-01",
            "cluster-prod-a",
            "dc-primary",
            "dvSwitch-prod",
        ),
        (
            "vm-prd-web-02",
            2,
            "poweredOn",
            4,
            16384,
            262144,
            142280,
            "Microsoft Windows Server 2019 (64-bit)",
            "esx-prod-02",
            "cluster-prod-a",
            "dc-primary",
            "dvSwitch-prod",
        ),
        (
            "vm-prd-app-01",
            3,
            "poweredOn",
            8,
            24576,
            393216,
            211770,
            "Microsoft Windows Server 2019 (64-bit)",
            "esx-prod-01",
            "cluster-prod-a",
            "dc-primary",
            "dvSwitch-prod",
        ),
        (
            "vm-prd-db-01",
            4,
            "poweredOn",
            16,
            65536,
            1048576,
            734003,
            "Microsoft Windows Server 2019 (64-bit)",
            "esx-prod-03",
            "cluster-prod-a",
            "dc-primary",
            "dvSwitch-prod",
        ),
        (
            "vm-prd-api-01",
            5,
            "poweredOn",
            8,
            16384,
            196608,
            90544,
            "Ubuntu Linux (64-bit)",
            "esx-prod-02",
            "cluster-prod-a",
            "dc-primary",
            "dvSwitch-prod",
        ),
        (
            "vm-prd-rpt-01",
            6,
            "poweredOn",
            8,
            32768,
            524288,
            310112,
            "Microsoft Windows Server 2016 (64-bit)",
            "esx-prod-03",
            "cluster-prod-a",
            "dc-primary",
            "dvSwitch-prod",
        ),
        (
            "vm-dev-jenkins-01",
            7,
            "poweredOn",
            4,
            8192,
            131072,
            60218,
            "CentOS 7 (64-bit)",
            "esx-dev-01",
            "cluster-dev-a",
            "dc-secondary",
            "vSwitch-dev",
        ),
        (
            "vm-prd-bastion-01",
            8,
            "poweredOn",
            2,
            8192,
            65536,
            22190,
            "Microsoft Windows Server 2022 (64-bit)",
            "esx-prod-02",
            "cluster-prod-a",
            "dc-primary",
            "dvSwitch-prod",
        ),
    ]
    return [
        {
            "vm": item[0],
            "uuid": make_uuid(item[1]),
            "power": item[2],
            "cpus": item[3],
            "memory_mib": item[4],
            "provisioned_mib": item[5],
            "in_use_mib": item[6],
            "os": item[7],
            "host": item[8],
            "cluster": item[9],
            "datacenter": item[10],
            "switch": item[11],
        }
        for item in raw
    ]


def small_snapshots(vms):
    by_name = {vm["vm"]: vm for vm in vms}
    return [
        [
            "vm-prd-db-01",
            by_name["vm-prd-db-01"]["uuid"],
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
            by_name["vm-dev-jenkins-01"]["uuid"],
            "poweredOn",
            256,
            2048,
            "false",
            "dc-secondary",
            "cluster-dev-a",
            "esx-dev-01",
        ],
    ]


def build_dataset_from_templates(
    app_templates: list[dict],
    tech_profiles: dict,
    hosts: list[dict],
    datastores: list[dict],
    networks: list[dict],
    start_index: int,
    scenario: str,
):
    vms = []
    apps = []
    dependencies = []
    tech_rows = []
    groups = []
    vm_index = start_index
    prod_hosts = [host for host in hosts if host["datacenter"] == "dc-primary"]
    non_prod_hosts = [host for host in hosts if host["datacenter"] != "dc-primary"]
    host_cursor = 0

    for app_id, template in enumerate(app_templates, start=1):
        app_name = template["name"]
        env = template.get("environment", "prod")
        app_vms = []
        for tier_name, count, cpus, memory_mib, profile_name in template["tier_specs"]:
            profile = tech_profiles[profile_name]
            for instance in range(1, count + 1):
                host_pool = (
                    prod_hosts if env == "prod" else non_prod_hosts or prod_hosts
                )
                host = host_pool[host_cursor % len(host_pool)]
                host_cursor += 1
                scale_multiplier = profile.get(
                    "storage_multiplier",
                    12 if tier_name in {"db", "etl", "compute"} else 8,
                )
                provisioned = memory_mib * scale_multiplier
                used_factor = profile.get(
                    "used_factor", 0.71 if tier_name == "db" else 0.56
                )
                used = int(provisioned * used_factor) + ((instance + app_id) % 5) * 384
                os_options = profile.get("os_options", [profile["os"]])
                os_value = os_options[(instance + app_id) % len(os_options)]
                power = "poweredOn"
                if env != "prod" and instance % 4 == 0:
                    power = "poweredOff"
                elif tier_name in {"worker", "batch", "compute"} and instance % 9 == 0:
                    power = "poweredOff"

                network_tier = profile.get("network_tier")
                if not network_tier:
                    if env != "prod":
                        network_tier = "dev"
                    elif tier_name == "db":
                        network_tier = "db"
                    elif tier_name in {
                        "app",
                        "api",
                        "broker",
                        "idm",
                        "etl",
                        "reporting",
                        "sapapp",
                        "storefront",
                        "controller",
                        "batch",
                        "compute",
                        "citrix",
                        "presentation",
                    }:
                        network_tier = "app"
                    else:
                        network_tier = "web"

                switch = profile.get(
                    "switch_override",
                    "vSwitch-dev"
                    if network_tier == "dev"
                    else "dvSwitch-prod-db"
                    if network_tier == "db"
                    else "dvSwitch-prod-app"
                    if network_tier == "app"
                    else "dvSwitch-prod-web",
                )

                vm = {
                    "vm": f"vm-{env}-{app_name[:18]}-{tier_name[:6]}-{instance:02d}",
                    "uuid": make_uuid(vm_index),
                    "power": power,
                    "cpus": cpus
                    + (1 if profile.get("cpu_burst") and instance % 3 == 0 else 0),
                    "memory_mib": memory_mib
                    + (
                        2048 if profile.get("memory_burst") and instance % 2 == 0 else 0
                    ),
                    "provisioned_mib": provisioned,
                    "in_use_mib": used,
                    "os": os_value,
                    "host": host["host"],
                    "cluster": host["cluster"],
                    "datacenter": host["datacenter"],
                    "switch": switch,
                    "application_name": app_name,
                    "tier": tier_name,
                    "environment": env,
                    "criticality": template["criticality"],
                    "owner": template["owner"],
                    "compliance": template["compliance"],
                    "technologies": profile["tech"] + [os_value.split(" (")[0]],
                    "suggested_target": profile["target"],
                    "wave": template.get(
                        "wave",
                        "wave-1"
                        if template["criticality"] == "tier-3"
                        else "wave-2"
                        if tier_name in {"web", "api", "ci", "worker", "storefront"}
                        else "wave-3",
                    ),
                }
                vms.append(vm)
                app_vms.append(vm)
                tech_rows.append(
                    [
                        vm["vm"],
                        vm["application_name"],
                        vm["tier"],
                        vm["criticality"],
                        vm["owner"],
                        "; ".join(vm["technologies"]),
                        vm["suggested_target"],
                        vm["wave"],
                    ]
                )
                vm_index += 1

        apps.append(
            {
                "application_name": app_name,
                "business_owner": template["owner"].replace("-", " ").title(),
                "technical_owner": f"{template['owner'].replace('-', ' ').title()} Team",
                "environment": env,
                "criticality": template["criticality"],
                "sla": template.get(
                    "sla",
                    "99.95%"
                    if template["criticality"] == "tier-1"
                    else "99.9%"
                    if template["criticality"] == "tier-2"
                    else "best effort",
                ),
                "compliance": template["compliance"],
                "target_pattern": template["pattern"],
                "notes": template.get(
                    "notes",
                    f"Synthetic {scenario} application {app_id} for VMware to Azure migration testing.",
                ),
            }
        )
        groups.append(
            [
                app_name,
                env,
                template["criticality"],
                template["owner"],
                len(app_vms),
                template["pattern"],
            ]
        )

        ordered_tiers = [tier for tier, *_ in template["tier_specs"]]
        protocol_map = template.get("protocol_map", {})
        port_map = template.get("port_map", {})
        interaction = template.get("interaction_type", "synchronous")
        for left, right in zip(ordered_tiers, ordered_tiers[1:]):
            dependencies.append(
                [
                    f"{app_name}:{left}",
                    f"{app_name}:{right}",
                    protocol_map.get(
                        (left, right), "HTTPS" if right != "db" else "TDS"
                    ),
                    port_map.get((left, right), 443 if right != "db" else 1433),
                    interaction,
                    "critical" if template["criticality"] == "tier-1" else "medium",
                ]
            )

    snapshots = []
    for vm in vms[:: max(1, len(vms) // 18)]:
        snapshots.append(
            [
                vm["vm"],
                vm["uuid"],
                vm["power"],
                512,
                8192 if vm["tier"] != "db" else 16384,
                "true" if vm["tier"] == "db" else "false",
                vm["datacenter"],
                vm["cluster"],
                vm["host"],
            ]
        )

    return {
        "vms": vms,
        "hosts": hosts,
        "datastores": datastores,
        "networks": networks,
        "snapshots": snapshots,
        "applications": apps,
        "dependencies": dependencies,
        "technology_rows": tech_rows,
        "groups": groups,
    }


def build_enterprise_dataset():
    app_templates = [
        {
            "name": "commerce-java",
            "tier_specs": [
                ("web", 6, 4, 16384, "windows-web"),
                ("app", 6, 8, 24576, "java-app"),
                ("db", 2, 16, 65536, "sql-db"),
            ],
            "criticality": "tier-1",
            "owner": "digital-commerce",
            "compliance": "PCI",
            "pattern": "Three-tier Java estate on AVS first, then selective modernization",
            "notes": "Classic three-tier Java estate with high change control and low cutover tolerance.",
        },
        {
            "name": "member-dotnet",
            "tier_specs": [
                ("web", 5, 4, 16384, "windows-web"),
                ("app", 5, 8, 24576, "dotnet-app"),
                ("db", 2, 12, 49152, "sql-db"),
            ],
            "criticality": "tier-1",
            "owner": "member-platform",
            "compliance": "PII",
            "pattern": "Three-tier .NET estate rehost first, App Service review later",
            "notes": "Three-tier .NET workload with gradual move toward Azure-native app hosting.",
        },
        {
            "name": "sap-s4hana",
            "tier_specs": [
                ("sapweb", 2, 4, 16384, "sap-web"),
                ("sapapp", 6, 12, 65536, "sap-app"),
                ("batch", 4, 8, 32768, "sap-batch"),
                ("db", 2, 24, 131072, "hana-db"),
            ],
            "criticality": "tier-1",
            "owner": "erp-platform",
            "compliance": "SOX",
            "pattern": "Conservative AVS-led SAP migration with later platform optimization",
            "protocol_map": {
                ("sapweb", "sapapp"): "HTTPS",
                ("sapapp", "batch"): "RFC",
                ("batch", "db"): "SQL",
            },
            "port_map": {("sapapp", "batch"): 3300, ("batch", "db"): 30015},
            "notes": "SAP S/4HANA style footprint with presentation, app, batch, and HANA database tiers.",
        },
        {
            "name": "sap-bw",
            "tier_specs": [
                ("sapapp", 4, 10, 49152, "sap-app"),
                ("batch", 4, 8, 32768, "sap-batch"),
                ("db", 2, 20, 98304, "hana-db"),
            ],
            "criticality": "tier-1",
            "owner": "data-warehouse",
            "compliance": "SOX",
            "pattern": "AVS-first SAP analytics estate",
            "protocol_map": {("sapapp", "batch"): "RFC", ("batch", "db"): "SQL"},
            "port_map": {("sapapp", "batch"): 3300, ("batch", "db"): 30015},
        },
        {
            "name": "citrix-vdi",
            "tier_specs": [
                ("controller", 2, 6, 16384, "citrix-controller"),
                ("storefront", 2, 4, 12288, "citrix-storefront"),
                ("license", 1, 2, 8192, "citrix-license"),
                ("worker", 24, 4, 16384, "citrix-worker"),
                ("db", 2, 8, 32768, "sql-db"),
            ],
            "criticality": "tier-1",
            "owner": "end-user-compute",
            "compliance": "internal",
            "pattern": "Citrix estate retained short-term while Azure Virtual Desktop options are evaluated",
            "protocol_map": {
                ("controller", "storefront"): "HTTPS",
                ("storefront", "license"): "TCP",
                ("license", "worker"): "ICA",
                ("worker", "db"): "TDS",
            },
            "port_map": {
                ("storefront", "license"): 7279,
                ("license", "worker"): 1494,
                ("worker", "db"): 1433,
            },
            "notes": "Citrix control plane plus worker pool for EUC migration and cost-analysis scenarios.",
        },
        {
            "name": "payments-sqlao",
            "tier_specs": [
                ("api", 4, 8, 16384, "linux-api"),
                ("app", 4, 8, 24576, "windows-app"),
                ("dbprimary", 1, 16, 65536, "sql-ao-db"),
                ("dbsecondary", 1, 16, 65536, "sql-ao-db"),
                ("witness", 1, 2, 8192, "sql-witness"),
            ],
            "criticality": "tier-1",
            "owner": "payments",
            "compliance": "PCI",
            "pattern": "SQL Always On workload with AVS or Azure VM split depending latency and support model",
            "protocol_map": {
                ("api", "app"): "HTTPS",
                ("app", "dbprimary"): "TDS",
                ("dbprimary", "dbsecondary"): "HADR",
                ("dbsecondary", "witness"): "TCP",
            },
            "port_map": {
                ("app", "dbprimary"): 1433,
                ("dbprimary", "dbsecondary"): 5022,
                ("dbsecondary", "witness"): 59999,
            },
            "notes": "SQL Always On style workload with HA nodes and quorum witness.",
        },
        {
            "name": "ehr-core",
            "tier_specs": [
                ("web", 4, 4, 16384, "windows-web"),
                ("app", 8, 8, 32768, "windows-app"),
                ("db", 4, 16, 65536, "sql-db"),
            ],
            "criticality": "tier-1",
            "owner": "clinical-platform",
            "compliance": "HIPAA",
            "pattern": "Rehost first with staged application and database modernization",
        },
        {
            "name": "claims-core",
            "tier_specs": [
                ("web", 4, 4, 12288, "windows-web"),
                ("api", 4, 8, 16384, "linux-api"),
                ("db", 2, 12, 32768, "postgres-db"),
            ],
            "criticality": "tier-2",
            "owner": "claims-it",
            "compliance": "PII",
            "pattern": "Azure VM and managed database mix",
        },
        {
            "name": "provider-portal",
            "tier_specs": [
                ("web", 4, 4, 12288, "windows-web"),
                ("app", 4, 6, 16384, "dotnet-app"),
                ("db", 2, 8, 32768, "sql-db"),
            ],
            "criticality": "tier-2",
            "owner": "provider-digital",
            "compliance": "PII",
            "pattern": "Three-tier .NET portal estate with future App Service option",
        },
        {
            "name": "integration-bus",
            "tier_specs": [
                ("broker", 4, 6, 12288, "linux-app"),
                ("api", 4, 6, 12288, "linux-api"),
            ],
            "criticality": "tier-2",
            "owner": "integration-platform",
            "compliance": "internal",
            "pattern": "Azure VM then container review",
        },
        {
            "name": "identity-services",
            "tier_specs": [
                ("idm", 4, 4, 16384, "windows-app"),
                ("db", 2, 8, 32768, "sql-db"),
            ],
            "criticality": "tier-1",
            "owner": "security-engineering",
            "compliance": "internal",
            "pattern": "Conservative AVS-first identity estate",
        },
        {
            "name": "data-warehouse",
            "tier_specs": [
                ("etl", 4, 8, 24576, "linux-etl"),
                ("reporting", 4, 8, 24576, "windows-app"),
                ("db", 2, 16, 65536, "sql-db"),
            ],
            "criticality": "tier-2",
            "owner": "data-platform",
            "compliance": "internal",
            "pattern": "Azure VM then analytics modernization",
        },
        {
            "name": "pacs-imaging",
            "tier_specs": [
                ("web", 2, 4, 12288, "windows-web"),
                ("app", 4, 8, 24576, "windows-app"),
                ("db", 2, 12, 49152, "sql-db"),
            ],
            "criticality": "tier-1",
            "owner": "imaging-services",
            "compliance": "HIPAA",
            "pattern": "Conservative migration due to imaging latency and archive dependencies",
        },
        {
            "name": "lab-systems",
            "tier_specs": [
                ("app", 4, 6, 16384, "windows-app"),
                ("db", 2, 8, 32768, "sql-db"),
            ],
            "criticality": "tier-2",
            "owner": "lab-it",
            "compliance": "HIPAA",
            "pattern": "AVS or Azure VM depending analyzer connectivity",
        },
        {
            "name": "pharmacy",
            "tier_specs": [
                ("app", 4, 6, 16384, "windows-app"),
                ("db", 2, 8, 32768, "sql-db"),
            ],
            "criticality": "tier-2",
            "owner": "pharmacy-it",
            "compliance": "HIPAA",
            "pattern": "Rehost with later modernization assessment",
        },
        {
            "name": "call-center",
            "tier_specs": [
                ("web", 4, 4, 12288, "windows-web"),
                ("app", 4, 6, 16384, "dotnet-app"),
                ("db", 2, 8, 32768, "sql-db"),
            ],
            "criticality": "tier-2",
            "owner": "customer-ops",
            "compliance": "PII",
            "pattern": "Azure VM and App Service hybrid path",
        },
        {
            "name": "research-genomics",
            "tier_specs": [
                ("etl", 4, 8, 32768, "linux-etl"),
                ("compute", 8, 12, 49152, "linux-compute"),
                ("db", 2, 16, 65536, "postgres-db"),
            ],
            "criticality": "tier-2",
            "owner": "research-platform",
            "compliance": "research-data",
            "pattern": "Azure VM compute burst with later HPC and data-lake review",
        },
        {
            "name": "devops-shared",
            "tier_specs": [
                ("ci", 2, 4, 8192, "linux-ci"),
                ("artifact", 2, 4, 12288, "linux-app"),
            ],
            "criticality": "tier-3",
            "owner": "platform-engineering",
            "compliance": "internal",
            "pattern": "Azure VMs or PaaS replacement",
            "environment": "dev",
        },
    ]

    tech_profiles = {
        "windows-web": {
            "os": "Microsoft Windows Server 2019 (64-bit)",
            "os_options": [
                "Microsoft Windows Server 2019 (64-bit)",
                "Microsoft Windows Server 2022 (64-bit)",
            ],
            "tech": ["IIS 10", ".NET Framework 4.8"],
            "target": "Azure VMware Solution",
            "memory_burst": True,
        },
        "java-app": {
            "os": "Microsoft Windows Server 2019 (64-bit)",
            "os_options": [
                "Microsoft Windows Server 2019 (64-bit)",
                "Red Hat Enterprise Linux 8 (64-bit)",
            ],
            "tech": ["Tomcat 9", "Java 11"],
            "target": "Azure VMware Solution",
            "cpu_burst": True,
        },
        "windows-app": {
            "os": "Microsoft Windows Server 2019 (64-bit)",
            "os_options": [
                "Microsoft Windows Server 2019 (64-bit)",
                "Microsoft Windows Server 2022 (64-bit)",
            ],
            "tech": ["Windows Service", ".NET 6"],
            "target": "Azure Virtual Machines",
            "memory_burst": True,
        },
        "sql-db": {
            "os": "Microsoft Windows Server 2019 (64-bit)",
            "os_options": [
                "Microsoft Windows Server 2019 (64-bit)",
                "Microsoft Windows Server 2022 (64-bit)",
            ],
            "tech": ["SQL Server 2019", "SSIS"],
            "target": "Azure SQL Managed Instance candidate",
            "storage_multiplier": 16,
            "used_factor": 0.74,
            "network_tier": "db",
        },
        "postgres-db": {
            "os": "Ubuntu Linux (64-bit)",
            "tech": ["PostgreSQL 14", "Patroni"],
            "target": "Azure Database for PostgreSQL candidate",
            "storage_multiplier": 14,
            "used_factor": 0.67,
            "network_tier": "db",
        },
        "oracle-db": {
            "os": "Oracle Linux 8 (64-bit)",
            "tech": ["Oracle Database 19c"],
            "target": "Azure VMware Solution",
            "storage_multiplier": 18,
            "used_factor": 0.76,
            "network_tier": "db",
        },
        "linux-api": {
            "os": "Ubuntu Linux (64-bit)",
            "os_options": [
                "Ubuntu Linux (64-bit)",
                "Red Hat Enterprise Linux 8 (64-bit)",
            ],
            "tech": ["Nginx", "Node.js 18"],
            "target": "Azure Virtual Machines",
            "cpu_burst": True,
        },
        "linux-app": {
            "os": "Ubuntu Linux (64-bit)",
            "tech": ["Nginx", "Python 3.11"],
            "target": "Azure Virtual Machines",
        },
        "linux-etl": {
            "os": "Rocky Linux 9 (64-bit)",
            "tech": ["Apache Airflow", "Python 3.11"],
            "target": "Azure Virtual Machines",
            "cpu_burst": True,
            "storage_multiplier": 10,
        },
        "linux-ci": {
            "os": "CentOS 7 (64-bit)",
            "tech": ["Jenkins", "Docker"],
            "target": "Azure Virtual Machines",
        },
        "dotnet-app": {
            "os": "Microsoft Windows Server 2022 (64-bit)",
            "tech": ["IIS 10", ".NET 8"],
            "target": "Azure App Service candidate",
            "memory_burst": True,
        },
        "sap-web": {
            "os": "Microsoft Windows Server 2019 (64-bit)",
            "tech": ["SAP Web Dispatcher"],
            "target": "Azure VMware Solution",
        },
        "sap-app": {
            "os": "Red Hat Enterprise Linux 8 (64-bit)",
            "tech": ["SAP NetWeaver", "SAP Application Server"],
            "target": "Azure VMware Solution",
            "cpu_burst": True,
            "memory_burst": True,
            "network_tier": "app",
        },
        "sap-batch": {
            "os": "Red Hat Enterprise Linux 8 (64-bit)",
            "tech": ["SAP Batch Scheduler", "SAP Background Processing"],
            "target": "Azure VMware Solution",
            "cpu_burst": True,
            "network_tier": "app",
        },
        "hana-db": {
            "os": "SUSE Linux Enterprise Server 15 (64-bit)",
            "tech": ["SAP HANA 2.0"],
            "target": "Azure VMware Solution",
            "storage_multiplier": 20,
            "used_factor": 0.78,
            "network_tier": "db",
        },
        "citrix-controller": {
            "os": "Microsoft Windows Server 2019 (64-bit)",
            "tech": ["Citrix Delivery Controller", "Citrix Studio"],
            "target": "Azure VMware Solution",
            "network_tier": "app",
        },
        "citrix-storefront": {
            "os": "Microsoft Windows Server 2019 (64-bit)",
            "tech": ["Citrix StoreFront"],
            "target": "Azure VMware Solution",
            "network_tier": "app",
        },
        "citrix-license": {
            "os": "Microsoft Windows Server 2019 (64-bit)",
            "tech": ["Citrix License Server"],
            "target": "Azure VMware Solution",
            "network_tier": "app",
        },
        "citrix-worker": {
            "os": "Microsoft Windows Server 2019 (64-bit)",
            "os_options": [
                "Microsoft Windows Server 2019 (64-bit)",
                "Microsoft Windows Server 2022 (64-bit)",
            ],
            "tech": ["Citrix Virtual Delivery Agent"],
            "target": "Azure VMware Solution",
            "network_tier": "app",
        },
        "sql-ao-db": {
            "os": "Microsoft Windows Server 2022 (64-bit)",
            "tech": ["SQL Server 2022 Enterprise", "Always On Availability Groups"],
            "target": "Azure VMware Solution",
            "storage_multiplier": 16,
            "used_factor": 0.75,
            "network_tier": "db",
        },
        "sql-witness": {
            "os": "Microsoft Windows Server 2022 (64-bit)",
            "tech": ["Windows Server Failover Cluster Witness"],
            "target": "Azure Virtual Machines",
            "network_tier": "app",
        },
        "linux-compute": {
            "os": "Rocky Linux 9 (64-bit)",
            "tech": ["Nextflow", "Docker", "Python 3.11"],
            "target": "Azure Virtual Machines",
            "cpu_burst": True,
            "storage_multiplier": 12,
        },
    }

    hosts = []
    for idx in range(1, 9):
        hosts.append(
            {
                "host": f"esx-prod-{idx:02d}",
                "cluster": "cluster-prod-a" if idx <= 4 else "cluster-prod-b",
                "datacenter": "dc-primary",
                "cpu_model": "Intel Xeon Gold 6430",
                "speed": 2200,
                "socket_count": 2,
                "cores_per_socket": 32,
                "cpu_usage_pct": 48 + idx,
                "memory_mib_total": 786432,
                "memory_usage_pct": 58 + idx,
                "vm_used_memory_mib": 180000 + (idx * 12000),
                "nics": 8,
                "vcpus_allocated": 64 + (idx * 4),
                "vram_allocated_mib": 180224 + (idx * 4096),
                "esx_version": "8.0.2",
                "vendor": "Dell",
                "model": "PowerEdge R760",
                "object_id": f"host-prod-{idx:03d}",
                "uuid": f"host-prod-uuid-{idx:03d}",
            }
        )
    for idx in range(1, 5):
        hosts.append(
            {
                "host": f"esx-dev-{idx:02d}",
                "cluster": "cluster-dev-a",
                "datacenter": "dc-secondary",
                "cpu_model": "Intel Xeon Silver 4314",
                "speed": 2400,
                "socket_count": 2,
                "cores_per_socket": 16,
                "cpu_usage_pct": 22 + idx,
                "memory_mib_total": 262144,
                "memory_usage_pct": 35 + idx,
                "vm_used_memory_mib": 64000 + (idx * 4096),
                "nics": 4,
                "vcpus_allocated": 20 + (idx * 4),
                "vram_allocated_mib": 65536 + (idx * 2048),
                "esx_version": "7.0.3",
                "vendor": "HPE",
                "model": "ProLiant DL360",
                "object_id": f"host-dev-{idx:03d}",
                "uuid": f"host-dev-uuid-{idx:03d}",
            }
        )

    datastores = [
        {
            "name": "vsan-prod-a",
            "object_id": "ds-prod-101",
            "type": "vsan",
            "hosts": ";".join(h["host"] for h in hosts[:4]),
            "capacity_mib": 9437184,
            "provisioned_mib": 6029312,
            "in_use_mib": 4012032,
        },
        {
            "name": "vsan-prod-b",
            "object_id": "ds-prod-102",
            "type": "vsan",
            "hosts": ";".join(h["host"] for h in hosts[4:8]),
            "capacity_mib": 9437184,
            "provisioned_mib": 5775360,
            "in_use_mib": 3661824,
        },
        {
            "name": "vmfs-dev-a",
            "object_id": "ds-dev-201",
            "type": "vmfs",
            "hosts": ";".join(h["host"] for h in hosts[8:]),
            "capacity_mib": 2097152,
            "provisioned_mib": 851968,
            "in_use_mib": 524288,
        },
    ]

    networks = [
        {
            "object_id": "dvport-prod-120",
            "port": "1201",
            "switch": "dvSwitch-prod-web",
            "type": "distributed",
            "vlan": 120,
        },
        {
            "object_id": "dvport-prod-130",
            "port": "1301",
            "switch": "dvSwitch-prod-app",
            "type": "distributed",
            "vlan": 130,
        },
        {
            "object_id": "dvport-prod-140",
            "port": "1401",
            "switch": "dvSwitch-prod-db",
            "type": "distributed",
            "vlan": 140,
        },
        {
            "object_id": "dvport-dev-220",
            "port": "2201",
            "switch": "vSwitch-dev",
            "type": "standard",
            "vlan": 220,
        },
    ]

    return build_dataset_from_templates(
        app_templates,
        tech_profiles,
        hosts,
        datastores,
        networks,
        100,
        "enterprise",
    )


def build_healthcare_dataset():
    app_templates = [
        {
            "name": "epic-ehr-core",
            "tier_specs": [
                ("presentation", 4, 4, 16384, "windows-web"),
                ("app", 8, 10, 32768, "windows-app"),
                ("db", 4, 16, 65536, "sql-ao-db"),
            ],
            "criticality": "tier-1",
            "owner": "clinical-informatics",
            "compliance": "HIPAA",
            "pattern": "Conservative clinical rehost with staged Azure modernization",
            "notes": "Fictional pediatric research hospital core EHR footprint aligned to high-availability clinical operations.",
        },
        {
            "name": "patient-portal-dotnet",
            "tier_specs": [
                ("web", 4, 4, 12288, "windows-web"),
                ("app", 4, 8, 24576, "dotnet-app"),
                ("db", 2, 12, 49152, "sql-db"),
            ],
            "criticality": "tier-1",
            "owner": "digital-patient-experience",
            "compliance": "HIPAA",
            "pattern": "Three-tier .NET estate with rehost first and App Service later",
        },
        {
            "name": "revenue-cycle-sap",
            "tier_specs": [
                ("sapweb", 2, 4, 16384, "sap-web"),
                ("sapapp", 4, 12, 49152, "sap-app"),
                ("batch", 2, 8, 32768, "sap-batch"),
                ("db", 2, 20, 98304, "hana-db"),
            ],
            "criticality": "tier-1",
            "owner": "finance-and-revenue-cycle",
            "compliance": "SOX",
            "pattern": "SAP-led rehost for finance and supply workflows",
        },
        {
            "name": "claims-adjudication",
            "tier_specs": [
                ("web", 4, 4, 12288, "windows-web"),
                ("api", 4, 8, 16384, "linux-api"),
                ("db", 2, 12, 32768, "postgres-db"),
            ],
            "criticality": "tier-2",
            "owner": "payer-operations",
            "compliance": "HIPAA",
            "pattern": "Azure VM and managed database mix for payer workloads",
        },
        {
            "name": "citrix-clinical-desktops",
            "tier_specs": [
                ("controller", 2, 6, 16384, "citrix-controller"),
                ("storefront", 2, 4, 12288, "citrix-storefront"),
                ("worker", 16, 4, 16384, "citrix-worker"),
                ("db", 2, 8, 32768, "sql-db"),
            ],
            "criticality": "tier-1",
            "owner": "clinical-end-user-compute",
            "compliance": "HIPAA",
            "pattern": "Short-term Citrix retention while Azure Virtual Desktop strategy is validated",
        },
        {
            "name": "research-genomics-pipeline",
            "tier_specs": [
                ("etl", 4, 8, 32768, "linux-etl"),
                ("compute", 8, 12, 49152, "linux-compute"),
                ("db", 2, 16, 65536, "postgres-db"),
            ],
            "criticality": "tier-2",
            "owner": "translational-research",
            "compliance": "research-data",
            "pattern": "Research compute rehost with future HPC and data platform modernization",
        },
        {
            "name": "pacs-imaging",
            "tier_specs": [
                ("web", 2, 4, 12288, "windows-web"),
                ("app", 4, 8, 24576, "windows-app"),
                ("db", 2, 12, 49152, "sql-db"),
            ],
            "criticality": "tier-1",
            "owner": "radiology-platform",
            "compliance": "HIPAA",
            "pattern": "Low-disruption imaging migration with network and archive dependency review",
        },
        {
            "name": "lab-information-system",
            "tier_specs": [
                ("app", 4, 6, 16384, "windows-app"),
                ("db", 2, 8, 32768, "sql-db"),
            ],
            "criticality": "tier-1",
            "owner": "laboratory-services",
            "compliance": "HIPAA",
            "pattern": "Rehost first due to analyzer and interface dependencies",
        },
        {
            "name": "pharmacy-management",
            "tier_specs": [
                ("app", 4, 6, 16384, "windows-app"),
                ("db", 2, 8, 32768, "sql-db"),
            ],
            "criticality": "tier-1",
            "owner": "pharmacy-operations",
            "compliance": "HIPAA",
            "pattern": "Clinical support system with conservative initial placement",
        },
        {
            "name": "provider-directory",
            "tier_specs": [
                ("web", 2, 4, 12288, "windows-web"),
                ("app", 2, 6, 16384, "dotnet-app"),
                ("db", 1, 8, 32768, "sql-db"),
            ],
            "criticality": "tier-2",
            "owner": "network-management",
            "compliance": "PII",
            "pattern": "Three-tier .NET provider portal",
        },
        {
            "name": "integration-engine",
            "tier_specs": [
                ("broker", 4, 6, 12288, "linux-app"),
                ("api", 4, 6, 12288, "linux-api"),
            ],
            "criticality": "tier-1",
            "owner": "interop-platform",
            "compliance": "HIPAA",
            "pattern": "Interface engine estate with later container review",
        },
        {
            "name": "identity-and-access",
            "tier_specs": [
                ("idm", 4, 4, 16384, "windows-app"),
                ("db", 2, 8, 32768, "sql-db"),
            ],
            "criticality": "tier-1",
            "owner": "cybersecurity",
            "compliance": "internal",
            "pattern": "Conservative AVS-first identity estate",
        },
    ]

    tech_profiles = {
        "windows-web": {
            "os": "Microsoft Windows Server 2022 (64-bit)",
            "os_options": [
                "Microsoft Windows Server 2019 (64-bit)",
                "Microsoft Windows Server 2022 (64-bit)",
            ],
            "tech": ["IIS 10", ".NET Framework 4.8"],
            "target": "Azure VMware Solution",
            "memory_burst": True,
        },
        "windows-app": {
            "os": "Microsoft Windows Server 2022 (64-bit)",
            "os_options": [
                "Microsoft Windows Server 2019 (64-bit)",
                "Microsoft Windows Server 2022 (64-bit)",
            ],
            "tech": ["Windows Service", ".NET 6"],
            "target": "Azure Virtual Machines",
            "memory_burst": True,
        },
        "dotnet-app": {
            "os": "Microsoft Windows Server 2022 (64-bit)",
            "tech": ["IIS 10", ".NET 8"],
            "target": "Azure App Service candidate",
            "memory_burst": True,
        },
        "sql-db": {
            "os": "Microsoft Windows Server 2022 (64-bit)",
            "tech": ["SQL Server 2022", "SSRS"],
            "target": "Azure SQL Managed Instance candidate",
            "storage_multiplier": 16,
            "used_factor": 0.74,
            "network_tier": "db",
        },
        "sql-ao-db": {
            "os": "Microsoft Windows Server 2022 (64-bit)",
            "tech": ["SQL Server 2022 Enterprise", "Always On Availability Groups"],
            "target": "Azure VMware Solution",
            "storage_multiplier": 16,
            "used_factor": 0.75,
            "network_tier": "db",
        },
        "linux-api": {
            "os": "Red Hat Enterprise Linux 8 (64-bit)",
            "os_options": [
                "Ubuntu Linux (64-bit)",
                "Red Hat Enterprise Linux 8 (64-bit)",
            ],
            "tech": ["Nginx", "Node.js 18"],
            "target": "Azure Virtual Machines",
            "cpu_burst": True,
        },
        "linux-app": {
            "os": "Red Hat Enterprise Linux 8 (64-bit)",
            "tech": ["Mirth Connect", "Python 3.11"],
            "target": "Azure Virtual Machines",
        },
        "postgres-db": {
            "os": "Ubuntu Linux (64-bit)",
            "tech": ["PostgreSQL 14", "Patroni"],
            "target": "Azure Database for PostgreSQL candidate",
            "storage_multiplier": 14,
            "used_factor": 0.67,
            "network_tier": "db",
        },
        "linux-etl": {
            "os": "Rocky Linux 9 (64-bit)",
            "tech": ["Apache Airflow", "Python 3.11"],
            "target": "Azure Virtual Machines",
            "cpu_burst": True,
            "storage_multiplier": 10,
        },
        "linux-compute": {
            "os": "Rocky Linux 9 (64-bit)",
            "tech": ["Nextflow", "Docker", "Python 3.11"],
            "target": "Azure Virtual Machines",
            "cpu_burst": True,
            "storage_multiplier": 12,
        },
        "sap-web": {
            "os": "Microsoft Windows Server 2019 (64-bit)",
            "tech": ["SAP Web Dispatcher"],
            "target": "Azure VMware Solution",
        },
        "sap-app": {
            "os": "Red Hat Enterprise Linux 8 (64-bit)",
            "tech": ["SAP NetWeaver", "SAP Application Server"],
            "target": "Azure VMware Solution",
            "cpu_burst": True,
            "memory_burst": True,
            "network_tier": "app",
        },
        "sap-batch": {
            "os": "Red Hat Enterprise Linux 8 (64-bit)",
            "tech": ["SAP Batch Scheduler"],
            "target": "Azure VMware Solution",
            "cpu_burst": True,
            "network_tier": "app",
        },
        "hana-db": {
            "os": "SUSE Linux Enterprise Server 15 (64-bit)",
            "tech": ["SAP HANA 2.0"],
            "target": "Azure VMware Solution",
            "storage_multiplier": 20,
            "used_factor": 0.78,
            "network_tier": "db",
        },
        "citrix-controller": {
            "os": "Microsoft Windows Server 2019 (64-bit)",
            "tech": ["Citrix Delivery Controller"],
            "target": "Azure VMware Solution",
            "network_tier": "app",
        },
        "citrix-storefront": {
            "os": "Microsoft Windows Server 2019 (64-bit)",
            "tech": ["Citrix StoreFront"],
            "target": "Azure VMware Solution",
            "network_tier": "app",
        },
        "citrix-worker": {
            "os": "Microsoft Windows Server 2022 (64-bit)",
            "os_options": [
                "Microsoft Windows Server 2019 (64-bit)",
                "Microsoft Windows Server 2022 (64-bit)",
            ],
            "tech": ["Citrix Virtual Delivery Agent"],
            "target": "Azure VMware Solution",
            "network_tier": "app",
        },
    }

    hosts = []
    for idx in range(1, 11):
        hosts.append(
            {
                "host": f"esx-clinical-{idx:02d}",
                "cluster": "cluster-clinical-a" if idx <= 5 else "cluster-clinical-b",
                "datacenter": "dc-primary",
                "cpu_model": "Intel Xeon Gold 6430",
                "speed": 2200,
                "socket_count": 2,
                "cores_per_socket": 32,
                "cpu_usage_pct": 46 + idx,
                "memory_mib_total": 786432,
                "memory_usage_pct": 55 + idx,
                "vm_used_memory_mib": 192000 + (idx * 10240),
                "nics": 8,
                "vcpus_allocated": 68 + (idx * 4),
                "vram_allocated_mib": 196608 + (idx * 4096),
                "esx_version": "8.0.2",
                "vendor": "Dell",
                "model": "PowerEdge R760",
                "object_id": f"host-clinical-{idx:03d}",
                "uuid": f"host-clinical-uuid-{idx:03d}",
            }
        )
    for idx in range(1, 5):
        hosts.append(
            {
                "host": f"esx-research-{idx:02d}",
                "cluster": "cluster-research-a",
                "datacenter": "dc-secondary",
                "cpu_model": "Intel Xeon Platinum 8468",
                "speed": 2400,
                "socket_count": 2,
                "cores_per_socket": 32,
                "cpu_usage_pct": 35 + idx,
                "memory_mib_total": 1048576,
                "memory_usage_pct": 48 + idx,
                "vm_used_memory_mib": 256000 + (idx * 8192),
                "nics": 8,
                "vcpus_allocated": 72 + (idx * 4),
                "vram_allocated_mib": 262144 + (idx * 4096),
                "esx_version": "8.0.2",
                "vendor": "HPE",
                "model": "ProLiant DL385",
                "object_id": f"host-research-{idx:03d}",
                "uuid": f"host-research-uuid-{idx:03d}",
            }
        )

    datastores = [
        {
            "name": "vsan-clinical-a",
            "object_id": "ds-clinical-101",
            "type": "vsan",
            "hosts": ";".join(h["host"] for h in hosts[:5]),
            "capacity_mib": 9437184,
            "provisioned_mib": 6225920,
            "in_use_mib": 4300800,
        },
        {
            "name": "vsan-clinical-b",
            "object_id": "ds-clinical-102",
            "type": "vsan",
            "hosts": ";".join(h["host"] for h in hosts[5:10]),
            "capacity_mib": 9437184,
            "provisioned_mib": 5767168,
            "in_use_mib": 3899392,
        },
        {
            "name": "vsan-research-a",
            "object_id": "ds-research-201",
            "type": "vsan",
            "hosts": ";".join(h["host"] for h in hosts[10:]),
            "capacity_mib": 6291456,
            "provisioned_mib": 3407872,
            "in_use_mib": 2097152,
        },
    ]

    networks = [
        {
            "object_id": "dvport-clinical-120",
            "port": "1201",
            "switch": "dvSwitch-prod-web",
            "type": "distributed",
            "vlan": 120,
        },
        {
            "object_id": "dvport-clinical-130",
            "port": "1301",
            "switch": "dvSwitch-prod-app",
            "type": "distributed",
            "vlan": 130,
        },
        {
            "object_id": "dvport-clinical-140",
            "port": "1401",
            "switch": "dvSwitch-prod-db",
            "type": "distributed",
            "vlan": 140,
        },
        {
            "object_id": "dvport-research-220",
            "port": "2201",
            "switch": "vSwitch-dev",
            "type": "standard",
            "vlan": 220,
        },
    ]

    return build_dataset_from_templates(
        app_templates,
        tech_profiles,
        hosts,
        datastores,
        networks,
        5000,
        "healthcare",
    )


def build_placement_dataset():
    hosts = base_hosts_small()
    datastores = base_datastores_small()
    networks = base_networks_small()
    vms = small_vms()
    snapshots = small_snapshots(vms)
    placement_rows = [
        [
            "contoso-commerce",
            "tier-1",
            "AVS",
            "Uses Windows + Tomcat app tiers and low-change requirement; fastest datacenter exit path.",
            "Database later candidate for Azure SQL Managed Instance",
            "wave-1",
        ],
        [
            "order-api",
            "tier-2",
            "Azure VMs",
            "Linux API workload with moderate change tolerance and straightforward rehost.",
            "Evaluate App Service or AKS after stabilization",
            "wave-2",
        ],
        [
            "finance-reporting",
            "tier-2",
            "AVS or Azure VMs",
            "Reporting stack may stay close to current topology initially due to SQL/SSRS coupling.",
            "Assess SQL modernization after dependency validation",
            "wave-3",
        ],
        [
            "devops-shared",
            "tier-3",
            "Azure VMs or PaaS replacement",
            "Good pilot candidate with lower business risk.",
            "Potential Jenkins replacement / PaaS refactor",
            "wave-1",
        ],
        [
            "shared-platform",
            "tier-2",
            "Azure Virtual Machines",
            "Management server fits native IaaS more naturally than AVS.",
            "No immediate modernization dependency",
            "wave-0",
        ],
    ]
    notes = {
        "decision_factors": [
            "operational symmetry required",
            "business downtime tolerance",
            "database modernization potential",
            "supportability and licensing",
            "cloud-native refactor readiness",
        ],
        "interpretation": "This planning sample is not an Azure Migrate import schema. It complements RVTools-style import data for portfolio decisions.",
    }
    return {
        "vms": vms,
        "hosts": hosts,
        "datastores": datastores,
        "networks": networks,
        "snapshots": snapshots,
        "placement_rows": placement_rows,
        "notes": notes,
    }


def write_csv(path: Path, headers: list[str], rows: list[list]):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def write_json(path: Path, payload):
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def main():
    small_hosts = base_hosts_small()
    small_datastores = base_datastores_small()
    small_networks = base_networks_small()
    small_vm_list = small_vms()
    build_rvtools_workbook(
        STRICT_WORKBOOK,
        small_vm_list,
        small_hosts,
        small_datastores,
        small_networks,
        small_snapshots(small_vm_list),
    )

    enterprise = build_enterprise_dataset()
    build_rvtools_workbook(
        ENTERPRISE_WORKBOOK,
        enterprise["vms"],
        enterprise["hosts"],
        enterprise["datastores"],
        enterprise["networks"],
        enterprise["snapshots"],
    )
    write_json(
        ENTERPRISE_APP_JSON,
        {
            "applications": enterprise["applications"],
            "vm_count": len(enterprise["vms"]),
        },
    )
    write_csv(
        ENTERPRISE_DEP_CSV,
        ["source", "target", "protocol", "port", "interaction_type", "criticality"],
        enterprise["dependencies"],
    )
    write_csv(
        ENTERPRISE_TECH_CSV,
        [
            "vm",
            "application_name",
            "tier",
            "criticality",
            "owner",
            "technologies",
            "suggested_target",
            "migration_wave",
        ],
        enterprise["technology_rows"],
    )
    write_csv(
        ENTERPRISE_GROUPS_CSV,
        [
            "application_name",
            "environment",
            "criticality",
            "owner",
            "vm_count",
            "target_pattern",
        ],
        enterprise["groups"],
    )

    healthcare = build_healthcare_dataset()
    build_rvtools_workbook(
        HEALTHCARE_WORKBOOK,
        healthcare["vms"],
        healthcare["hosts"],
        healthcare["datastores"],
        healthcare["networks"],
        healthcare["snapshots"],
    )
    write_json(
        HEALTHCARE_APP_JSON,
        {
            "organization_profile": {
                "scenario_name": "NorthStar Children's Health",
                "industry": "healthcare payor-provider with pediatric research hospital characteristics",
                "notes": "Fictional sample modeled after a major pediatric research and care delivery organization; not an Azure Migrate native schema.",
            },
            "applications": healthcare["applications"],
            "vm_count": len(healthcare["vms"]),
        },
    )
    write_csv(
        HEALTHCARE_DEP_CSV,
        ["source", "target", "protocol", "port", "interaction_type", "criticality"],
        healthcare["dependencies"],
    )
    write_csv(
        HEALTHCARE_TECH_CSV,
        [
            "vm",
            "application_name",
            "tier",
            "criticality",
            "owner",
            "technologies",
            "suggested_target",
            "migration_wave",
        ],
        healthcare["technology_rows"],
    )
    write_csv(
        HEALTHCARE_GROUPS_CSV,
        [
            "application_name",
            "environment",
            "criticality",
            "owner",
            "vm_count",
            "target_pattern",
        ],
        healthcare["groups"],
    )

    placement = build_placement_dataset()
    build_rvtools_workbook(
        PLACEMENT_WORKBOOK,
        placement["vms"],
        placement["hosts"],
        placement["datastores"],
        placement["networks"],
        placement["snapshots"],
    )
    write_csv(
        PLACEMENT_MATRIX_CSV,
        [
            "application_name",
            "business_criticality",
            "recommended_initial_target",
            "rationale",
            "modernization_follow_on",
            "suggested_wave",
        ],
        placement["placement_rows"],
    )
    write_json(PLACEMENT_NOTES_JSON, placement["notes"])

    for path in [
        STRICT_WORKBOOK,
        ENTERPRISE_WORKBOOK,
        ENTERPRISE_APP_JSON,
        ENTERPRISE_DEP_CSV,
        ENTERPRISE_TECH_CSV,
        ENTERPRISE_GROUPS_CSV,
        HEALTHCARE_WORKBOOK,
        HEALTHCARE_APP_JSON,
        HEALTHCARE_DEP_CSV,
        HEALTHCARE_TECH_CSV,
        HEALTHCARE_GROUPS_CSV,
        PLACEMENT_WORKBOOK,
        PLACEMENT_MATRIX_CSV,
        PLACEMENT_NOTES_JSON,
    ]:
        print(f"Created {path}")


if __name__ == "__main__":
    main()
