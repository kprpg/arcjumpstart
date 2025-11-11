[CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='Medium')]
param(
    [Parameter(Mandatory=$true, HelpMessage='Subscription ID to operate on')]
    [string]$SubscriptionId,

    [Parameter(Mandatory=$false, HelpMessage='Substring filter: matches RG names containing this text')]
    [string]$NameContains,

    [Parameter(Mandatory=$false, HelpMessage='Regex filter: matches RG names matching this pattern')]
    [string]$NameRegex,

    [Parameter(Mandatory=$false, HelpMessage='Regex to exclude RG names from deletion')]
    [string]$ExcludeRegex,

    [Parameter(Mandatory=$false, HelpMessage='Remove resource and RG-level locks before deletion')]
    [switch]$RemoveLocks,

    [Parameter(Mandatory=$false, HelpMessage='Start deletions and return immediately (do not wait)')]
    [switch]$NoWait,

    [Parameter(Mandatory=$false, HelpMessage='Bypass interactive confirmation (DANGEROUS)')]
    [switch]$ForceDelete,

    [Parameter(Mandatory=$false, HelpMessage='Preview matched resource groups and exit without deleting')]
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Info($m){ Write-Host "[INFO]  $m" -ForegroundColor Cyan }
function Write-Warn($m){ Write-Host "[WARN]  $m" -ForegroundColor Yellow }
function Write-Err($m){ Write-Host "[ERROR] $m" -ForegroundColor Red }

function Ensure-AzModules {
    $mods = @('Az.Accounts','Az.Resources')
    $missing = @()
    foreach ($m in $mods) { if (-not (Get-Module -ListAvailable -Name $m)) { $missing += $m } }
    if ($missing.Count -gt 0) {
        throw "Missing Az modules: $($missing -join ', '). Install with: Install-Module Az -Scope CurrentUser"
    }
}

function Set-SubscriptionContext {
    Write-Info "Setting subscription context to $SubscriptionId"
    Set-AzContext -SubscriptionId $SubscriptionId | Out-Null
    $cid = (Get-AzContext).Subscription.Id
    if ($cid -ne $SubscriptionId) { throw "Failed to set context to $SubscriptionId (current=$cid)" }
}

function Get-TargetResourceGroups {
    $rgs = Get-AzResourceGroup
    if ($null -ne $NameContains -and $NameContains -ne '') {
        $rgs = $rgs | Where-Object { $_.ResourceGroupName -like "*${NameContains}*" }
    }
    if ($null -ne $NameRegex -and $NameRegex -ne '') {
        $rgs = $rgs | Where-Object { $_.ResourceGroupName -match $NameRegex }
    }
    if ($null -ne $ExcludeRegex -and $ExcludeRegex -ne '') {
        $rgs = $rgs | Where-Object { $_.ResourceGroupName -notmatch $ExcludeRegex }
    }
    return $rgs | Sort-Object ResourceGroupName
}

function Remove-AllLocksForRg([string]$rgName) {
    try {
        # RG-level locks
        $rgLocks = Get-AzResourceLock -ResourceGroupName $rgName -AtScope -ErrorAction SilentlyContinue
        foreach ($l in $rgLocks) {
            Write-Info "Removing RG lock '$($l.Name)' on '$rgName'"
            Remove-AzResourceLock -LockId $l.LockId -Force -ErrorAction Stop
        }
        # Locks on resources within RG
        $childLocks = Get-AzResourceLock -ResourceGroupName $rgName -ErrorAction SilentlyContinue
        foreach ($l in $childLocks) {
            Write-Info "Removing resource lock '$($l.Name)' in '$rgName'"
            Remove-AzResourceLock -LockId $l.LockId -Force -ErrorAction Stop
        }
    } catch {
        Write-Warn "Failed removing some locks in RG '$rgName': $($_.Exception.Message)"
    }
}

function Confirm-Deletion([string[]]$rgNames) {
    Write-Warn "About to DELETE the following resource groups (count=$(@($rgNames).Count)) in subscription ${SubscriptionId}:"
    $rgNames | ForEach-Object { Write-Host "  - $_" }
    if (-not $ForceDelete) {
        $title = "Confirm deletion"
        $msg = "Delete $(@($rgNames).Count) resource groups listed above? This is destructive and cannot be undone."
        $yes = New-Object System.Management.Automation.Host.ChoiceDescription "&Yes","Proceed"
        $no  = New-Object System.Management.Automation.Host.ChoiceDescription "&No","Cancel"
        $choices = [System.Management.Automation.Host.ChoiceDescription[]]($yes,$no)
        $selection = $Host.UI.PromptForChoice($title,$msg,$choices,1)
        if ($selection -ne 0) { return $false }
    }
    return $true
}

Ensure-AzModules
Set-SubscriptionContext
$targets = Get-TargetResourceGroups
if (-not $targets -or @($targets).Count -eq 0) {
    Write-Info "No resource groups matched the provided filters. Nothing to do."
    return
}

$rgNames = @($targets.ResourceGroupName)
Write-Info "Matched $(@($rgNames).Count) resource groups."

if ($DryRun) {
    Write-Warn "Dry run: the following resource groups would be deleted (no action taken):"
    $rgNames | ForEach-Object { Write-Host "  - $_" }
    return
}
if (-not (Confirm-Deletion -rgNames $rgNames)) {
    Write-Info "Operation cancelled by user."
    return
}

# Track started deletion jobs explicitly
$startedJobs = @()

foreach ($rg in $rgNames) {
    if ($PSCmdlet.ShouldProcess($rg, 'Delete Resource Group')) {
        try {
            if ($RemoveLocks) { Remove-AllLocksForRg -rgName $rg }
            Write-Info "Starting deletion of RG '$rg'..."
            # -Force suppresses prompt; -AsJob starts background job; -Confirm:$false respects ForceDelete intent
            $job = Remove-AzResourceGroup -Name $rg -Force -AsJob -Confirm:$false -ErrorAction Stop
            if ($job) { $startedJobs += $job }
        } catch {
            Write-Err "Failed to start deletion for '$rg': $($_.Exception.Message)"
        }
    }
}

if ($NoWait) {
    Write-Info "Deletion jobs started. Not waiting for completion due to -NoWait."
    return
}

Write-Info "Waiting for deletion jobs to complete..."
# Wait only on the jobs we started
if (@($startedJobs).Count -gt 0) {
    Wait-Job -Job $startedJobs | Out-Null
    # Pull results (if any) and keep for further inspection
    $null = Receive-Job -Job $startedJobs -Keep
    # Summarize job results
    $failed = $startedJobs | Where-Object { $_.State -eq 'Failed' }
    $failedCount = @($failed).Count
    $jobsCount = @($startedJobs).Count
    if ($failedCount -gt 0) {
        Write-Warn "Some deletions failed ($failedCount). Review job details with Get-Job -Id $(@($startedJobs).Id -join ',') | Receive-Job."
    } else {
        Write-Info "All deletions completed (jobs: $jobsCount)."
    }
} else {
    Write-Warn "No deletion jobs found to wait on."
}

Write-Info "Done. Note: Soft-delete resources (e.g., Key Vault with purge protection) may require separate purge operations."
