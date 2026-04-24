param(
    [Alias('InputFile')]
    [string]$SourcePath = "c:\Users\gpillai\source\repos\arcjumpstart\azure_arc_vsphere_jumpstart\azure_migrate_samples\Encompass-20260416 XenApp RVTools_export.xlsx",
    [string]$TemplatePath = "c:\Users\gpillai\source\repos\arcjumpstart\azure_arc_vsphere_jumpstart\azure_migrate_samples\azure_migrate_vmware_rvtools_strict_sample.xlsx",
    [string]$OutputPath = "c:\Users\gpillai\source\repos\arcjumpstart\azure_arc_vsphere_jumpstart\azure_migrate_samples\Encompass-20260416 XenApp RVTools_export_azure_migrate_fixed.xlsx"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-HeaderMap {
    param($Worksheet)

    $used = $Worksheet.UsedRange
    $map = @{}
    for ($column = 1; $column -le $used.Columns.Count; $column++) {
        $header = [string]$used.Cells.Item(1, $column).Text
        if (-not [string]::IsNullOrWhiteSpace($header)) {
            $map[$header] = $column
        }
    }
    return $map
}

function Get-CellText {
    param($Worksheet, $HeaderMap, [int]$Row, [string]$Header)

    if (-not $HeaderMap.ContainsKey($Header)) {
        return ''
    }
    return [string]$Worksheet.UsedRange.Cells.Item($Row, $HeaderMap[$Header]).Text
}

function Get-CellTextAny {
    param($Worksheet, $HeaderMap, [int]$Row, [string[]]$Headers)

    foreach ($header in $Headers) {
        $value = Get-CellText -Worksheet $Worksheet -HeaderMap $HeaderMap -Row $Row -Header $header
        if (-not [string]::IsNullOrWhiteSpace($value)) {
            return $value
        }
    }
    return ''
}

function New-DeterministicGuid {
    param([string]$Seed)

    $normalized = [Text.Encoding]::UTF8.GetBytes($Seed)
    $hash = [System.Security.Cryptography.MD5]::Create().ComputeHash($normalized)
    return [Guid]::New($hash).Guid
}

function Clear-SheetData {
    param($Worksheet)

    $used = $Worksheet.UsedRange
    while ($used.Rows.Count -gt 1) {
        $Worksheet.Rows.Item(2).Delete()
        $used = $Worksheet.UsedRange
    }
}

function Write-Row {
    param($Worksheet, [int]$RowIndex, [object[]]$Values)

    for ($column = 0; $column -lt $Values.Count; $column++) {
        $Worksheet.Cells.Item($RowIndex, $column + 1) = $Values[$column]
    }
}

if (-not (Test-Path $SourcePath)) {
    throw "Source workbook not found: $SourcePath"
}
if (-not (Test-Path $TemplatePath)) {
    throw "Template workbook not found: $TemplatePath"
}

if (Test-Path $OutputPath) {
    Remove-Item -LiteralPath $OutputPath -Force
}
Copy-Item -LiteralPath $TemplatePath -Destination $OutputPath -Force

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

try {
    $sourceWorkbook = $excel.Workbooks.Open((Resolve-Path $SourcePath).Path, 0, $true)
    $outputWorkbook = $excel.Workbooks.Open((Resolve-Path $OutputPath).Path)

    try {
        $writtenCounts = @{}
        $partitionFallbackRows = @()
        $sourceSheets = @{}
        foreach ($worksheet in $sourceWorkbook.Worksheets) {
            $sourceSheets[$worksheet.Name] = $worksheet
        }

        $templateSheets = @{}
        foreach ($worksheet in $outputWorkbook.Worksheets) {
            $templateSheets[$worksheet.Name] = $worksheet
            Clear-SheetData -Worksheet $worksheet
            $writtenCounts[$worksheet.Name] = 0
        }

        $vInfoSheet = $sourceSheets['vInfo']
        $vInfoHeaders = Get-HeaderMap -Worksheet $vInfoSheet
        $vMemorySheet = $sourceSheets['vMemory']
        $vMemoryHeaders = Get-HeaderMap -Worksheet $vMemorySheet

        $vmUuidById = @{}
        for ($row = 2; $row -le $vMemorySheet.UsedRange.Rows.Count; $row++) {
            $vmId = Get-CellText -Worksheet $vMemorySheet -HeaderMap $vMemoryHeaders -Row $row -Header 'VM ID'
            $vmUuid = Get-CellText -Worksheet $vMemorySheet -HeaderMap $vMemoryHeaders -Row $row -Header 'VM UUID'
            if (-not [string]::IsNullOrWhiteSpace($vmId)) {
                $vmUuidById[$vmId] = $vmUuid
            }
        }

        $vInfoTarget = $templateSheets['vInfo']
        $targetRow = 2
        for ($row = 2; $row -le $vInfoSheet.UsedRange.Rows.Count; $row++) {
            $vmId = Get-CellText -Worksheet $vInfoSheet -HeaderMap $vInfoHeaders -Row $row -Header 'VM ID'
            if ([string]::IsNullOrWhiteSpace($vmId)) {
                continue
            }

            $vmName = Get-CellText -Worksheet $vInfoSheet -HeaderMap $vInfoHeaders -Row $row -Header 'VM'
            if ([string]::IsNullOrWhiteSpace($vmName)) {
                $vmName = $vmId
            }

            $vmUuid = ''
            if ($vmUuidById.ContainsKey($vmId)) {
                $vmUuid = $vmUuidById[$vmId]
            }
            if ([string]::IsNullOrWhiteSpace($vmUuid)) {
                $vmUuid = New-DeterministicGuid -Seed ($vmId + '|' + (Get-CellText -Worksheet $vInfoSheet -HeaderMap $vInfoHeaders -Row $row -Header 'VI SDK UUID'))
            }

            Write-Row -Worksheet $vInfoTarget -RowIndex $targetRow -Values @(
                $vmName,
                $vmUuid,
                (Get-CellText -Worksheet $vInfoSheet -HeaderMap $vInfoHeaders -Row $row -Header 'Powerstate'),
                (Get-CellText -Worksheet $vInfoSheet -HeaderMap $vInfoHeaders -Row $row -Header 'CPUs'),
                (Get-CellText -Worksheet $vInfoSheet -HeaderMap $vInfoHeaders -Row $row -Header 'Memory'),
                (Get-CellText -Worksheet $vInfoSheet -HeaderMap $vInfoHeaders -Row $row -Header 'Provisioned MiB'),
                (Get-CellText -Worksheet $vInfoSheet -HeaderMap $vInfoHeaders -Row $row -Header 'In Use MiB'),
                (Get-CellText -Worksheet $vInfoSheet -HeaderMap $vInfoHeaders -Row $row -Header 'OS according to the configuration file')
            )

            $partitionFallbackRows += , @(
                $vmName,
                $vmUuid,
                (Get-CellText -Worksheet $vInfoSheet -HeaderMap $vInfoHeaders -Row $row -Header 'Provisioned MiB'),
                (Get-CellText -Worksheet $vInfoSheet -HeaderMap $vInfoHeaders -Row $row -Header 'In Use MiB')
            )
            $targetRow++
        }
        $writtenCounts['vInfo'] = $targetRow - 2

        $vHostSource = $sourceSheets['vHost']
        $vHostHeaders = Get-HeaderMap -Worksheet $vHostSource
        $vHostTarget = $templateSheets['vHost']
        $targetRow = 2
        for ($row = 2; $row -le $vHostSource.UsedRange.Rows.Count; $row++) {
            $hostId = ('host-{0:D3}' -f ($row - 1))
            Write-Row -Worksheet $vHostTarget -RowIndex $targetRow -Values @(
                $hostId,
                (Get-CellText -Worksheet $vHostSource -HeaderMap $vHostHeaders -Row $row -Header 'Cluster'),
                (Get-CellText -Worksheet $vHostSource -HeaderMap $vHostHeaders -Row $row -Header 'Datacenter'),
                (Get-CellText -Worksheet $vHostSource -HeaderMap $vHostHeaders -Row $row -Header 'Config status'),
                (Get-CellText -Worksheet $vHostSource -HeaderMap $vHostHeaders -Row $row -Header 'in Maintenance Mode'),
                (Get-CellText -Worksheet $vHostSource -HeaderMap $vHostHeaders -Row $row -Header 'in Quarantine Mode'),
                (Get-CellText -Worksheet $vHostSource -HeaderMap $vHostHeaders -Row $row -Header 'CPU Model'),
                (Get-CellText -Worksheet $vHostSource -HeaderMap $vHostHeaders -Row $row -Header 'Speed'),
                (Get-CellText -Worksheet $vHostSource -HeaderMap $vHostHeaders -Row $row -Header '# CPU'),
                (Get-CellText -Worksheet $vHostSource -HeaderMap $vHostHeaders -Row $row -Header 'Cores per CPU'),
                (Get-CellText -Worksheet $vHostSource -HeaderMap $vHostHeaders -Row $row -Header '# Cores'),
                (Get-CellText -Worksheet $vHostSource -HeaderMap $vHostHeaders -Row $row -Header 'CPU usage %'),
                (Get-CellText -Worksheet $vHostSource -HeaderMap $vHostHeaders -Row $row -Header '# Memory'),
                (Get-CellText -Worksheet $vHostSource -HeaderMap $vHostHeaders -Row $row -Header 'Memory usage %'),
                (Get-CellText -Worksheet $vHostSource -HeaderMap $vHostHeaders -Row $row -Header 'VM Used memory'),
                (Get-CellText -Worksheet $vHostSource -HeaderMap $vHostHeaders -Row $row -Header 'VM Memory Swapped'),
                (Get-CellText -Worksheet $vHostSource -HeaderMap $vHostHeaders -Row $row -Header 'VM Memory Ballooned'),
                (Get-CellText -Worksheet $vHostSource -HeaderMap $vHostHeaders -Row $row -Header '# NICs'),
                (Get-CellText -Worksheet $vHostSource -HeaderMap $vHostHeaders -Row $row -Header '# vCPUs'),
                (Get-CellText -Worksheet $vHostSource -HeaderMap $vHostHeaders -Row $row -Header 'vRAM'),
                (Get-CellText -Worksheet $vHostSource -HeaderMap $vHostHeaders -Row $row -Header 'ESX Version'),
                (Get-CellText -Worksheet $vHostSource -HeaderMap $vHostHeaders -Row $row -Header 'Vendor'),
                (Get-CellText -Worksheet $vHostSource -HeaderMap $vHostHeaders -Row $row -Header 'Model'),
                $hostId,
                (New-DeterministicGuid -Seed $hostId)
            )
            $targetRow++
        }
        $writtenCounts['vHost'] = $targetRow - 2

        $vDatastoreSource = $sourceSheets['vDatastore']
        $vDatastoreHeaders = Get-HeaderMap -Worksheet $vDatastoreSource
        $vDatastoreTarget = $templateSheets['vDatastore']
        $targetRow = 2
        for ($row = 2; $row -le $vDatastoreSource.UsedRange.Rows.Count; $row++) {
            $datastoreId = ('datastore-{0:D3}' -f ($row - 1))
            Write-Row -Worksheet $vDatastoreTarget -RowIndex $targetRow -Values @(
                $datastoreId,
                $datastoreId,
                (Get-CellText -Worksheet $vDatastoreSource -HeaderMap $vDatastoreHeaders -Row $row -Header 'Type'),
                (Get-CellText -Worksheet $vDatastoreSource -HeaderMap $vDatastoreHeaders -Row $row -Header '# Hosts'),
                (Get-CellText -Worksheet $vDatastoreSource -HeaderMap $vDatastoreHeaders -Row $row -Header 'Capacity MiB'),
                (Get-CellText -Worksheet $vDatastoreSource -HeaderMap $vDatastoreHeaders -Row $row -Header 'Provisioned MiB'),
                (Get-CellText -Worksheet $vDatastoreSource -HeaderMap $vDatastoreHeaders -Row $row -Header 'In Use MiB')
            )
            $targetRow++
        }
        $writtenCounts['vDatastore'] = $targetRow - 2

        $vPartitionSource = $sourceSheets['vPartition']
        $vPartitionHeaders = Get-HeaderMap -Worksheet $vPartitionSource
        $vPartitionTarget = $templateSheets['vPartition']
        $targetRow = 2
        for ($row = 2; $row -le $vPartitionSource.UsedRange.Rows.Count; $row++) {
            $vmId = Get-CellTextAny -Worksheet $vPartitionSource -HeaderMap $vPartitionHeaders -Row $row -Headers @('VM ID', 'VM')
            if ([string]::IsNullOrWhiteSpace($vmId)) {
                continue
            }

            $vmUuid = Get-CellTextAny -Worksheet $vPartitionSource -HeaderMap $vPartitionHeaders -Row $row -Headers @('VM UUID')
            if ([string]::IsNullOrWhiteSpace($vmUuid) -and $vmUuidById.ContainsKey($vmId)) {
                $vmUuid = $vmUuidById[$vmId]
            }
            if ([string]::IsNullOrWhiteSpace($vmUuid)) {
                $vmUuid = New-DeterministicGuid -Seed ($vmId + '|partition')
            }

            $capacity = Get-CellTextAny -Worksheet $vPartitionSource -HeaderMap $vPartitionHeaders -Row $row -Headers @('Capacity MiB', 'Capacity MB')
            $consumed = Get-CellTextAny -Worksheet $vPartitionSource -HeaderMap $vPartitionHeaders -Row $row -Headers @('Consumed MiB', 'Consumed MB')
            if ([string]::IsNullOrWhiteSpace($consumed)) {
                $free = Get-CellTextAny -Worksheet $vPartitionSource -HeaderMap $vPartitionHeaders -Row $row -Headers @('Free MiB', 'Free MB')
                [double]$capacityValue = 0
                [double]$freeValue = 0
                if ([double]::TryParse($capacity, [ref]$capacityValue) -and [double]::TryParse($free, [ref]$freeValue)) {
                    $consumed = [string]([math]::Max([math]::Round($capacityValue - $freeValue), 0))
                }
            }

            if ([string]::IsNullOrWhiteSpace($capacity) -or [string]::IsNullOrWhiteSpace($consumed)) {
                continue
            }

            Write-Row -Worksheet $vPartitionTarget -RowIndex $targetRow -Values @(
                $vmId,
                $vmUuid,
                $capacity,
                $consumed
            )
            $targetRow++
        }

        if ($targetRow -eq 2) {
            foreach ($values in $partitionFallbackRows) {
                if ([string]::IsNullOrWhiteSpace([string]$values[2]) -or [string]::IsNullOrWhiteSpace([string]$values[3])) {
                    continue
                }
                Write-Row -Worksheet $vPartitionTarget -RowIndex $targetRow -Values $values
                $targetRow++
            }
        }
        $writtenCounts['vPartition'] = $targetRow - 2

        $vMemoryTarget = $templateSheets['vMemory']
        $targetRow = 2
        for ($row = 2; $row -le $vMemorySheet.UsedRange.Rows.Count; $row++) {
            $vmId = Get-CellText -Worksheet $vMemorySheet -HeaderMap $vMemoryHeaders -Row $row -Header 'VM ID'
            if ([string]::IsNullOrWhiteSpace($vmId)) {
                continue
            }
            $vmUuid = Get-CellText -Worksheet $vMemorySheet -HeaderMap $vMemoryHeaders -Row $row -Header 'VM UUID'
            if ([string]::IsNullOrWhiteSpace($vmUuid)) {
                $vmUuid = New-DeterministicGuid -Seed $vmId
            }
            Write-Row -Worksheet $vMemoryTarget -RowIndex $targetRow -Values @(
                $vmId,
                $vmUuid,
                (Get-CellText -Worksheet $vMemorySheet -HeaderMap $vMemoryHeaders -Row $row -Header 'Size MiB'),
                (Get-CellText -Worksheet $vMemorySheet -HeaderMap $vMemoryHeaders -Row $row -Header 'Reservation')
            )
            $targetRow++
        }
        $writtenCounts['vMemory'] = $targetRow - 2

        $vUSBSource = $sourceSheets['vUSB']
        $vUSBHeaders = Get-HeaderMap -Worksheet $vUSBSource
        $vUSBTarget = $templateSheets['vUSB']
        $targetRow = 2
        for ($row = 2; $row -le $vUSBSource.UsedRange.Rows.Count; $row++) {
            $vmName = Get-CellText -Worksheet $vUSBSource -HeaderMap $vUSBHeaders -Row $row -Header 'VM'
            if ([string]::IsNullOrWhiteSpace($vmName)) {
                continue
            }
            Write-Row -Worksheet $vUSBTarget -RowIndex $targetRow -Values @(
                $vmName,
                (Get-CellText -Worksheet $vUSBSource -HeaderMap $vUSBHeaders -Row $row -Header 'VM UUID'),
                (Get-CellText -Worksheet $vUSBSource -HeaderMap $vUSBHeaders -Row $row -Header 'Powerstate'),
                (Get-CellText -Worksheet $vUSBSource -HeaderMap $vUSBHeaders -Row $row -Header 'Device Type'),
                (Get-CellText -Worksheet $vUSBSource -HeaderMap $vUSBHeaders -Row $row -Header 'Connected')
            )
            $targetRow++
        }
        $writtenCounts['vUSB'] = $targetRow - 2

        $dvPortSource = $sourceSheets['dvPort']
        $dvPortHeaders = Get-HeaderMap -Worksheet $dvPortSource
        $dvPortTarget = $templateSheets['dvPort']
        $targetRow = 2
        for ($row = 2; $row -le $dvPortSource.UsedRange.Rows.Count; $row++) {
            Write-Row -Worksheet $dvPortTarget -RowIndex $targetRow -Values @(
                (Get-CellText -Worksheet $dvPortSource -HeaderMap $dvPortHeaders -Row $row -Header 'Object ID'),
                ($row - 1),
                (Get-CellText -Worksheet $dvPortSource -HeaderMap $dvPortHeaders -Row $row -Header 'Switch'),
                (Get-CellText -Worksheet $dvPortSource -HeaderMap $dvPortHeaders -Row $row -Header 'Type'),
                (Get-CellText -Worksheet $dvPortSource -HeaderMap $dvPortHeaders -Row $row -Header 'VLAN'),
                (Get-CellText -Worksheet $dvPortSource -HeaderMap $dvPortHeaders -Row $row -Header 'Allow Promiscuous'),
                (Get-CellText -Worksheet $dvPortSource -HeaderMap $dvPortHeaders -Row $row -Header 'Mac Changes'),
                (Get-CellText -Worksheet $dvPortSource -HeaderMap $dvPortHeaders -Row $row -Header 'Forged Transmits')
            )
            $targetRow++
        }
        $writtenCounts['dvPort'] = $targetRow - 2

        $outputWorkbook.Save()
        Write-Host "Wrote repaired workbook: $OutputPath"
        foreach ($sheetName in 'vInfo', 'vHost', 'vDatastore', 'vMemory', 'vUSB', 'dvPort') {
            Write-Host ($sheetName + ' rows written: ' + $writtenCounts[$sheetName])
        }
        foreach ($sheetName in 'vSnapshot', 'vPartition', 'vDisk', 'vCD', 'vNetwork') {
            Write-Host ($sheetName + ' rows written: ' + $writtenCounts[$sheetName])
        }
    }
    finally {
        $outputWorkbook.Close($true) | Out-Null
        $sourceWorkbook.Close($false) | Out-Null
    }
}
finally {
    $excel.Quit()
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel)
}