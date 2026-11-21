<#
.SYNOPSIS
Descarga un solo ano del ZIP JSON anual de la descarga masiva de SERCOP y registra su procedencia.

.DESCRIPTION
Hace un unico GET a la descarga masiva del portal (todos los meses y todos los tipos),
guarda el ZIP en una carpeta nueva, conserva las cabeceras HTTP de esa misma respuesta
sin cookies, compara el tamano recibido con el Content-Length de la misma respuesta,
calcula el SHA-256 y anade una fila al CSV de procedencia. No reintenta, no sigue
redirecciones y no sobrescribe nada: una descarga nueva es otra carpeta.

Un ano por ejecucion. La descarga son cientos de MB de una fuente publica: no la
programes en bucle. Patron del enlace y licencia: docs/sources/reconocimiento.md.

.PARAMETER Year
Ano del archivo anual. El portal acepta 2015 hasta el ano en curso (manual de la API).

.PARAMETER OutputRoot
Carpeta existente o nueva donde se crea la subcarpeta de la descarga. En el repositorio
principal es <raiz>/data/datos_crudos; en un worktree esa carpeta no existe, asi que se
pasa la ruta absoluta de la carpeta principal.

.PARAMETER EvidenceCsv
CSV versionado de procedencia. Por defecto docs/h2/evidencia/descargas-sercop.csv junto
al script; se crea con cabecera si no existe y se le anade una fila.

.PARAMETER LicenseUrl
URL de la licencia declarada en los paquetes OCDS.

.PARAMETER LicenseValue
Nombre corto de la licencia declarada en los paquetes OCDS.

.EXAMPLE
.\scripts\download_sercop_ocds.ps1 -Year 2022 -OutputRoot 'data/datos_crudos'
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateRange(2015, 2100)]
    [int]$Year,

    [Parameter(Mandatory = $true)]
    [string]$OutputRoot,

    [string]$EvidenceCsv = '',

    [string]$LicenseUrl = 'https://creativecommons.org/licenses/by/3.0/ec/',

    [string]$LicenseValue = 'CC BY 3.0 Ecuador',

    # Only for local tests with a synthetic server. A real download uses the portal
    # URL built from -Year; do not replace it with an invented link.
    [string]$RequestUri = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Windows PowerShell 5.1 does not always load this assembly before resolving
# HttpClient types. Fail before creating a folder or a CSV row if it is unavailable.
Add-Type -AssemblyName System.Net.Http -ErrorAction Stop

# The annual resource: all months, all procurement types. Observed in the portal filter.
if ([string]::IsNullOrWhiteSpace($RequestUri)) {
    $RequestUri = "https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/download?type=json&year=$Year&month=0&method=all"
}
$requestUri = $RequestUri
$fileName = "releases_$Year.zip"
# Ecuador has used UTC-5 without daylight saving time since 1992; the offset is fixed.
$ecuadorOffset = [System.TimeSpan]::FromHours(-5)

if ([string]::IsNullOrWhiteSpace($EvidenceCsv)) {
    $EvidenceCsv = Join-Path $PSScriptRoot '..\docs\h2\evidencia\descargas-sercop.csv'
}

$outputRootFullPath = [System.IO.Path]::GetFullPath($OutputRoot)
$evidenceCsvFullPath = [System.IO.Path]::GetFullPath($EvidenceCsv)
$startedUtc = [System.DateTimeOffset]::UtcNow
$folderName = 'sercop-ocds-json-{0}-{1}' -f $Year, $startedUtc.ToOffset($ecuadorOffset).ToString('yyyyMMdd-HHmmss')
$downloadFolder = Join-Path $outputRootFullPath $folderName
$zipPath = Join-Path $downloadFolder $fileName
$headersPath = Join-Path $downloadFolder "headers-$Year.txt"

$csvColumns = @(
    'year',
    'url',
    'http_status',
    'download_started_utc',
    'download_started_local',
    'download_finished_utc',
    'download_finished_local',
    'bytes_received',
    'content_length',
    'sha256',
    'file_name',
    'folder',
    'license_url',
    'license_value'
)

function ConvertTo-CsvCell {
    param([AllowNull()][object]$Value)

    $text = if ($null -eq $Value) { '' } else { [string]$Value }
    return '"' + $text.Replace('"', '""') + '"'
}

