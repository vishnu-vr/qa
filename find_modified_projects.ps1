[CmdletBinding()]
Param(
    [Parameter(Mandatory = $True, Position = 1)]
    [string] $Commit_1,
    [Parameter(Mandatory = $True, Position = 2)]
    [string] $Commit_2
)

function Get-Csproj {
    param (
        $Location
    )
    return Get-ChildItem -path $Location\*.csproj -Name
}

function Find-ProjectName {
    param (
        $File
    )

    [System.Collections.ArrayList]$File = $File.split('/')

    $projectName = $null
    while ($File.count -ne 0) {
        $path = $File -join '/'

        # check whether this is a file or a directory
        $isContainer = Test-Path -Path $path -PathType Container
        if ($isContainer -eq $False){
            # whether its in the base directory
            if ($File.count -eq 1){
                # get the csproj in the base directory
                $projectName = Get-Csproj -Location $git_loc
            }
            # a file not in the base directory
            else {
                [System.Collections.ArrayList]$newPath = $path.split('/')
                $newPath.RemoveAt($newPath.Count - 1)
                [String]$newPath = $newPath -join '/'
                $projectName = Get-Csproj -Location $newPath
            }
        }
        # this is a directory
        else{
            $projectName = Get-Csproj -Location $path
        }

        if ($null -ne $projectName){
            return $projectName
        }

        # end
        $File.RemoveAt($File.Count - 1)
    }
}

function Find-ModifiedDLLs($Commit_1, $Commit_2) {
    $modified_files = git diff --name-only $Commit_1 $Commit_2
    $modified_files = $modified_files.split()
    # Write-Host $null -eq $modified_files
    # Write-Host "here"
    if ($null -eq $modified_files -or $modified_files.Count -eq 0){
        return
    }
    
    foreach ($file in $modified_files) {
        $out = Find-ProjectName -File $file
        if ($null -ne $out){
            Write-Host $out
        }
    }
}

# provide atleast 6 characters of the hash
if ($Commit_1.length -lt 5 -Or $Commit_2.length -lt 5) {
    Write-Output "Please enter atleast 6 character of the commit hash."
}

# FOR TESTING PURPOSES ONLY
$location = Get-Location
$git_loc = "D:\emrgateway"
# $git_loc = "D:\"
Push-Location $git_loc

# find whether the given location contains a .git folder
try {
    Get-ChildItem -path $git_loc\.git -Name --no-verbose -ErrorAction Stop
}
catch {
    Write-Host "Given location doesn't contain a .git folder"
    Exit
}

Find-ModifiedDLLs $Commit_1 $Commit_2

# FOR TESTING PURPOSES ONLY
Push-Location $location