# 実行環境をセットアップする (Windows の PowerShell 用)．
# リポジトリ直下に venv の仮想環境 (.venv) を作り，requirements.txt のパッケージを入れる．
#
# 使い方:
#     powershell -ExecutionPolicy Bypass -File setup.ps1
# 使う Python を変えるときは，-Python か環境変数 PYTHON で指定する．
#     powershell -ExecutionPolicy Bypass -File setup.ps1 -Python py
#
# このファイルは BOM 付きの UTF-8 で保存してある．
# BOM を外すと，Windows PowerShell 5.1 が日本語を読み違える．

param(
    [string]$Python = $(if ($env:PYTHON) { $env:PYTHON } else { "python" })
)

$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$VenvDir = ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

if (-not (Get-Command $Python -ErrorAction SilentlyContinue)) {
    Write-Host "$Python が見つかりません．Python 3 をインストールするか，-Python か環境変数 PYTHON で指定してください．"
    exit 1
}

if (-not (Test-Path $VenvDir)) {
    Write-Host "仮想環境 $VenvDir を作成します ($(& $Python --version))．"
    & $Python -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
    Write-Host "仮想環境 $VenvDir は作成済みです ($(& $VenvPython --version))．"
}

& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $VenvPython -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "セットアップが終わりました．次のコマンドで仮想環境を有効にしてください．"
Write-Host "    $VenvDir\Scripts\Activate.ps1    (PowerShell)"
Write-Host "    $VenvDir\Scripts\activate.bat    (コマンドプロンプト)"
