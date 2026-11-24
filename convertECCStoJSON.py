import json
import os
import re
import sys

'''
    テキスト形式の電子捕獲断面積データ(nl 別，単位 10^-16 cm^2)を
    Calc_Populations.py が読み込む ECCS_json/ 以下の JSON に変換する．

    使い方(リポジトリのルートで実行):
        python convertECCStoJSON.py [入力ディレクトリ(default: tmp)] [出力ディレクトリ(default: ECCS_json)]

    出力:
        ECCS_json/{H,He,Li}like/{衝突系}.json
        {
          "iontype": "H" | "He" | "Li",
          "1.5": {"1s": 0.0, "2s": 0.0, ...},   # キーは str(float(衝突エネルギー[keV/u]))
          ...
        }
'''

ATOMIC_NUMBER = {'C': 6, 'N': 7, 'O': 8}
# 捕獲後のイオンの電子数 -> (iontype, nl に付ける内殻電子配置)
IONTYPES = {1: ('H', ''), 2: ('He', '1s'), 3: ('Li', '1s1s')}

TITLE_PATTERN = re.compile(r'([CNO])\^?\(?(\d)\+\)?\s*[-+]\s*(H2|He|H)(?![A-Za-z0-9])')
HEADER_PATTERN = re.compile(r'^.*?\(ke[vV]/u\)')
NL_PATTERN = re.compile(r'^\d[spdfghi]$')


def is_number(token):
    try:
        float(token)
    except ValueError:
        return False
    return True


def parse_file(path):
    '''
        ファイルを読み，[(衝突系 or None, 列名のlist, 行のlist), ...] を返す．
        1つのファイルに複数の衝突系の表が入っていることがある．
        見出しに衝突系が書かれていない表は None にしておき，ファイル名から決める．
    '''
    with open(path, newline='') as f:
        lines = re.split(r'\r\n|\r|\n', f.read())

    tables = []
    pending_system = None
    for linenumber, line in enumerate(lines, 1):
        tokens = line.split()
        if not tokens:
            continue

        if HEADER_PATTERN.match(line.strip()):
            # 列名の行
            rest = HEADER_PATTERN.sub('', line.strip()).split()
            columns = [t for t in rest if not is_number(t)]
            tables.append([pending_system, columns, []])
            pending_system = None
            # 列名の後ろに数値が付いている行がある．どの列の値か分からないので変換には使わない
            stray = rest[len(columns):]
            if stray:
                print('警告 {}:{}: ヘッダ行の末尾の数値を無視しました: {}'.format(path, linenumber, ' '.join(stray)))
            continue

        if is_number(tokens[0]):
            if not tables:
                sys.exit('{}:{}: ヘッダより前にデータ行があります．'.format(path, linenumber))
            if pending_system is not None:
                # 衝突系の見出しの後にヘッダがない表は，直前の表と同じ列とみなす
                print('注意 {}:{}: {}{}+{} の表にヘッダがないため，直前の表の列名を使いました．'.format(
                    path, linenumber, *pending_system))
                tables.append([pending_system, tables[-1][1], []])
                pending_system = None
            columns, rows = tables[-1][1], tables[-1][2]
            if not all(is_number(t) for t in tokens):
                sys.exit('{}:{}: 数値でない値があります．'.format(path, linenumber))
            # 列数 + 1(衝突エネルギー) より短い行(途中で切れている行)は trim_table() で処理する
            width = len(columns) + 1
            if len(tokens) > width:
                sys.exit('{}:{}: 列数がヘッダと合いません(ヘッダ {} 列，データ {} 個)．'.format(
                    path, linenumber, width, len(tokens)))
            rows.append([float(t) for t in tokens])
            continue

        title = TITLE_PATTERN.search(line)
        if title:
            pending_system = title.groups()

    return [t for t in tables if t[2]]


def trim_table(columns, rows, name, source):
    '''
        途中で切れている行を含む表を，全ての行に共通する列までで切り詰める．
            - 切れた行は，値が揃っている最後の殻(主量子数)までを使う．
              殻の途中で切れた分(例: 6s だけある)は，同じ殻の残りが分からないので捨てる．
            - total 列まで届かずに切れた行は，行そのものが壊れているとみなして省略する．
        切り詰めた列名と行を返す．
    '''
    total_index = columns.index('total') if 'total' in columns else None

    kept = []
    usable_counts = []
    for row in rows:
        count = len(row) - 1
        if count < len(columns):
            if total_index is not None and total_index >= count:
                print('警告 {}: {} {} keV/u の行は total 列の前で切れているため省略しました({}/{} 列)．'.format(
                    source, name, row[0], count, len(columns)))
                continue
            # 次の列と主量子数が変わる位置(殻の終わり)まで戻る
            while count > 0 and not (NL_PATTERN.match(columns[count - 1]) and columns[count][0] != columns[count - 1][0]):
                count -= 1
            if count == 0 or not any(NL_PATTERN.match(c) for c in columns[:count]):
                print('警告 {}: {} {} keV/u の行は使える列がないため省略しました．'.format(source, name, row[0]))
                continue
        kept.append(row)
        usable_counts.append(count)

    if not kept:
        sys.exit('{}: {} に変換できる行がありません．'.format(source, name))

    common = min(usable_counts)
    if common < len(columns):
        short = sum(1 for row in kept if len(row) - 1 < len(columns))
        print('注意 {}: {} は {} 行が途中で切れているため，{} までの列に切り詰めました(捨てた列: {})．'.format(
            source, name, short, columns[common - 1], ' '.join(columns[common:])))
    return columns[:common], [row[:common + 1] for row in kept]


