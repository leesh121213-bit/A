import csv
from pathlib import Path

import matplotlib.pyplot as plt


CSV_PATH = Path(__file__).with_name("load_data.csv")
RESULT_CSV_PATH = Path(__file__).with_name("load_result.csv")
PLOT_PATH = Path(__file__).with_name("stress_plot.png")
AREA_MM2 = 100.0
REFERENCE_STRESS_MPA = 6.0
REQUIRED_COLUMNS = {"time_s", "force_N"}


def _read_load_data(
    csv_path: Path,
) -> tuple[list[tuple[float, float]], list[str], set[int]]:
    with csv_path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None or not REQUIRED_COLUMNS.issubset(reader.fieldnames):
            raise ValueError("CSV 파일에 time_s, force_N 열이 필요합니다.")

        rows = list(reader)

    if not rows:
        raise ValueError("CSV 파일에 데이터가 없습니다.")

    data: list[tuple[float, float]] = []
    invalid_messages: list[str] = []
    invalid_row_numbers: set[int] = set()
    for row_number, row in enumerate(rows, start=2):
        values = {}
        row_is_valid = True
        for column in ("time_s", "force_N"):
            value = row.get(column)
            if value is None or not value.strip():
                invalid_messages.append(
                    f"{row_number}행 {column} 값 '{value or ''}'은(는) 비어 있습니다."
                )
                invalid_row_numbers.add(row_number)
                row_is_valid = False
                continue
            try:
                values[column] = float(value)
            except ValueError:
                invalid_messages.append(
                    f"{row_number}행 {column} 값 '{value}'은(는) 숫자여야 합니다."
                )
                invalid_row_numbers.add(row_number)
                row_is_valid = False

        if row_is_valid:
            data.append((values["time_s"], values["force_N"]))

    return data, invalid_messages, invalid_row_numbers


def read_load_data(csv_path: Path) -> list[tuple[float, float]]:
    data, _, _ = _read_load_data(csv_path)
    if not data:
        raise ValueError("유효한 데이터가 없습니다. 계산을 중단합니다.")
    return data


def analyze_load_data(csv_path: Path) -> tuple[int, float, float]:
    data = read_load_data(csv_path)
    data_count = len(data)
    max_time_s, max_force_N = max(data, key=lambda item: item[1])
    return data_count, max_force_N, max_time_s


def write_load_result(
    data: list[tuple[float, float]],
    result_csv_path: Path,
    area_mm2: float = AREA_MM2,
) -> tuple[float, float]:
    if area_mm2 <= 0:
        raise ValueError("단면적은 0보다 커야 합니다.")

    result_rows = [
        (time_s, force_N, force_N / area_mm2)
        for time_s, force_N in data
    ]

    with result_csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["time_s", "force_N", "stress_MPa"])
        writer.writerows(result_rows)

    max_time_s, _, max_stress_MPa = max(
        result_rows,
        key=lambda item: item[2],
    )
    return max_stress_MPa, max_time_s


def write_stress_plot(
    data: list[tuple[float, float]],
    plot_path: Path,
    area_mm2: float = AREA_MM2,
) -> None:
    if area_mm2 <= 0:
        raise ValueError("단면적은 0보다 커야 합니다.")

    time_values = [time_s for time_s, _ in data]
    stress_values = [force_N / area_mm2 for _, force_N in data]
    max_index = max(range(len(stress_values)), key=stress_values.__getitem__)
    max_time_s = time_values[max_index]
    max_stress_MPa = stress_values[max_index]

    figure, axes = plt.subplots()
    axes.plot(time_values, stress_values, marker="o")
    exceeded_points = [
        (time_s, stress_MPa)
        for time_s, stress_MPa in zip(time_values, stress_values)
        if stress_MPa > REFERENCE_STRESS_MPA
    ]
    if exceeded_points:
        exceeded_time_values, exceeded_stress_values = zip(*exceeded_points)
        axes.scatter(
            exceeded_time_values,
            exceeded_stress_values,
            color="orange",
            zorder=3,
        )
    axes.plot(
        max_time_s,
        max_stress_MPa,
        marker="o",
        color="red",
        markersize=8,
    )
    axes.annotate(
        f"{max_stress_MPa:g} MPa",
        (max_time_s, max_stress_MPa),
        xytext=(8, 8),
        textcoords="offset points",
    )
    axes.set_xlabel("time(s)")
    axes.set_ylabel("stress(MPa)")
    axes.grid(True)
    figure.savefig(plot_path)
    plt.close(figure)


def main() -> None:
    data, invalid_messages, invalid_row_numbers = _read_load_data(CSV_PATH)
    for message in invalid_messages:
        print(f"제외: {message}")

    print(f"제외한 데이터 수: {len(invalid_row_numbers)}개")
    if not data:
        raise ValueError("유효한 데이터가 없어 계산을 중단합니다.")

    data_count = len(data)
    max_time_s, max_force_N = max(data, key=lambda item: item[1])
    max_stress_MPa, max_stress_time_s = write_load_result(
        data,
        RESULT_CSV_PATH,
    )
    write_stress_plot(data, PLOT_PATH)
    reference_exceeded_count = sum(
        force_N / AREA_MM2 > REFERENCE_STRESS_MPA
        for _, force_N in data
    )

    print(f"계산한 데이터 개수: {data_count}개")
    print(f"최대 하중: {max_force_N:g} N")
    print(f"최대 하중 발생 시간: {max_time_s:g} s")
    print(f"최대 응력: {max_stress_MPa:g} MPa")
    print(f"최대 응력 발생 시간: {max_stress_time_s:g} s")
    print(
        f"기준응력({REFERENCE_STRESS_MPA:g} MPa) 초과 데이터 개수: "
        f"{reference_exceeded_count}개"
    )


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        print(f"오류: {error}")
