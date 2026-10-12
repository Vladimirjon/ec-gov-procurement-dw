[CmdletBinding(DefaultParameterSetName = 'Minutes')]
param(
    [ValidateRange(1, 48)]
    [int]$Samples = 10,

    [ValidateRange(0, 86400)]
    [int]$InitialDelaySeconds = 0,

    [Parameter(ParameterSetName = 'Minutes')]
    [ValidateRange(1, 1440)]
    [int]$IntervalMinutes = 10,

    [Parameter(ParameterSetName = 'Seconds')]
    [ValidateRange(10, 86400)]
    [int]$IntervalSeconds = 10,

    [ValidateRange(0, 59)]
    [int]$StopAtRemaining = 10,

    [string]$OutputPath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$requestUri = 'https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/api/search_ocds?year=2025&search=agua&page=1'
$runId = [guid]::NewGuid().ToString('D')
if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $PSScriptRoot ("..\docs\sources\sercop-api-rate-limit-observations-v3-$runId.csv")
}
$sampleIntervalSeconds = if ($PSCmdlet.ParameterSetName -eq 'Seconds') {
    $IntervalSeconds
} else {
    $IntervalMinutes * 60
}
$sampleIntervalDescription = if ($PSCmdlet.ParameterSetName -eq 'Seconds') {
    "$IntervalSeconds segundo(s)"
} else {
    "$IntervalMinutes minuto(s)"
}
$outputFullPath = [System.IO.Path]::GetFullPath($OutputPath)
$outputDirectory = [System.IO.Path]::GetDirectoryName($outputFullPath)
$csvColumns = @(
    'run_id',
    'sample',
    'request_started_utc',
    'response_received_utc',
    'response_date',
    'request_url',
    'http_status',
    'rate_limit_limit',
    'x_rate_limit_limit',
    'rate_limit_remaining',
    'x_rate_limit_remaining',
    'rate_limit_reset',
    'x_rate_limit_reset',
    'rate_limit_policy',
    'x_rate_limit_policy',
    'rate_limit_window',
    'x_rate_limit_window',
    'retry_after',
    'response_age',
    'response_cache_control',
    'response_via',
    'response_x_cache',
    'response_request_url',
    'redirect_location_present',
    'client_allow_redirects',
    'request_cache_control',
    'transport_error'
)

function ConvertTo-CsvCell {
    param([AllowNull()][object]$Value)

    $text = if ($null -eq $Value) { '' } else { [string]$Value }
    return '"' + $text.Replace('"', '""') + '"'
}

function Get-ResponseHeaderValue {
    param(
        [System.Net.Http.Headers.HttpResponseHeaders]$ResponseHeaders,
        [string[]]$Names
    )

    foreach ($name in $Names) {
        # All monitored fields are response headers. Checking a response-only
        # name such as Retry-After on Content.Headers throws when it is absent.
        if ($null -ne $ResponseHeaders -and $ResponseHeaders.Contains($name)) {
            $values = @($ResponseHeaders.GetValues($name))
            if ($values.Count -gt 0) {
                return ($values -join ';')
            }
        }
    }

    return ''
}

if (-not [System.IO.Directory]::Exists($outputDirectory)) {
    [void][System.IO.Directory]::CreateDirectory($outputDirectory)
}

if ([System.IO.File]::Exists($outputFullPath)) {
    throw 'La salida ya existe: elige otro OutputPath para conservar la evidencia anterior.'
}

# CreateNew also rejects a competing writer that creates this file after the check.
# Source: https://learn.microsoft.com/en-us/dotnet/api/system.io.filemode#fields
$headerStream = [System.IO.File]::Open(
    $outputFullPath,
    [System.IO.FileMode]::CreateNew,
    [System.IO.FileAccess]::Write,
    [System.IO.FileShare]::None
)
try {
    $headerBytes = [System.Text.UTF8Encoding]::new($false).GetBytes(($csvColumns -join ',') + "`r`n")
    $headerStream.Write($headerBytes, 0, $headerBytes.Length)
}
finally {
    $headerStream.Dispose()
}

