Get-AppxPackage *CoPilot* -AllUsers | Remove-AppPackage -AllUsers

Get-AppxProvisionedPackage -Online | where-object {$_.PackageName -like "*Copilot*"} | Remove-AppxProvisionedPackage -online