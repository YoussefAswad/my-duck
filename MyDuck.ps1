$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$domainFiles = (Get-ChildItem -Path $scriptDir -recurse -filter domains*.txt | Group-Object -Property Directory)
$tokenFiles = (Get-ChildItem -Path $scriptDir -recurse -filter token*.txt | Group-Object -Property Directory)


while($true){
    For ($i=0; $i -lt $domainFiles.Count; $i++) {
        $domainFile = Get-Content ($domainFiles.Name +"\"+ $domainFiles.Group[$i])
        $token = Get-Content ($tokenFiles.Name +"\"+ $tokenFiles.Group[$i])

        $domains = $null 

        Foreach($d in $domainFile){

            if($domains -eq $null){
                $domains = $d
            }
            else{
                $domains = $domains +"," + $d
            }
        }
        $url = "https://www.duckdns.org/update?domains=" + $domains + "&token=" + $token + "&ip=&verbose=true"
        $response = Invoke-WebRequest -Uri $url
        $responseStr = [System.Text.Encoding]::UTF8.GetString($response.Content)
        $responseArr = $responseStr.Split([Environment]::NewLine) | ? {$_}
        $responseTable = [PSCustomObject]@{
                            'Success' = $(If ($responseArr[0] -eq "OK") {$true} Else {$false}) 
                            'IP Address'  = $responseArr[1]
                            'Changed'  = $(If ($responseArr[2] -eq "UPDATED") {$true} Else {$false})
                         }
        $responseTable
                                
    }
    TIMEOUT /T 300
}

