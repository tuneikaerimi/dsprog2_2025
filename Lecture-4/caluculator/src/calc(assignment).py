import flet as ft
import math

class CalcButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked, expand=1):
        super().__init__()
        self.text = text
        self.expand = expand
        self.on_click = button_clicked
        self.data = text

class DigitButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):
        CalcButton.__init__(self, text, button_clicked, expand)
        self.bgcolor = ft.Colors.GREY_800 # 例えば暗めの灰色
        self.color = ft.Colors.WHITE

class ActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked)
        self.bgcolor = ft.Colors.ORANGE
        self.color = ft.Colors.WHITE

class ExtraActionButton(CalcButton):
    def __init__(self, text, button_clicked, expand=1):  # expandを追加
        CalcButton.__init__(self, text, button_clicked, expand) # expandを渡す
        self.bgcolor = ft.Colors.BLUE_GREY_700 # 例えば青みがかった灰色
        self.color = ft.Colors.WHITE

class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.reset()

        self.result = ft.Text(value="0", color=ft.Colors.WHITE, size=20)
        self.width = 380
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20

        # レイアウト：元の行に加えて科学計算の行を追加
        self.content = ft.Column(
            controls=[
                ft.Row(controls=[self.result], alignment="end"),

                # 科学計算ボタン行（7つ + 1つ追加）
                ft.Row(
                    controls=[
                        ExtraActionButton(text="√", button_clicked=self.button_clicked),
                        ExtraActionButton(text="|x|", button_clicked=self.button_clicked),
                        ExtraActionButton(text="SIN", button_clicked=self.button_clicked),
                        ExtraActionButton(text="COS", button_clicked=self.button_clicked),
                        ExtraActionButton(text="TAN", button_clicked=self.button_clicked),
                        ExtraActionButton(text="nCr", button_clicked=self.button_clicked),
                        ExtraActionButton(text="nPr", button_clicked=self.button_clicked),
                        ExtraActionButton(text="^", button_clicked=self.button_clicked), # <-- 新しいボタン
                    ],
                    wrap=True,
                ),

                ft.Row(
                    controls=[
                        ExtraActionButton(text="AC", button_clicked=self.button_clicked),
                        ExtraActionButton(text="+/-", button_clicked=self.button_clicked),
                        ExtraActionButton(text="%", button_clicked=self.button_clicked),
                        ActionButton(text="/", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="7", button_clicked=self.button_clicked),
                        DigitButton(text="8", button_clicked=self.button_clicked),
                        DigitButton(text="9", button_clicked=self.button_clicked),
                        ActionButton(text="*", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="4", button_clicked=self.button_clicked),
                        DigitButton(text="5", button_clicked=self.button_clicked),
                        DigitButton(text="6", button_clicked=self.button_clicked),
                        ActionButton(text="-", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="1", button_clicked=self.button_clicked),
                        DigitButton(text="2", button_clicked=self.button_clicked),
                        DigitButton(text="3", button_clicked=self.button_clicked),
                        ActionButton(text="+", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(text="0", expand=2, button_clicked=self.button_clicked),
                        DigitButton(text=".", button_clicked=self.button_clicked),
                        ActionButton(text="=", button_clicked=self.button_clicked),
                    ]
                ),
            ]
        )

    def button_clicked(self, e):
        data = e.control.data
        # print(f"Button clicked with data = {data}") # デバッグ用。必要ならコメント解除

        # ACまたはErrorのリセット
        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"
            self.reset()

        # 数字・小数点の入力
        elif data in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "."):
            if self.result.value == "0" or self.new_operand is True:
                # 最初が小数点なら "0." をセット
                if data == ".":
                    self.result.value = "0."
                else:
                    self.result.value = data
                self.new_operand = False
            else:
                # 小数点は1つまで
                if data == "." and "." in self.result.value:
                    pass
                else:
                    self.result.value = self.result.value + data

        # 四則演算
        elif data in ("+", "-", "*", "/"):
            try:
                self.result.value = self.format_number(float(self.calculate(self.operand1, float(self.result.value), self.operator)))
                self.operator = data
                if self.result.value == "Error":
                    self.operand1 = 0
                else:
                    self.operand1 = float(self.result.value)
                self.new_operand = True
            except Exception:
                self.result.value = "Error"
                self.reset()

        # イコール
        elif data == "=":
            try:
                self.result.value = self.format_number(float(self.calculate(self.operand1, float(self.result.value), self.operator)))
                self.reset()
            except Exception:
                self.result.value = "Error"
                self.reset()

        # パーセント
        elif data == "%":
            try:
                self.result.value = self.format_number(float(self.result.value) / 100)
                self.reset()
            except Exception:
                self.result.value = "Error"
                self.reset()

        # 符号反転
        elif data == "+/-":
            try:
                val = float(self.result.value)
                if val == 0: # 0の符号反転は0のまま
                    pass
                elif val > 0:
                    self.result.value = "-" + str(self.result.value)
                else: # val < 0
                    self.result.value = str(self.format_number(abs(val)))
            except Exception:
                self.result.value = "Error"
                self.reset()

        # --- 科学計算（単項） ---
        elif data == "√":
            try:
                val = float(self.result.value)
                if val < 0:
                    self.result.value = "Error"
                else:
                    self.result.value = self.format_number(math.sqrt(val))
                self.reset()
            except Exception:
                self.result.value = "Error"
                self.reset()

        elif data == "|x|":
            try:
                val = float(self.result.value)
                self.result.value = self.format_number(abs(val))
                self.reset()
            except Exception:
                self.result.value = "Error"
                self.reset()

        elif data == "SIN":
            try:
                deg = float(self.result.value)
                rad = math.radians(deg)
                self.result.value = self.format_number(math.sin(rad))
                self.reset()
            except Exception:
                self.result.value = "Error"
                self.reset()

        elif data == "COS":
            try:
                deg = float(self.result.value)
                rad = math.radians(deg)
                self.result.value = self.format_number(math.cos(rad))
                self.reset()
            except Exception:
                self.result.value = "Error"
                self.reset()

        elif data == "TAN":
            try:
                deg = float(self.result.value)
                # 90 + k*180 近傍は未定義（度で判定）
                k = round((deg - 90) / 180)
                if abs(deg - (90 + 180 * k)) < 1e-12:
                    self.result.value = "Error"
                else:
                    rad = math.radians(deg)
                    self.result.value = self.format_number(math.tan(rad))
                self.reset()
            except Exception:
                self.result.value = "Error"
                self.reset()

        # --- 科学計算（二項：nCr, nPr） ---
        elif data in ("nCr", "nPr"):
            try:
                n = float(self.result.value)
                if not self.is_non_negative_integer(n):
                    self.result.value = "Error"
                    self.reset()
                else:
                    # n を保持して、次は r 入力を待つ
                    self.operand1 = int(n)
                    self.operator = data
                    self.new_operand = True
            except Exception:
                self.result.value = "Error"
                self.reset()

        # --- 科学計算（二項：べき乗 ^） --- # <-- ここに新しい処理を追加
        elif data == "^":
            try:
                self.operand1 = float(self.result.value)
                self.operator = data
                self.new_operand = True
            except Exception:
                self.result.value = "Error"
                self.reset()

        self.update()

    def format_number(self, num):
        try:
            if isinstance(num, float) and num.is_integer():
                return int(num)
            # 非常に小さいが0ではない浮動小数点数を0として扱う例
            if abs(num) < 1e-9: # 例として10^-9より小さい場合は0と見なす
                 return 0
            return num
        except Exception:
            return num

    def is_non_negative_integer(self, x):
        try:
            return float(x).is_integer() and int(x) >= 0
        except Exception:
            return False

    def nCr(self, n, r):
        # 事前条件チェック
        if not (self.is_non_negative_integer(n) and self.is_non_negative_integer(r)):
            return "Error"
        n, r = int(n), int(r)
        if r > n:
            return "Error"
        try:
            # 対称性で小さくする（計算安定化）
            r = min(r, n - r)
            numer = 1
            denom = 1
            for i in range(1, r + 1):
                numer *= (n - r + i)
                denom *= i
            return self.format_number(numer // denom)
        except Exception:
            return "Error"

    def nPr(self, n, r):
        if not (self.is_non_negative_integer(n) and self.is_non_negative_integer(r)):
            return "Error"
        n, r = int(n), int(r)
        if r > n:
            return "Error"
        try:
            # nPr = n*(n-1)*...*(n-r+1)
            result = 1
            for k in range(r):
                result *= (n - k)
            return self.format_number(result)
        except Exception:
            return "Error"

    def calculate(self, operand1, operand2, operator):
        try:
            if operator == "+":
                return self.format_number(operand1 + operand2)
            elif operator == "-":
                return self.format_number(operand1 - operand2)
            elif operator == "*":
                return self.format_number(operand1 * operand2)
            elif operator == "/":
                if operand2 == 0:
                    return "Error"
                else:
                    return self.format_number(operand1 / operand2)
            elif operator == "nCr":
                return self.nCr(operand1, operand2)
            elif operator == "nPr":
                return self.nPr(operand1, operand2)
            elif operator == "^": # <-- ここに新しい処理を追加
                return self.format_number(math.pow(operand1, operand2))
            else:
                # 初期状態や未知演算子の場合は現在値を返す
                return self.format_number(operand2)
        except Exception:
            return "Error"

    def reset(self):
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True

def main(page: ft.Page):
    page.title = "Simple Calculator (Scientific 7)"
    page.bgcolor = ft.Colors.BLACK # ページ全体の背景色を黒に設定
    calc = CalculatorApp()
    page.add(calc)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)