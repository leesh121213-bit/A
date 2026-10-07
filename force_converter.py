import tkinter as tk

def convert_kn(kn_value: float):
    """kN 값을 N과 kgf로 변환"""
    newton = kn_value * 1000
    kgf = kn_value * 101.9716
    return newton, kgf

def calculate():
    user_input = entry_value.get().strip()
    try:
        value = float(user_input)
        conversion_to_kn = {'kN': 1, 'N': 0.001, 'kgf': 1 / 101.9716}
        kn_value = value * conversion_to_kn[input_unit.get()]
        if kn_value < 0:
            result_label.config(text="⚠️ 음수는 입력할 수 없습니다.", fg="red")
            return
    except ValueError:
        result_label.config(text="⚠️ 올바른 숫자를 입력하세요.", fg="red")
        return

    newton, kgf = convert_kn(kn_value)
    result_label.config(
        text=f"{value:.4f} {input_unit.get()} = {newton:.4f} N , {kgf:.4f} kgf",
        fg="black"
    )
    history_list.insert(
        tk.END,
        f"{value:.4f} {input_unit.get()} = {newton:.4f} N , {kgf:.4f} kgf"
    )

def on_enter(event):
    calculate()

def add_digit(digit):
    entry_value.insert(tk.END, str(digit))

def backspace_entry():
    if entry_value.get():
        entry_value.delete(len(entry_value.get()) - 1, tk.END)

def clear_entry():
    entry_value.delete(0, tk.END)

# 메인 윈도우 생성
root = tk.Tk()
root.title("kN 변환 계산기")
root.geometry("400x550")
input_unit = tk.StringVar(value="kN")

# 입력창
entry_label = tk.Label(root, text="입력값을 입력하세요:")
entry_label.pack(pady=5)

entry_value = tk.Entry(root, width=25, font=("Arial", 14), justify="right")
entry_value.pack(pady=5)
entry_value.bind("<Return>", on_enter)

# 입력 단위 선택
unit_frame = tk.Frame(root)
unit_frame.pack(pady=5)
tk.Label(unit_frame, text="입력 단위:").pack(side=tk.LEFT)
unit_menu = tk.OptionMenu(unit_frame, input_unit, "kN", "N", "kgf")
unit_menu.pack(side=tk.LEFT)

# 결과 출력 라벨
result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.pack(pady=10)

# 변환 기록
history_label = tk.Label(root, text="변환 기록")
history_label.pack()
history_list = tk.Listbox(root, width=48, height=6)
history_list.pack(pady=5)

# 넘버패드 프레임
pad_frame = tk.Frame(root)
pad_frame.pack()

buttons = [
    ['7','8','9'],
    ['4','5','6'],
    ['1','2','3'],
    ['0','.','⌫'],
    ['C']
]

for r, row in enumerate(buttons):
    for c, char in enumerate(row):
        if char == 'C':
            btn = tk.Button(pad_frame, text=char, width=5, height=2, command=clear_entry)
        elif char == '⌫':
            btn = tk.Button(pad_frame, text=char, width=5, height=2, command=backspace_entry)
        else:
            btn = tk.Button(pad_frame, text=char, width=5, height=2, command=lambda ch=char: add_digit(ch))
        btn.grid(row=r, column=c, padx=5, pady=5)

# 변환 버튼
convert_button = tk.Button(root, text="변환", command=calculate, width=15, height=2)
convert_button.pack(pady=10)

# GUI 실행
root.mainloop()
