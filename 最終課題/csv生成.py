import requests
import pandas as pd
from io import StringIO

APP_ID="ff4095938870ab7ae2a558daf701943dd1867069"
URL="https://api.e-stat.go.jp/rest/3.0/app/getSimpleStatsData"
params={
  "appId":APP_ID,"lang":"J","statsDataId":"0003425893",
  "cdTime":"2023000000","cdCat01":"03","cdCat02":"37","cdCat03":"01",
  "cdTab":"33,34,40,42",
  "metaGetFlg":"Y","cntGetFlg":"N","explanationGetFlg":"Y","annotationGetFlg":"Y",
  "sectionHeaderFlg":"1","replaceSpChars":"0",
}

r=requests.get(URL, params=params, timeout=60)
r.raise_for_status()
text=r.text
if text.lstrip().startswith("<"):


    print(text[:2000]); raise SystemExit("CSVではなくXML")

lines=text.splitlines()
i_value = next(i for i,l in enumerate(lines) if l.strip().strip('"')=="VALUE")

csv_text = "\n".join(lines[i_value+1:])  # ヘッダ行から末尾まで
df = pd.read_csv(StringIO(csv_text))

df.to_csv("simple_2023.csv", index=False, encoding="utf-8-sig")
print(df.shape)
print(df.head())
print(df["tab_code"].value_counts())

# 型変換（数値化）
df["cat01_code"] = df["cat01_code"].astype(str).str.zfill(2)
df["cat02_code"] = df["cat02_code"].astype(str).str.zfill(2)
df["cat03_code"] = df["cat03_code"].astype(str).str.zfill(2)
df["value"] = pd.to_numeric(df["value"], errors="coerce")

# tab別に見たいとき（例：tab_codeごとの平均）
print(df.groupby("tab_code")["value"].mean())

import numpy as np
import pandas as pd

# 1) 欠損・型
df = df.replace({"-": np.nan, "X": np.nan})
df["value"] = pd.to_numeric(df["value"], errors="coerce")
df["tab_code"] = df["tab_code"].astype(int)

# 2) コードを文字列化（0埋めは必要なければ削除OK）
for c, n in [("cat01_code",2),("cat02_code",2),("cat03_code",2),
             ("cat04_code",2),("cat05_code",2),("cat06_code",2)]:
    df[c] = df[c].astype(str).str.zfill(n)

# 3) tabを横持ち（1行=属性セット）
keys = ["cat01_code","企業規模_基本","cat02_code","産業分類","cat03_code","性別_基本",
        "cat04_code","年齢階級_基本","cat05_code","学歴_基本８区分（2020年～）",
        "cat06_code","民・公区分","time_code","時間軸（2020～2023）"]

wide = (df.pivot_table(index=keys, columns="tab_code", values="value", aggfunc="first")
          .reset_index()
          .rename(columns={33:"年齢(歳)",34:"勤続年数(年)",40:"所定内給与(千円)",42:"年間賞与(千円)"}))

# 4) 使う列だけ＆保存
wide = wide[keys + ["年齢(歳)","勤続年数(年)","所定内給与(千円)","年間賞与(千円)"]]
wide.to_csv("分析用_整形済み.csv", index=False, encoding="utf-8-sig")

print(wide.shape)
print(wide.head())