# Capture redirect responses rather than generating unrecorded follow-up requests.
# https://learn.microsoft.com/en-us/dotnet/api/system.net.http.httpclienthandler.allowautoredirect
$handler = [System.Net.Http.HttpClientHandler]::new()
$handler.AllowAutoRedirect = $false
$handler.UseCookies = $false
$client = [System.Net.Http.HttpClient]::new($handler)
$client.Timeout = [System.TimeSpan]::FromSeconds(30)

Write-Host "Run ID: $runId"
Write-Host "Muestras solicitadas: $Samples; espera inicial: $InitialDelaySeconds segundo(s); intervalo entre muestras: $sampleIntervalDescription."
Write-Host "Se registran solo estado y cabeceras; no se lee ni guarda el cuerpo de la respuesta."
Write-Host "Archivo de observaciones: $outputFullPath"

try {
    if ($InitialDelaySeconds -gt 0) {
        Write-Host "Esperando $InitialDelaySeconds segundo(s) antes de la primera muestra..."
        Start-Sleep -Seconds $InitialDelaySeconds
    }

    for ($sample = 1; $sample -le $Samples; $sample++) {
        if ($sample -gt 1) {
            Write-Host "Esperando $sampleIntervalDescription para la siguiente muestra..."
            Start-Sleep -Seconds $sampleIntervalSeconds
        }

        $requestStartedUtc = [System.DateTimeOffset]::UtcNow
        $responseReceivedUtc = ''
        $httpStatus = ''
        $responseDate = ''
        $rateLimitLimit = ''
        $xRateLimitLimit = ''
        $rateLimitRemaining = ''
        $xRateLimitRemaining = ''
        $rateLimitReset = ''
        $xRateLimitReset = ''
        $rateLimitPolicy = ''
        $xRateLimitPolicy = ''
        $rateLimitWindow = ''
        $xRateLimitWindow = ''
        $retryAfter = ''
        $responseAge = ''
        $responseCacheControl = ''
        $responseVia = ''
        $responseXCache = ''
        $responseRequestUrl = ''
        $redirectLocationPresent = ''
        $transportError = ''
        $request = $null
        $response = $null

        try {
            $request = [System.Net.Http.HttpRequestMessage]::new(
                [System.Net.Http.HttpMethod]::Get,
                $requestUri
            )
            # Request revalidation; this does not prove that every intermediary obeys it.
            # https://www.rfc-editor.org/rfc/rfc9111.html#section-5.2.1.4
            [void]$request.Headers.TryAddWithoutValidation('Cache-Control', 'no-cache')
            $response = $client.SendAsync(
                $request,
                [System.Net.Http.HttpCompletionOption]::ResponseHeadersRead
            ).GetAwaiter().GetResult()

            $responseReceivedUtc = [System.DateTimeOffset]::UtcNow.ToString('o')
            $httpStatus = [int]$response.StatusCode
            $responseDate = Get-ResponseHeaderValue `
                -ResponseHeaders $response.Headers `
                -Names @('Date')
            $rateLimitLimit = Get-ResponseHeaderValue `
                -ResponseHeaders $response.Headers `
                -Names @('RateLimit-Limit')
            $xRateLimitLimit = Get-ResponseHeaderValue `
                -ResponseHeaders $response.Headers `
                -Names @('X-RateLimit-Limit')
            $rateLimitRemaining = Get-ResponseHeaderValue `
                -ResponseHeaders $response.Headers `
                -Names @('RateLimit-Remaining')
            $xRateLimitRemaining = Get-ResponseHeaderValue `
                -ResponseHeaders $response.Headers `
                -Names @('X-RateLimit-Remaining')
            $rateLimitReset = Get-ResponseHeaderValue `
                -ResponseHeaders $response.Headers `
                -Names @('RateLimit-Reset')
            $xRateLimitReset = Get-ResponseHeaderValue `
                -ResponseHeaders $response.Headers `
                -Names @('X-RateLimit-Reset')
            $rateLimitPolicy = Get-ResponseHeaderValue `
                -ResponseHeaders $response.Headers `
                -Names @('RateLimit-Policy')
            $xRateLimitPolicy = Get-ResponseHeaderValue `
                -ResponseHeaders $response.Headers `
                -Names @('X-RateLimit-Policy')
            $rateLimitWindow = Get-ResponseHeaderValue `
                -ResponseHeaders $response.Headers `
                -Names @('RateLimit-Window')
            $xRateLimitWindow = Get-ResponseHeaderValue `
                -ResponseHeaders $response.Headers `
                -Names @('X-RateLimit-Window')
            $retryAfter = Get-ResponseHeaderValue `
                -ResponseHeaders $response.Headers `
                -Names @('Retry-After')
            $responseAge = Get-ResponseHeaderValue -ResponseHeaders $response.Headers -Names @('Age')
            $responseCacheControl = Get-ResponseHeaderValue -ResponseHeaders $response.Headers -Names @('Cache-Control')
            $responseVia = Get-ResponseHeaderValue -ResponseHeaders $response.Headers -Names @('Via')
            $responseXCache = Get-ResponseHeaderValue -ResponseHeaders $response.Headers -Names @('X-Cache')
            if ($null -ne $response.RequestMessage) {
                $responseRequestUrl = $response.RequestMessage.RequestUri.AbsoluteUri
            }
            # Do not log Location values: an untrusted destination can include credentials.
            $redirectLocationPresent = $response.Headers.Contains('Location').ToString().ToLowerInvariant()
        }
        catch {
            $transportError = $_.Exception.GetBaseException().GetType().FullName
        }
        finally {
            if ($null -ne $response) { $response.Dispose() }
            if ($null -ne $request) { $request.Dispose() }
        }

        $row = @(
            $runId,
            $sample,
            $requestStartedUtc.ToString('o'),
            $responseReceivedUtc,
            $responseDate,
            $requestUri,
            $httpStatus,
            $rateLimitLimit,
            $xRateLimitLimit,
            $rateLimitRemaining,
            $xRateLimitRemaining,
            $rateLimitReset,
            $xRateLimitReset,
            $rateLimitPolicy,
            $xRateLimitPolicy,
            $rateLimitWindow,
            $xRateLimitWindow,
            $retryAfter,
            $responseAge,
            $responseCacheControl,
            $responseVia,
            $responseXCache,
            $responseRequestUrl,
            $redirectLocationPresent,
            'false',
            'no-cache',
            $transportError
        ) | ForEach-Object { ConvertTo-CsvCell $_ }
        [System.IO.File]::AppendAllText(
            $outputFullPath,
            ($row -join ',') + "`r`n",
            [System.Text.UTF8Encoding]::new($false)
        )

        Write-Host ("[{0}/{1}] HTTP={2}; RateLimit-Limit={3}; X-RateLimit-Limit={4}; RateLimit-Remaining={5}; X-RateLimit-Remaining={6}; RateLimit-Reset={7}; X-RateLimit-Reset={8}" -f `
            $sample, $Samples, $httpStatus, $rateLimitLimit, $xRateLimitLimit, `
            $rateLimitRemaining, $xRateLimitRemaining, $rateLimitReset, $xRateLimitReset)

        if ($transportError) {
            if ($httpStatus) {
                Write-Warning "La API respondió HTTP $httpStatus, pero falló el registro local de cabeceras ($transportError); la fila puede estar incompleta. Se detiene sin reintentar."
            }
            else {
                Write-Warning "La consulta falló por transporte ($transportError); se detiene sin reintentar."
            }
            break
        }

        if ($httpStatus -eq 429) {
            Write-Warning 'La API respondió 429; se detiene sin reintentar para no insistir sobre el límite.'
            break
        }

        if ($httpStatus -ne 200) {
            Write-Warning "La API respondió HTTP $httpStatus; se detiene sin seguir redirecciones ni reintentar."
            break
        }

        $remainingNumber = 0
        $effectiveRemaining = if ($rateLimitRemaining) { $rateLimitRemaining } else { $xRateLimitRemaining }
        if ([int]::TryParse($effectiveRemaining, [ref]$remainingNumber) -and
            $remainingNumber -le $StopAtRemaining) {
            Write-Warning "Remaining llegó a $remainingNumber; se detiene para conservar un margen de cuota."
            break
        }
    }
}
finally {
    $client.Dispose()
}

Write-Host "Fin de la observación. Revisa el CSV; run_id=$runId"