function Add-EvidenceRow {
    param([object[]]$Values)

    $csvDirectory = [System.IO.Path]::GetDirectoryName($evidenceCsvFullPath)
    if (-not [System.IO.Directory]::Exists($csvDirectory)) {
        [void][System.IO.Directory]::CreateDirectory($csvDirectory)
    }

    $encoding = [System.Text.UTF8Encoding]::new($false)
    if (-not [System.IO.File]::Exists($evidenceCsvFullPath)) {
        [System.IO.File]::WriteAllText($evidenceCsvFullPath, ($csvColumns -join ',') + "`r`n", $encoding)
    }

    $row = $Values | ForEach-Object { ConvertTo-CsvCell $_ }
    [System.IO.File]::AppendAllText($evidenceCsvFullPath, ($row -join ',') + "`r`n", $encoding)
}

if ([System.IO.Directory]::Exists($downloadFolder)) {
    throw "La carpeta de destino ya existe: $downloadFolder. Una descarga nueva va en otra carpeta."
}

if (-not [System.IO.Directory]::Exists($outputRootFullPath)) {
    [void][System.IO.Directory]::CreateDirectory($outputRootFullPath)
}
# CreateDirectory fails if the folder appeared after the check, so a competing
# writer cannot share this folder.
[void][System.IO.Directory]::CreateDirectory($downloadFolder)

Write-Host "Ano: $Year"
Write-Host "URL: $requestUri"
Write-Host "Carpeta: $downloadFolder"
Write-Host "CSV de procedencia: $evidenceCsvFullPath"

# Capture a redirect as a response instead of generating an unrecorded follow-up request,
# and do not accept or send cookies.
# https://learn.microsoft.com/en-us/dotnet/api/system.net.http.httpclienthandler.allowautoredirect
$handler = [System.Net.Http.HttpClientHandler]::new()
$handler.AllowAutoRedirect = $false
$handler.UseCookies = $false
$client = [System.Net.Http.HttpClient]::new($handler)
# A whole year is hundreds of MB: the timeout applies to the headers, not the body.
$client.Timeout = [System.TimeSpan]::FromMinutes(30)

$httpStatus = ''
$contentLength = ''
$hasContentLength = $false
$bytesReceived = 0
$sha256 = ''
$finishedUtc = ''
$request = $null
$response = $null
$contentStream = $null
$fileStream = $null
$failure = ''

try {
    $request = [System.Net.Http.HttpRequestMessage]::new([System.Net.Http.HttpMethod]::Get, $requestUri)
    [void]$request.Headers.TryAddWithoutValidation('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36')
    [void]$request.Headers.TryAddWithoutValidation('Accept', '*/*')
    $response = $client.SendAsync(
        $request,
        [System.Net.Http.HttpCompletionOption]::ResponseHeadersRead
    ).GetAwaiter().GetResult()

    $httpStatus = [int]$response.StatusCode
    if ($null -ne $response.Content.Headers.ContentLength) {
        $contentLength = [long]$response.Content.Headers.ContentLength
        $hasContentLength = $true
    }

    # Save the headers of this exact response, without cookies.
    $headerLines = [System.Collections.Generic.List[string]]::new()
    $headerLines.Add(('HTTP/{0} {1} {2}' -f $response.Version, $httpStatus, $response.ReasonPhrase).TrimEnd())
    foreach ($header in $response.Headers) {
        if ($header.Key -eq 'Set-Cookie') { continue }
        $headerLines.Add(('{0}: {1}' -f $header.Key, (@($header.Value) -join '; ')))
    }
    foreach ($header in $response.Content.Headers) {
        $headerLines.Add(('{0}: {1}' -f $header.Key, (@($header.Value) -join '; ')))
    }
    [System.IO.File]::WriteAllText(
        $headersPath,
        (($headerLines -join "`r`n") + "`r`n"),
        [System.Text.UTF8Encoding]::new($false)
    )

    if ($httpStatus -ne 200) {
        throw "El portal respondio HTTP $httpStatus. Se conservan las cabeceras y no se descarga el cuerpo."
    }

    $contentStream = $response.Content.ReadAsStreamAsync().GetAwaiter().GetResult()
    # CreateNew refuses to reuse a file; the folder was created empty in this run.
    $fileStream = [System.IO.File]::Open(
        $zipPath,
        [System.IO.FileMode]::CreateNew,
        [System.IO.FileAccess]::ReadWrite,
        [System.IO.FileShare]::None
    )
    try {
        $contentStream.CopyTo($fileStream, 1048576)
        $bytesReceived = $fileStream.Length
        $fileStream.Position = 0
        $hasher = [System.Security.Cryptography.SHA256]::Create()
        try {
            $sha256 = -join ($hasher.ComputeHash($fileStream) | ForEach-Object { $_.ToString('X2') })
        }
        finally {
            $hasher.Dispose()
        }
    }
    catch {
        $bytesReceived = $fileStream.Length
        throw
    }
}
catch {
    $failure = $_.Exception.GetBaseException().Message
}
finally {
    if ($null -ne $fileStream) { $fileStream.Dispose() }
    if ($null -ne $contentStream) { $contentStream.Dispose() }
    if ($null -ne $response) { $response.Dispose() }
    if ($null -ne $request) { $request.Dispose() }
    $client.Dispose()
}

