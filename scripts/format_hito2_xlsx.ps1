<#
.SYNOPSIS
  Aplica el formato sobrio del Hito 2 al libro de Excel, sin cambiar su contenido.

.DESCRIPTION
  El libro lo genera scripts/build_hito2_xlsx.py solo con la biblioteca estándar; este script
  le da el aspecto del documento del Hito 1 (texto serif, encabezados en negrita con reglas
  horizontales, sin colores de relleno) usando Excel por automatización COM. Requiere Excel
  instalado en Windows. No modifica ningún valor de celda: después de correrlo,
  `python -I scripts/compare_hito2_xlsx_sources.py` debe seguir sin discrepancias.

.EXAMPLE
  pwsh -NoProfile -File scripts/format_hito2_xlsx.ps1 -Path deliverables/h2/Proyecto_Grupo5_Hito2.xlsx
#>
param(
    [Parameter(Mandatory = $true)][string]$Path
)

$ErrorActionPreference = 'Stop'
$full = (Resolve-Path -LiteralPath $Path).Path

$black = 0
$hair = 191 + 191 * 256 + 191 * 65536
$font = 'Times New Roman'
$mono = 'Consolas'
$xlNone = -4142
$xlContinuous = 1
$xlThin = 2
$xlHairline = 1
$edgeTop = 8; $edgeBottom = 9; $insideH = 12

function Clear-Look($ws) {
    $r = $ws.UsedRange
    $r.Interior.ColorIndex = $xlNone
    $r.Borders.LineStyle = $xlNone
    $r.Font.Name = $font
    $r.Font.Size = 10
    $r.Font.Bold = $false
    $r.Font.Italic = $false
    $r.Font.Color = $black
    $r.VerticalAlignment = -4160
    $r.WrapText = $true
    $ws.Cells.FormatConditions.Delete() | Out-Null
    $ws.Tab.ColorIndex = $xlNone
}

function Set-Header($range) {
    $range.Font.Bold = $true
    $range.Interior.ColorIndex = $xlNone
    $range.Borders.Item($edgeTop).LineStyle = $xlContinuous
    $range.Borders.Item($edgeTop).Weight = $xlThin
    $range.Borders.Item($edgeTop).Color = $black
    $range.Borders.Item($edgeBottom).LineStyle = $xlContinuous
    $range.Borders.Item($edgeBottom).Weight = $xlThin
    $range.Borders.Item($edgeBottom).Color = $black
    $range.VerticalAlignment = -4107
    $range.HorizontalAlignment = -4131
}

function Set-Body($range) {
    $range.Borders.Item($insideH).LineStyle = $xlContinuous
    $range.Borders.Item($insideH).Weight = $xlHairline
    $range.Borders.Item($insideH).Color = $hair
    $range.Borders.Item($edgeBottom).LineStyle = $xlContinuous
    $range.Borders.Item($edgeBottom).Weight = $xlThin
    $range.Borders.Item($edgeBottom).Color = $black
}

function Fit-Rows($ws, $pad) {
    $n = $ws.UsedRange.Rows.Count
    for ($r = 1; $r -le $n; $r++) {
        if (-not $ws.Cells.Item($r, 1).MergeCells) {
            $ws.Rows.Item($r).AutoFit() | Out-Null
            $ws.Rows.Item($r).RowHeight = [Math]::Min(409, [Math]::Max(16, $ws.Rows.Item($r).RowHeight * $pad + 7))
        }
    }
}

function Set-Page($xl, $ws, $titleRows) {
    $ps = $ws.PageSetup
    $ps.PaperSize = 9
    $ps.Orientation = 2
    $ps.LeftMargin = $xl.CentimetersToPoints(1.5)
    $ps.RightMargin = $xl.CentimetersToPoints(1.5)
    $ps.TopMargin = $xl.CentimetersToPoints(1.6)
    $ps.BottomMargin = $xl.CentimetersToPoints(1.6)
    $ps.Zoom = $false
    $ps.FitToPagesWide = 1
    $ps.FitToPagesTall = $false
    $ps.RightHeader = '&P'
    $ps.CenterFooter = ''
    if ($titleRows) { $ps.PrintTitleRows = $titleRows }
}

