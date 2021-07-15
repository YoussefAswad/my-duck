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
        $url = "https://www.duckdns.org/update?domains=" + $domains + "&token=" + $token + "&ip="
        $response = Invoke-WebRequest -Uri $url
        $content = $response.content
        $status = [String] ([Char] $content[0] + [Char] $content[1])
        $status
    }
    TIMEOUT /T 300
}

