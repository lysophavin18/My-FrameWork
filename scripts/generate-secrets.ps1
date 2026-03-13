param()

function New-SecretHex([int]$bytes = 32) {
  $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
  $data = New-Object byte[]($bytes)
  $rng.GetBytes($data)
  ($data | ForEach-Object { $_.ToString("x2") }) -join ""
}

$vars = @{
  POSTGRES_PASSWORD = (New-SecretHex 32)
  REDIS_PASSWORD    = (New-SecretHex 32)
  SECRET_KEY        = (New-SecretHex 32)
  JWT_SECRET_KEY    = (New-SecretHex 32)
  OPENVAS_PASSWORD  = (New-SecretHex 32)
}

$vars.GetEnumerator() | Sort-Object Name | ForEach-Object { "{0}={1}" -f $_.Name, $_.Value }

