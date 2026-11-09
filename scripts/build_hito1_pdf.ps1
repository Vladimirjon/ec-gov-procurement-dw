<#
.SYNOPSIS
    Builds the Hito 1 PDF from docs/requirements/hito1.md.

.DESCRIPTION
    The Markdown file is the source of the deliverable. This helper converts it to
    HTML with pandoc, prints the HTML to PDF with a Chromium-based browser (Edge or
    Chrome, headless) and checks the page limits of the course guide:
      * Part 1 (institutional profile): at most 3 pages.
      * Everything before the annexes: at most 6 pages.
    The section "Criterios de aceptación del hito" is the team's checklist and is not
    part of the PDF. Relative links to files of this repository become absolute
    GitHub links, because the PDF travels without the repository.

    It needs pandoc and Edge or Chrome installed locally; they are not project
    dependencies and nothing is installed. It writes only -Output (overwritten on each
    run) and a temporary folder. Run it from the repository root, in PowerShell 7:

        pwsh -File scripts/build_hito1_pdf.ps1

    The page count reads the page objects of the PDF that the browser writes; it was
    compared with pdfinfo when the script was written.

.PARAMETER Output
    PDF to write. Default: deliverables/h1/Hito1_BravoFreireGuajanPasquelTorres.pdf.

.PARAMETER Pandoc
    pandoc executable (3.x). Default: the one found in PATH.

.PARAMETER Browser
    Edge or Chrome executable. Default: the first one found in the usual folders.
#>
[CmdletBinding()]
param(
    [string]$Output = 'deliverables/h1/Hito1_BravoFreireGuajanPasquelTorres.pdf',
    [string]$Pandoc = 'pandoc',
    [string]$Browser = ''
)

$ErrorActionPreference = 'Stop'
$repo = (git rev-parse --show-toplevel).Trim()
$source = Join-Path $repo 'docs/requirements/hito1.md'
$css = Join-Path $repo 'scripts/hito1-pdf.css'
$repoBlob = 'https://github.com/Vladimirjon/ec-gov-procurement-dw/blob/main/docs/'
$maxProfilePages = 3
$maxBodyPages = 6

if (-not $Browser) {
    $candidates = @(
        "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
        "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
        "$env:ProgramFiles\Google\Chrome\Application\chrome.exe"
    )
    $Browser = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (-not $Browser) { throw 'Edge or Chrome not found; pass -Browser.' }
if (-not (Get-Command $Pandoc -ErrorAction SilentlyContinue)) { throw 'pandoc not found; pass -Pandoc.' }

$text = (Get-Content -Raw -Encoding utf8 $source) -replace "`r`n", "`n"
# The checklist at the end is the team's; it may mention the marks and is not in the PDF.
$text = $text.Substring(0, $text.IndexOf('## Criterios de aceptación del hito')).TrimEnd() + "`n"
foreach ($mark in '[VERIFICAR]', '[PENDIENTE]') {
    if ($text.Contains($mark)) { throw "$mark found in the text of the deliverable." }
}
$text = $text.Replace('](../', "]($repoBlob")
$pageBreak = "<div style=`"page-break-after: always`"></div>`n`n"
$annex = $text.IndexOf('## Anexo A')
$part2 = $text.IndexOf('## Parte 2')
if ($annex -lt 0 -or $part2 -lt 0) { throw 'Headings "Parte 2" and "Anexo A" not found.' }

$work = Join-Path ([IO.Path]::GetTempPath()) ("hito1-pdf-" + [guid]::NewGuid())
New-Item -ItemType Directory $work | Out-Null
Copy-Item $css (Join-Path $work 'hito1-pdf.css')

function Build-Pdf([string]$Markdown, [string]$Name) {
    $md = Join-Path $work "$Name.md"
    $html = Join-Path $work "$Name.html"
    $pdf = Join-Path $work "$Name.pdf"
    [IO.File]::WriteAllText($md, $Markdown, [Text.UTF8Encoding]::new($false))
    Push-Location $work
    try {
        & $Pandoc -f gfm -t html5 --standalone --metadata pagetitle='Hito 1 - Perfil institucional y preguntas de negocio' `
            -c hito1-pdf.css --embed-resources -o $html $md
        if ($LASTEXITCODE -ne 0) { throw 'pandoc failed.' }
    } finally { Pop-Location }
    $profile = Join-Path $work "browser-$Name"
    & $Browser --headless --disable-gpu --no-pdf-header-footer "--user-data-dir=$profile" `
        "--print-to-pdf=$pdf" ([uri]::new($html).AbsoluteUri) 2>&1 | Out-Null
    if (-not (Test-Path $pdf)) { throw "The browser did not write $pdf." }
    return $pdf
}

function Get-PageCount([string]$Pdf) {
    $latin1 = [Text.Encoding]::Latin1.GetString([IO.File]::ReadAllBytes($Pdf))
    return [regex]::Matches($latin1, '/Type\s*/Page(?![a-zA-Z])').Count
}

try {
    # Part 1 alone, then everything before the annexes, then the whole document.
    $profilePages = Get-PageCount (Build-Pdf $text.Substring(0, $part2) 'parte1')
    $bodyPages = Get-PageCount (Build-Pdf $text.Substring(0, $annex) 'cuerpo')
    $full = Build-Pdf ($text.Substring(0, $annex) + $pageBreak + $text.Substring($annex)) 'completo'
    $totalPages = Get-PageCount $full

    Write-Host "Part 1: $profilePages page(s) (limit $maxProfilePages)"
    Write-Host "Before the annexes: $bodyPages page(s) (limit $maxBodyPages)"
    Write-Host "Whole document: $totalPages page(s)"
    if ($profilePages -gt $maxProfilePages) { throw "Part 1 has $profilePages pages; the guide allows $maxProfilePages." }
    if ($bodyPages -gt $maxBodyPages) { throw "The body has $bodyPages pages; the guide allows $maxBodyPages." }

    $target = Join-Path $repo $Output
    New-Item -ItemType Directory -Force (Split-Path $target) | Out-Null
    Copy-Item $full $target -Force
    Write-Host "Written: $target"
} finally {
    Remove-Item -Recurse -Force $work -ErrorAction SilentlyContinue
}