function Text-Of($ws, $r, $c) { return [string]$ws.Cells.Item($r, $c).Text }

$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false
$xl.DisplayAlerts = $false
try {
    $wb = $xl.Workbooks.Open($full)

    # --- Portada -------------------------------------------------------------
    $ws = $wb.Worksheets.Item('Portada')
    Clear-Look $ws
    $ws.Range('A1:C1').Font.Size = 10
    $ws.Range('A1:C1').HorizontalAlignment = -4108
    $ws.Range('A2:C2').Font.Size = 16
    $ws.Range('A2:C2').Font.Bold = $true
    $ws.Range('A2:C2').HorizontalAlignment = -4108
    $ws.Range('A4:A8').Font.Bold = $true
    $ws.Range('B4:C8').HorizontalAlignment = -4131
    $ws.Range('A10:C10').Font.Bold = $true
    $ws.Range('A10:C10').Font.Size = 11
    Set-Header $ws.Range('A11:C11')
    Set-Body $ws.Range('A12:C16')
    $ws.Range('A12:A16').Font.Bold = $true
    $ws.Range('A18:C18').Font.Italic = $true
    $ws.Columns.Item(1).ColumnWidth = 26
    $ws.Columns.Item(2).ColumnWidth = 46
    $ws.Columns.Item(3).ColumnWidth = 62
    Fit-Rows $ws 1.08
    $ws.Rows.Item(1).RowHeight = 20
    $ws.Rows.Item(2).RowHeight = 30
    $ws.Rows.Item(8).RowHeight = 34

    # --- Fuentes -------------------------------------------------------------
    $ws = $wb.Worksheets.Item('Fuentes')
    Clear-Look $ws
    $last = $ws.UsedRange.Rows.Count
    Set-Header $ws.Range("A1:G1")
    Set-Body $ws.Range("A2:G$last")
    $ws.Range("A2:A$last").Font.Bold = $true
    $ws.Range("G2:G$last").Font.Name = $mono
    $ws.Range("G2:G$last").Font.Size = 8
    $ws.Columns.Item(7).ColumnWidth = 40
    Fit-Rows $ws 1.08
    foreach ($rowIndex in 2..$last) {
        $row = $ws.Rows.Item([int]$rowIndex)
        $row.RowHeight = [double]$row.RowHeight + 12.0
    }

    # --- Diccionario ---------------------------------------------------------
    $ws = $wb.Worksheets.Item('Diccionario')
    Clear-Look $ws
    $n = $ws.UsedRange.Rows.Count
    $r = 1
    while ($r -le $n) {
        $a = Text-Of $ws $r 1
        if ($a.StartsWith('Tabla:')) {
            $row = $ws.Range("A${r}:F${r}")
            $row.Font.Bold = $true
            $row.Font.Size = 11
            $row.HorizontalAlignment = -4131
            $r++
            continue
        }
        if ($a -eq 'Campo') {
            Set-Header $ws.Range("A${r}:F${r}")
            $first = $r + 1
            $r++
            while ($r -le $n -and (Text-Of $ws $r 1) -ne '' -and -not (Text-Of $ws $r 1).StartsWith('Tabla:')) { $r++ }
            $lastRow = $r - 1
            if ($lastRow -ge $first) {
                Set-Body $ws.Range("A${first}:F${lastRow}")
                $ws.Range("A${first}:A${lastRow}").Font.Name = $mono
                $ws.Range("A${first}:A${lastRow}").Font.Bold = $true
                $ws.Range("A${first}:A${lastRow}").Font.Size = 9
            }
            continue
        }
        $r++
    }
    Fit-Rows $ws 1.08

    # --- Calidad -------------------------------------------------------------
    $ws = $wb.Worksheets.Item('Calidad')
    Clear-Look $ws
    $n = $ws.UsedRange.Rows.Count
    $ws.Range('A1:F1').Font.Bold = $true
    $ws.Range('A1:F1').Font.Size = 12
    $ws.Range('A1:F1').HorizontalAlignment = -4131
    Set-Header $ws.Range('A2:F2')
    $end = 3
    while ($end -le $n -and (Text-Of $ws $end 1) -ne '') { $end++ }
    $end = $end - 1
    Set-Body $ws.Range("A3:F$end")
    $ws.Range("A3:A$end").Font.Name = $mono
    $ws.Range("A3:B$end").Font.Bold = $true
    for ($i = 3; $i -le $end; $i++) {
        if ((Text-Of $ws $i 1).StartsWith('S-')) { $ws.Range("A${i}:A${i}").Font.Italic = $true }
    }
    $ws.Range("A3:A$end").HorizontalAlignment = -4131
    $ws.Range("C3:C$end").HorizontalAlignment = -4131
    $m = $end + 1
    while ($m -le $n -and -not (Text-Of $ws $m 1).StartsWith('2.')) { $m++ }
    if ($m -le $n) {
        $ws.Range("A${m}:G${m}").Font.Bold = $true
        $ws.Range("A${m}:G${m}").Font.Size = 12
        $ws.Range("A${m}:G${m}").HorizontalAlignment = -4131
        $h = $m + 1
        Set-Header $ws.Range("A${h}:G${h}")
        $b1 = $h + 1; $b2 = $n
        Set-Body $ws.Range("A${b1}:G${b2}")
        $ws.Range("A${b1}:A${b2}").Font.Bold = $true
        $ws.Range("B${b1}:G${b2}").Font.Name = $mono
        $ws.Range("B${b1}:G${b2}").HorizontalAlignment = -4108
        $ws.Range("B${h}:G${h}").HorizontalAlignment = -4108
        for ($i = $b1; $i -le $b2; $i++) {
            for ($c = 2; $c -le 7; $c++) {
                if ((Text-Of $ws $i $c).StartsWith('S-')) { $ws.Cells.Item($i, $c).Font.Italic = $true }
            }
        }
    }
    $ws.Columns.Item(1).ColumnWidth = 24
    Fit-Rows $ws 1.08

    # --- Cobertura -----------------------------------------------------------
    $ws = $wb.Worksheets.Item('Cobertura')
    Clear-Look $ws
    $last = $ws.UsedRange.Rows.Count
    Set-Header $ws.Range('A1:E1')
    Set-Body $ws.Range("A2:E$last")
    $ws.Range("A2:A$last").Font.Bold = $true
    $ws.Range("D2:D$last").Font.Bold = $true
    $ws.Range("D1:D$last").HorizontalAlignment = -4108
    Fit-Rows $ws 1.08

    # --- Vista e impresión ---------------------------------------------------
    $titleRows = @{ 'Portada' = ''; 'Fuentes' = '$1:$1'; 'Diccionario' = ''; 'Calidad' = '$1:$2'; 'Cobertura' = '$1:$1' }
    foreach ($sheet in $wb.Worksheets) {
        $sheet.Activate()
        $xl.ActiveWindow.DisplayGridlines = $false
        $xl.ActiveWindow.FreezePanes = $false
        $xl.ActiveWindow.Zoom = 100
        $xl.ActiveWindow.ScrollRow = 1
        $xl.ActiveWindow.ScrollColumn = 1
        if ($sheet.Name -in @('Fuentes', 'Cobertura')) {
            $sheet.Range('A2').Select()
            $xl.ActiveWindow.FreezePanes = $true
        }
        $sheet.Range('A1').Select()
        Set-Page $xl $sheet $titleRows[$sheet.Name]
    }
    $wb.Worksheets.Item('Portada').Activate()
    $wb.Save()
    $wb.Close($false)
}
finally {
    $xl.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null
}
Write-Output "Formato aplicado a $full"
