from pathlib import Path
import pandas as pd
import statsmodels.formula.api as smf

HERE = Path(__file__).resolve().parent
csv_path = HERE / "分析用_整形済み.csv"

# 読み込み（同フォルダ基準）
df = pd.read_csv(csv_path, encoding="utf-8-sig")

# 数値化
for c in ["年齢(歳)", "勤続年数(年)", "所定内給与(千円)", "年間賞与(千円)"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# 回帰に使う列に絞って欠損を落とす
use_cols = ["所定内給与(千円)", "年間賞与(千円)", "年齢(歳)", "勤続年数(年)", "学歴_基本８区分（2020年～）"]
df2 = df[use_cols].dropna()

# 1) 学歴別の平均
g = (df2.groupby("学歴_基本８区分（2020年～）")[["所定内給与(千円)", "年間賞与(千円)", "年齢(歳)", "勤続年数(年)"]]
       .mean()
       .sort_values("所定内給与(千円)", ascending=False))
print(g)

# 2) 回帰（学歴はカテゴリ）
f_salary = "Q('所定内給与(千円)') ~ Q('年齢(歳)') + Q('勤続年数(年)') + C(Q('学歴_基本８区分（2020年～）'))"
f_bonus  = "Q('年間賞与(千円)') ~ Q('年齢(歳)') + Q('勤続年数(年)') + C(Q('学歴_基本８区分（2020年～）'))"

m_salary = smf.ols(f_salary, data=df2).fit()
m_bonus  = smf.ols(f_bonus, data=df2).fit()

print(m_salary.summary())
print(m_bonus.summary())

# 3) 係数表
coef = pd.DataFrame({
    "salary_coef": m_salary.params,
    "salary_p": m_salary.pvalues,
    "bonus_coef": m_bonus.params,
    "bonus_p": m_bonus.pvalues,
})
print(coef)

import numpy as np
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import matplotlib as mpl
import matplotlib.pyplot as plt

# 日本語フォント候補（入っているものが自動で使われる）
mpl.rcParams["font.family"] = [
    "Hiragino Sans", "Hiragino Kaku Gothic ProN",  # mac
    "Yu Gothic", "MS Gothic",                       # windows
    "Noto Sans CJK JP", "IPAexGothic", "TakaoGothic" # linux等
]
mpl.rcParams["axes.unicode_minus"] = False  # マイナス記号の文字化け対策

# 学歴の基準を「大学」に固定（説明しやすい）
df2 = df[["所定内給与(千円)","年間賞与(千円)","年齢(歳)","勤続年数(年)","学歴_基本８区分（2020年～）"]].dropna()
df2["学歴_基本８区分（2020年～）"] = df2["学歴_基本８区分（2020年～）"].astype("category")

f_salary = "Q('所定内給与(千円)') ~ Q('年齢(歳)') + Q('勤続年数(年)') + C(Q('学歴_基本８区分（2020年～）'), Treatment(reference='大学'))"
f_bonus  = "Q('年間賞与(千円)') ~ Q('年齢(歳)') + Q('勤続年数(年)') + C(Q('学歴_基本８区分（2020年～）'), Treatment(reference='大学'))"

m_salary = smf.ols(f_salary, data=df2).fit()
m_bonus  = smf.ols(f_bonus, data=df2).fit()

def coef_ci(model, key_prefix):
    s = model.params.filter(like=key_prefix)
    ci = model.conf_int().loc[s.index]
    out = pd.DataFrame({"coef": s, "low": ci[0], "high": ci[1]})
    out.index = [i.split("T.")[-1].rstrip("]") for i in out.index]
    return out.sort_values("coef")

# 1) 学歴差（大学との差）の係数プロット（給与）
sal_ed = coef_ci(m_salary, "C(Q('学歴_基本８区分（2020年～）')")[0:0]  # ダミー: 行を消す用
sal_ed = coef_ci(m_salary, "C(Q('学歴_基本８区分（2020年～）')")

bon_ed = coef_ci(m_bonus,  "C(Q('学歴_基本８区分（2020年～）')")

def plot_coef(df_coef, title, fname):
    y = np.arange(len(df_coef))
    plt.figure(figsize=(7, 4.5))
    plt.hlines(y, df_coef["low"], df_coef["high"], color="black", lw=2)
    plt.plot(df_coef["coef"], y, "o")
    plt.axvline(0, color="gray", lw=1)
    plt.yticks(y, df_coef.index)
    plt.xlabel("大学との差（千円）")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(HERE / fname, dpi=200)
    plt.close()

plot_coef(sal_ed, "学歴差（大学との差）: 所定内給与", "coef_salary_by_edu.png")
plot_coef(bon_ed, "学歴差（大学との差）: 年間賞与", "coef_bonus_by_edu.png")

# 2) 勤続年数の効果（点＋95%CI）
def plot_one(model, var, title, fname):
    coef = model.params[var]
    low, high = model.conf_int().loc[var]
    plt.figure(figsize=(5, 3.5))
    plt.hlines(0, low, high, color="black", lw=3)
    plt.plot(coef, 0, "o")
    plt.axvline(0, color="gray", lw=1)
    plt.yticks([])
    plt.xlabel("効果（千円/年）")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(HERE / fname, dpi=200)
    plt.close()

plot_one(m_salary, "Q('勤続年数(年)')", "勤続年数の効果: 所定内給与", "coef_salary_tenure.png")
plot_one(m_bonus,  "Q('勤続年数(年)')", "勤続年数の効果: 年間賞与", "coef_bonus_tenure.png")

print("saved:",
      "coef_salary_by_edu.png, coef_bonus_by_edu.png, coef_salary_tenure.png, coef_bonus_tenure.png")