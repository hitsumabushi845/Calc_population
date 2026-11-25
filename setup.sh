#!/bin/sh
# 実行環境をセットアップする．
# リポジトリ直下に venv の仮想環境 (.venv) を作り，requirements.txt のパッケージを入れる．
#
# 使い方:
#     ./setup.sh
# 使う Python を変えるときは，環境変数 PYTHON で指定する．
#     PYTHON=python3.12 ./setup.sh

set -eu

cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
VENV_DIR=".venv"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "$PYTHON が見つかりません．Python 3 をインストールするか，環境変数 PYTHON で指定してください．" >&2
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "仮想環境 $VENV_DIR を作成します ($("$PYTHON" --version))．"
    "$PYTHON" -m venv "$VENV_DIR"
else
    echo "仮想環境 $VENV_DIR は作成済みです ($("$VENV_DIR/bin/python" --version))．"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r requirements.txt

echo
echo "セットアップが終わりました．次のコマンドで仮想環境を有効にしてください．"
echo "    source $VENV_DIR/bin/activate        (bash, zsh)"
echo "    source $VENV_DIR/bin/activate.fish   (fish)"
