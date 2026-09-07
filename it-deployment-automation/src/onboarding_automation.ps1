<#
.SYNOPSIS
    Automates new-hire account setup for Meridian Manufacturing: AD account creation,
    department/role-based security group assignment, home directory provisioning,
    Exchange mailbox creation, and (where eligible) VPN group membership.

.DESCRIPTION
    Reads a CSV of new hires (one row per employee: name, department, role, start date,
    remote-eligibility) and, for each row, provisions the account end to end from a single
    source of truth — the $DepartmentGroupMap table below — instead of a technician
    assigning groups from memory or a printed cheat-sheet. That's the actual fix: the
    manual process's error rate wasn't a training problem, it was a "recalling the right
    list under time pressure" problem, and a lookup table doesn't forget.

    Designed to run against a real Active Directory + Exchange Online environment via the
    ActiveDirectory and ExchangeOnlineManagement PowerShell modules. Not executed against
    live infrastructure in this portfolio (none is available in this sandbox) — this is the
    real, runnable script; data/raw/*.csv and src/onboarding_analysis.py simulate what running
    it at Meridian's actual new-hire volume would look like. See README.md for that analysis.

.PARAMETER NewHireCsvPath
    Path to a CSV with columns: hire_id, first_name, last_name, department, role,
    start_date, manager_upn, remote_eligible (Y/N).

.PARAMETER WhatIf
    Standard PowerShell ShouldProcess support — run with -WhatIf to preview every
    action (account creation, group adds, mailbox creation) without making changes.

.EXAMPLE
    .\onboarding_automation.ps1 -NewHireCsvPath .\data\raw\new_hires_this_week.csv -WhatIf
#>

[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $true)]
    [string]$NewHireCsvPath,

    [string]$LogPath = ".\onboarding-log-$(Get-Date -Format 'yyyyMMdd-HHmmss').csv",

    [string]$HomeDriveRoot = "\\FILE01\Homes",

    [string]$OuBase = "OU=Employees,DC=meridianmfg,DC=local"
)

# ----------------------------------------------------------------------------
# Single source of truth for department -> required security groups.
# This table is the actual fix for the manual process's error rate: it's the
# one place group requirements live, instead of living in a technician's head
# or a printed cheat-sheet that gets out of date the moment a new group ships.
# ----------------------------------------------------------------------------
$DepartmentGroupMap = @{
    "Warehouse & Ops" = @("GRP-WMS-Users", "GRP-Warehouse-Floor", "GRP-Timeclock")
    "Office/Admin"    = @("GRP-Office365-Standard", "GRP-SharedDrive-Admin")
    "Sales"           = @("GRP-CRM-Users", "GRP-Office365-Standard", "GRP-SharedDrive-Sales")
    "Finance"         = @("GRP-ERP-Finance", "GRP-Office365-Standard", "GRP-SharedDrive-Finance")
    "IT"              = @("GRP-Office365-Standard", "GRP-IT-Admins", "GRP-VPN-Standard")
    "HR"              = @("GRP-HRIS-Users", "GRP-Office365-Standard", "GRP-SharedDrive-HR-Restricted")
    "Engineering"     = @("GRP-PLM-Users", "GRP-Office365-Standard", "GRP-SharedDrive-Engineering")
}
$RemoteVpnGroup = "GRP-VPN-Standard"

function Test-Prerequisites {
    [CmdletBinding()]
    param()
    $missing = @()
    foreach ($module in @("ActiveDirectory", "ExchangeOnlineManagement")) {
        if (-not (Get-Module -ListAvailable -Name $module)) {
            $missing += $module
        }
    }
    if ($missing.Count -gt 0) {
        throw "Missing required module(s): $($missing -join ', '). Install with Install-Module before running."
    }
    if (-not (Test-Path $NewHireCsvPath)) {
        throw "New-hire CSV not found at path: $NewHireCsvPath"
    }
}

function New-SamAccountName {
    param([string]$FirstName, [string]$LastName)
    # first initial + last name, lowercased, truncated to 20 chars (SAM account name limit),
    # with a numeric suffix loop if the account already exists
    $base = ("{0}{1}" -f $FirstName.Substring(0,1), $LastName).ToLower() -replace '[^a-z0-9]', ''
    $base = $base.Substring(0, [Math]::Min(20, $base.Length))
    $candidate = $base
    $suffix = 1
    while (Get-ADUser -Filter "SamAccountName -eq '$candidate'" -ErrorAction SilentlyContinue) {
        $suffix++
        $candidate = "{0}{1}" -f $base.Substring(0, [Math]::Min(19, $base.Length)), $suffix
    }
    return $candidate
}

function New-EmployeeAccount {
    [CmdletBinding(SupportsShouldProcess = $true)]
    param($Hire)

    $samAccountName = New-SamAccountName -FirstName $Hire.first_name -LastName $Hire.last_name
    $upn = "$samAccountName@meridianmfg.com"
    $tempPassword = ConvertTo-SecureString ([System.Web.Security.Membership]::GeneratePassword(16, 4)) -AsPlainText -Force

    if ($PSCmdlet.ShouldProcess($upn, "Create AD user account")) {
        New-ADUser `
            -Name "$($Hire.first_name) $($Hire.last_name)" `
            -GivenName $Hire.first_name `
            -Surname $Hire.last_name `
            -SamAccountName $samAccountName `
            -UserPrincipalName $upn `
            -Path $OuBase `
            -AccountPassword $tempPassword `
            -ChangePasswordAtLogon $true `
            -Enabled $true `
            -Department $Hire.department `
            -Title $Hire.role `
            -Manager $Hire.manager_upn
    }
    return [PSCustomObject]@{
        SamAccountName = $samAccountName
        Upn            = $upn
    }
}

function Add-RequiredGroups {
    [CmdletBinding(SupportsShouldProcess = $true)]
    param([string]$SamAccountName, [string]$Department, [bool]$RemoteEligible)

    if (-not $DepartmentGroupMap.ContainsKey($Department)) {
        Write-Warning "No group mapping found for department '$Department' — $SamAccountName was NOT added to any department group. Update `$DepartmentGroupMap and re-run for this hire."
        return @()
    }

    $groups = [System.Collections.Generic.List[string]]::new($DepartmentGroupMap[$Department])
    if ($RemoteEligible -and -not $groups.Contains($RemoteVpnGroup)) {
        $groups.Add($RemoteVpnGroup)
    }

    foreach ($group in $groups) {
        if ($PSCmdlet.ShouldProcess($SamAccountName, "Add to group $group")) {
            Add-ADGroupMember -Identity $group -Members $SamAccountName
        }
    }
    return $groups
}

function New-HomeDirectory {
    [CmdletBinding(SupportsShouldProcess = $true)]
    param([string]$SamAccountName)

    $path = Join-Path $HomeDriveRoot $SamAccountName
    if ($PSCmdlet.ShouldProcess($path, "Create home directory")) {
        New-Item -Path $path -ItemType Directory -Force | Out-Null
        $acl = Get-Acl $path
        $rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
            "MERIDIANMFG\$SamAccountName", "Modify", "ContainerInherit,ObjectInherit", "None", "Allow")
        $acl.AddAccessRule($rule)
        Set-Acl -Path $path -AclObject $acl
    }
    return $path
}

function New-EmployeeMailbox {
    [CmdletBinding(SupportsShouldProcess = $true)]
    param([string]$Upn, [string]$FirstName, [string]$LastName)

    if ($PSCmdlet.ShouldProcess($Upn, "Create Exchange Online mailbox")) {
        Enable-Mailbox -Identity $Upn -Alias ($Upn.Split('@')[0])
        Set-Mailbox -Identity $Upn -DisplayName "$FirstName $LastName"
    }
}

function Invoke-Onboarding {
    [CmdletBinding(SupportsShouldProcess = $true)]
    param()

    Test-Prerequisites
    $hires = Import-Csv -Path $NewHireCsvPath
    $log = [System.Collections.Generic.List[object]]::new()

    foreach ($hire in $hires) {
        Write-Host "Provisioning $($hire.first_name) $($hire.last_name) ($($hire.department) / $($hire.role))..."
        $account = New-EmployeeAccount -Hire $hire
        $remoteEligible = $hire.remote_eligible -eq "Y"
        $groupsAssigned = Add-RequiredGroups -SamAccountName $account.SamAccountName -Department $hire.department -RemoteEligible $remoteEligible
        $homeDir = New-HomeDirectory -SamAccountName $account.SamAccountName
        New-EmployeeMailbox -Upn $account.Upn -FirstName $hire.first_name -LastName $hire.last_name

        $log.Add([PSCustomObject]@{
            HireId          = $hire.hire_id
            SamAccountName  = $account.SamAccountName
            Upn             = $account.Upn
            Department      = $hire.department
            Role            = $hire.role
            RemoteEligible  = $remoteEligible
            GroupsAssigned  = ($groupsAssigned -join ";")
            GroupCount      = $groupsAssigned.Count
            HomeDirectory   = $homeDir
            ProvisionedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
        })
    }

    $log | Export-Csv -Path $LogPath -NoTypeInformation
    Write-Host "`nOnboarding complete: $($log.Count) accounts provisioned. Report written to $LogPath"
    return $log
}

Invoke-Onboarding
