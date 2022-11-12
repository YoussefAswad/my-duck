$configDir = '.\Data'
$accountFiles = (Get-ChildItem -Path $configDir  -recurse -filter account*.conf )
#$TokenFiles = (Get-ChildItem -Path $configDir  -recurse -filter token*.txt | Group-Object -Property Directory)
$accounts = @()
Foreach ($accountFile in $accountFiles){
	Foreach ($i in $(Get-Content $accountFile)){
		$line = $i.trim()
		if (($line -ne "") -and -not ($line.StartsWith('#') -or $line.StartsWith('//'))){
			Set-Variable -Name $line.Split("=")[0] -Value $line.Split("=",2)[1]
		}
	}
	$account = @{
				'Email' = $EMAIL
				'Token' = $TOKEN
				'Domains' = $DOMAINS
			}
			$accounts += ,$account
}
while ($true)
{
	if ($true)
	{
		Foreach ($account in $accounts)
		{
			$url = "https://www.duckdns.org/update?domains=" + $account.Domains + "&token=" + $account.Token + "&ip=&verbose=true"
			$response = Invoke-WebRequest -Uri $url
			$responseStr = [System.Text.Encoding]::UTF8.GetString($response.Content)
			$responseArr = $responseStr.Split("`n") | ? { $_ }
			$responseTable = [PSCustomObject]@{
				'Success' = $(If ($responseArr[0] -eq "OK") { $true }
					Else { $false })
				'IP Address' = $responseArr[1]
				'Changed' = $(If ($responseArr[2] -eq "UPDATED") { $true }
					Else { $false })
			}
			if (!$responseTable.Success)
			{
				Write-Host "Failed to Update!"
			}
			else
			{
				if ($responseTable.Changed)
				{
					Write-Host "Updated to" $responseTable.'IP Address'
				}
			}
			$responseTable
		}
	}
	else
	{
		Write-Host "No Internet Connection"
	}
	Start-Sleep -Seconds 5
}