$finishedUtc = [System.DateTimeOffset]::UtcNow

# Folder path recorded in CSV: relative to repo root with forward slashes (e.g. data/datos_crudos/sercop-ocds-json-...)
$recordedFolder = $downloadFolder
if ($downloadFolder -match '(?i)(?:^|[\\/])(data[\\/]datos_crudos[\\/][^\\/]+)$') {
    $recordedFolder = $Matches[1] -replace '\\', '/'
}
else {
    $repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..')).TrimEnd('\', '/')
    if ($downloadFolder.StartsWith($repoRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        $rel = $downloadFolder.Substring($repoRoot.Length).TrimStart('\', '/')
        $recordedFolder = $rel -replace '\\', '/'
    }
    else {
        $outRootFull = $outputRootFullPath.TrimEnd('\', '/')
        if ($downloadFolder.StartsWith($outRootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
            $rel = $downloadFolder.Substring($outRootFull.Length).TrimStart('\', '/')
            $recordedFolder = $rel -replace '\\', '/'
        }
        else {
            $recordedFolder = $folderName
        }
    }
}

Add-EvidenceRow @(
    $Year,
    $requestUri,
    $httpStatus,
    $startedUtc.ToString('o'),
    $startedUtc.ToOffset($ecuadorOffset).ToString('yyyy-MM-dd HH:mm:ss'),
    $finishedUtc.ToString('o'),
    $finishedUtc.ToOffset($ecuadorOffset).ToString('yyyy-MM-dd HH:mm:ss'),
    $bytesReceived,
    $contentLength,
    $sha256,
    $fileName,
    $recordedFolder,
    $LicenseUrl,
    $LicenseValue
)

if ($failure) {
    if ($hasContentLength -and [long]$contentLength -ne $bytesReceived) {
        throw "La descarga no termino bien ($failure): el tamano recibido ($bytesReceived) no coincide con el Content-Length de la misma respuesta ($contentLength). Revisa la fila del CSV y la carpeta $downloadFolder."
    }
    throw "La descarga no termino bien: $failure. Revisa la fila del CSV y la carpeta $downloadFolder."
}

# A raw file is evidence: mark it read-only so nobody edits it by accident.
# To delete it later: Set-ItemProperty -Path <archivo> -Name IsReadOnly -Value $false
foreach ($path in @($zipPath, $headersPath)) {
    Set-ItemProperty -Path $path -Name IsReadOnly -Value $true
}

Write-Host "Bytes recibidos: $bytesReceived; Content-Length: $contentLength"
Write-Host "SHA-256: $sha256"
Write-Host "Archivo: $zipPath"

if (-not $hasContentLength) {
    Write-Warning 'La respuesta no anuncio Content-Length; no hay tamano esperado con el que comparar.'
}
elseif ([long]$contentLength -ne $bytesReceived) {
    throw "El tamano recibido ($bytesReceived) no coincide con el Content-Length de la misma respuesta ($contentLength). El archivo queda como evidencia; no lo uses sin revisarlo."
}

Write-Host 'Descarga completa: tamano, cabeceras, SHA-256 y fila de procedencia registrados.'