def system_from_filename(path):
    '''
        ファイル名が単一の衝突系(例: O7+He.txt)のときだけ衝突系を返す．
    '''
    name = os.path.splitext(os.path.basename(path))[0]
    m = re.match(r'^([CNO])(\d)\+(H2|He|H)$', name)
    return m.groups() if m else None


def convert_table(system, columns, rows, source):
    element, charge, target = system
    electrons = ATOMIC_NUMBER[element] - int(charge) + 1
    if electrons not in IONTYPES:
        sys.exit('{}: {}{}+ は未対応のイオン種です．'.format(source, element, charge))
    iontype, core = IONTYPES[electrons]

    with open('AtomicOrbitDatasets/electron_configuration_{}.txt'.format(iontype)) as f:
        conflist = [i.rstrip('\n') for i in f.readlines() if i.strip()]

    has_total = 'total' in columns
    nls = [c for c in columns if c != 'total']
    for nl in nls:
        if not NL_PATTERN.match(nl):
            sys.exit('{}: 列名 {} を解釈できません．'.format(source, nl))
    confs = [core + nl for nl in nls]
    for conf in confs:
        if conf not in conflist:
            sys.exit('{}: 電子配置 {} が electron_configuration_{}.txt にありません．'.format(source, conf, iontype))
    if len(set(confs)) != len(confs):
        sys.exit('{}: 列名が重複しています．'.format(source))

    # Calc_Populations.py は準位リストの先頭から連続して断面積が入っていることを前提にしているので，
    # データにない低い準位(例: Li-like の 2s, 2p)は 0.0 で埋める．
    last = max(conflist.index(conf) for conf in confs)
    filled = [conf for conf in conflist[:last + 1] if conf not in confs]

    result = {'iontype': iontype}
    deviations = []
    for row in rows:
        energy = str(row[0])
        values = dict(zip(columns, row[1:]))
        if energy in result:
            sys.exit('{}: 衝突エネルギー {} が重複しています．'.format(source, energy))
        result[energy] = {conf: float(values.get(conf[len(core):], 0.0)) if conf in confs else 0.0
                          for conf in conflist[:last + 1]}
        if has_total:
            # total は表にない高い準位への捕獲も含むので，total >= Σnl になるはず
            deviation = values['total'] - sum(result[energy].values())
            deviations.append(deviation)
            if deviation < -1.e-3:
                print('警告 {}: {}{}+{} {} keV/u で nl の和が total を {:.5f} 上回っています．'.format(
                    source, element, charge, target, energy, -deviation))

    name = '{}{}+{}'.format(element, charge, target)
    return name, iontype, result, filled, deviations


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    inputdir = args[0] if len(args) > 0 else 'tmp'
    outputdir = args[1] if len(args) > 1 else 'ECCS_json'

    converted = {}
    for filename in sorted(os.listdir(inputdir)):
        path = os.path.join(inputdir, filename)
        if filename.startswith('.') or not os.path.isfile(path):
            continue
        for system, columns, rows in parse_file(path):
            if system is None:
                system = system_from_filename(path)
            if system is None:
                sys.exit('{}: 衝突系を見出しからもファイル名からも決められない表があります．'.format(path))
            columns, rows = trim_table(columns, rows, '{}{}+{}'.format(*system), path)
            name, iontype, result, filled, deviation = convert_table(system, columns, rows, path)

            if name in converted:
                # 同じ衝突系が複数のファイルに入っている場合，内容が一致するときだけ許す
                if converted[name]['result'] != result:
                    sys.exit('{} のデータが {} と {} で食い違っています．'.format(name, converted[name]['source'], path))
                print('{:<7} {} は {} と同一のため省略'.format(name, path, converted[name]['source']))
                continue
            converted[name] = {'result': result, 'source': path, 'iontype': iontype}

            message = '{:<7} {}like  エネルギー {:>2} 点  nl {:>2} 個'.format(
                name, iontype, len(result) - 1, len(columns) - ('total' in columns))
            if deviation:
                message += '  total - Σnl = {:+.5f} 〜 {:+.5f}'.format(min(deviation), max(deviation))
            else:
                message += '  total 列なし'
            if filled:
                message += '  0.0 で補完: {}'.format(' '.join(filled))
            print(message)

    for name, item in converted.items():
        directory = os.path.join(outputdir, '{}like'.format(item['iontype']))
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, '{}.json'.format(name)), 'w') as f:
            json.dump(item['result'], f, indent=2)

    print('{} 個の衝突系を {}/ に出力しました．'.format(len(converted), outputdir))


if __name__ == '__main__':
    main()
