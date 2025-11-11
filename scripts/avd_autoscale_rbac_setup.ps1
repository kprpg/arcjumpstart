# Azure Virtual Desktop Autoscale RBAC Setup Script
# Purpose: Idempotently ensure the Azure Virtual Desktop (AVD) service principal exists in the tenant
#          and assign required roles at subscription scope for autoscale (scaling plan) operations.
# Requirements: Azure CLI installed and logged in (az login). Caller must have Owner or User Access Administrator
#               on the target subscription and sufficient Entra ID permissions (Application Administrator) if
#               enterprise app needs to be created.

param(
    [Parameter(Mandatory=$true)][string]$SubscriptionId,
    [Parameter(Mandatory=$false)][string]$HostPoolName,
    [Parameter(Mandatory=$false)][string]$HostPoolResourceGroup,
    [switch]$VerboseOutput
)

$ErrorActionPreference = 'Stop'

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "[ERROR] $msg" -ForegroundColor Red }

$avdAppId = '9cdead84-a844-4324-93f2-b2e6bb768d07'   # Azure Virtual Desktop multi-tenant application ID
$requiredRoles = @(
    'Desktop Virtualization Power On Off Contributor',
    'Desktop Virtualization Virtual Machine Contributor'
)

function Get-AvdServicePrincipal {
    Write-Info "Searching for AVD service principal by appId..."
    $spJson = az ad sp list --filter "appId eq '$avdAppId'" --query "[0]" -o json 2>$null
    if (-not $spJson -or $spJson -eq 'null') {
        Write-Info "Not found by appId. Trying by display names..."
        foreach ($name in 'Azure Virtual Desktop','Windows Virtual Desktop') {
            $spJson = az ad sp list --display-name $name --query "[0]" -o json 2>$null
            if ($spJson -and $spJson -ne 'null') { break }
        }
    }
    if ($spJson -and $spJson -ne 'null') {
        return ($spJson | ConvertFrom-Json)
    }
    return $null
}

function Ensure-AvdServicePrincipal {
    $sp = Get-AvdServicePrincipal
    if ($sp) {
        Write-Info "Found AVD service principal: displayName='${($sp.displayName)}' objectId='${($sp.id)}'"
        return $sp
    }
    Write-Warn "AVD service principal not found. Attempting creation (requires Entra admin rights)."
    try {
        az ad sp create --id $avdAppId | Out-Null
    } catch {
        Write-Err "Creation failed: $($_.Exception.Message). Ensure you have Application Administrator or equivalent."
        throw
    }
    Start-Sleep -Seconds 5
    $sp = Get-AvdServicePrincipal
    if (-not $sp) { throw "Service principal still not found after creation attempt." }
    Write-Info "Created AVD service principal: objectId='${($sp.id)}'"
    return $sp
}

function Assign-AvdAutoscaleRoles($spObjectId) {
    Write-Info "Assigning required autoscale roles at subscription scope..."
    foreach ($role in $requiredRoles) {
        Write-Info "Ensuring role '$role' is assigned..."
        $existing = az role assignment list --assignee-object-id $spObjectId --scope "/subscriptions/$SubscriptionId" --query "[?roleDefinitionName=='$role']" -o json 2>$null
        if ($existing -and $existing -ne '[]') {
            Write-Info "Role '$role' already assigned. Skipping."
            continue
        }
        az role assignment create `
            --assignee-object-id $spObjectId `
            --assignee-principal-type ServicePrincipal `
            --role "$role" `
            --scope "/subscriptions/$SubscriptionId" | Out-Null
        Write-Info "Role '$role' assigned."
    }
}

function Validate-HostPoolPrereqs {
    if (-not $HostPoolName -or -not $HostPoolResourceGroup) { return }
    Write-Info "Validating host pool '$HostPoolName' in RG '$HostPoolResourceGroup'..."
    try {
        $hp = az desktopvirtualization hostpool show -g $HostPoolResourceGroup -n $HostPoolName -o json | ConvertFrom-Json
    } catch {
        Write-Warn "Unable to retrieve host pool. $_"
        return
    }
    $maxSession = $hp.maxSessionLimit
    if (-not $maxSession -or $maxSession -lt 1) {
        Write-Warn "Host pool has default or invalid MaxSessionLimit. Set a custom value for autoscale load balancing."
    } else {
        Write-Info "Host pool MaxSessionLimit: $maxSession"
    }
    Write-Info "Host pool type: $($hp.hostPoolType) (personal vs pooled impacts autoscale method)."
}

function Validate-ProviderRegistration {
    Write-Info "Checking resource provider registration..."
    $state = az provider show --namespace Microsoft.DesktopVirtualization --query registrationState -o tsv 2>$null
    if ($state -ne 'Registered') {
        Write-Warn "Provider not registered (state=$state). Attempting registration..."
        az provider register --namespace Microsoft.DesktopVirtualization | Out-Null
        Start-Sleep -Seconds 5
        $state = az provider show --namespace Microsoft.DesktopVirtualization --query registrationState -o tsv 2>$null
        if ($state -ne 'Registered') { Write-Warn "Provider still not registered. Check permissions." } else { Write-Info "Provider registered." }
    } else { Write-Info "Provider already registered." }
}

function Main {
    Write-Info "Setting subscription context..."
    az account set --subscription $SubscriptionId
    $current = az account show --query id -o tsv
    if ($current -ne $SubscriptionId) { throw "Failed to set subscription context." }

    Validate-ProviderRegistration
    $sp = Ensure-AvdServicePrincipal
    Assign-AvdAutoscaleRoles -spObjectId $sp.id
    Validate-HostPoolPrereqs

    Write-Info "Verification of role assignments:"
    az role assignment list --assignee-object-id $sp.id --scope "/subscriptions/$SubscriptionId" --query "[].{role:roleDefinitionName,scope:scope}" -o table

    Write-Info "Completed AVD autoscale RBAC setup."
}

try {
    Main
} catch {
    Write-Err "Script failed: $($_.Exception.Message)"
    exit 1
}
