"""Общий код блокнотов по CIC-IDS2017.

Здесь лежит то, что нужно нескольким блокнотам сразу:
- загрузка данных из архива;
- словарь русских названий признаков;
- оформление графиков и таблиц.
"""
import warnings
from pathlib import Path
from zipfile import ZipFile

import cufflinks as cf
import numpy as np
import pandas as pd
from IPython.display import display

# cufflinks строит графики plotly прямо из таблиц pandas.
# Режим offline: графики рисуются на этом компьютере и никуда не отправляются.
cf.go_offline()
cf.set_config_file(offline=True, world_readable=False, theme="white")

# cufflinks вызывает функции pandas, помеченные как устаревшие. На результат это не влияет,
# поэтому такие предупреждения скрываем.
warnings.filterwarnings("ignore", category=FutureWarning, module="cufflinks")


# ---------------------------------------------------------------------------
# Загрузка данных
# ---------------------------------------------------------------------------

DATA_ARCHIVE = Path(__file__).resolve().parent.parent / "data" / "CICIDS2017_improved.zip"

# Файлы в архиве названы по дням недели. Русское название дня нужно для подписей.
DAY_FILES = {
    "monday.csv": "Понедельник",
    "tuesday.csv": "Вторник",
    "wednesday.csv": "Среда",
    "thursday.csv": "Четверг",
    "friday.csv": "Пятница",
}

ATTEMPTED_SUFFIX = " - Attempted"


def load_dataset(archive_path=DATA_ARCHIVE):
    """Читает все дни из архива в одну таблицу. Распаковывать архив не нужно.

    К колонкам датасета добавляет три свои:
    - Day: день недели;
    - Attack: вид атаки без слова Attempted;
    - Traffic Type: «Норма», «Атака» или «Попытка атаки».
    """
    days = []
    with ZipFile(archive_path) as archive:
        for file_name, day_name in DAY_FILES.items():
            with archive.open(file_name) as csv_file:
                day = pd.read_csv(csv_file, parse_dates=["Timestamp"])
            day["Day"] = day_name
            days.append(day)
    dataset = pd.concat(days, ignore_index=True)
    # Задаём порядок дней, чтобы в таблицах и на графиках они шли с понедельника по пятницу
    dataset["Day"] = pd.Categorical(dataset["Day"], categories=list(DAY_FILES.values()), ordered=True)

    # Метки вида "DoS Hulk - Attempted" авторы датасета ставят потокам, которые относятся к атаке,
    # но вреда не нанесли: например, атакующий не отправил данных или порт был закрыт.
    is_benign = dataset["Label"] == "BENIGN"
    is_attempted = dataset["Label"].str.endswith(ATTEMPTED_SUFFIX)
    dataset["Attack"] = dataset["Label"].str.replace(ATTEMPTED_SUFFIX, "", regex=False)
    dataset["Traffic Type"] = np.select([is_benign, is_attempted], ["Норма", "Попытка атаки"], default="Атака")
    return dataset


# ---------------------------------------------------------------------------
# Русские названия
# ---------------------------------------------------------------------------

# Признаки сгруппированы так же, как в документе docs/Описание атрибутов датасетов CIC.pdf:
# ключ группы повторяет номер пункта из таблицы документа.
# "Вперёд" означает направление от источника к назначению, "обратно" от назначения к источнику.
ATTRIBUTE_GROUPS = {
    "1. Идентификатор потока": {
        "Flow ID": "Идентификатор потока",
    },
    "2. Источник": {
        "Src IP": "IP-адрес источника",
        "Src Port": "Порт источника",
    },
    "3. Назначение": {
        "Dst IP": "IP-адрес назначения",
        "Dst Port": "Порт назначения",
    },
    "4. Протокол": {
        "Protocol": "Протокол",
    },
    "5. Время начала потока": {
        "Timestamp": "Время начала потока",
    },
    "6. Длительность потока": {
        "Flow Duration": "Длительность потока, мкс",
    },
    "7. Число пакетов": {
        "Total Fwd Packet": "Пакетов вперёд",
        "Total Bwd packets": "Пакетов обратно",
    },
    "8. Объём переданных данных": {
        "Total Length of Fwd Packet": "Байт вперёд",
        "Total Length of Bwd Packet": "Байт обратно",
    },
    "9. Размер пакета по направлениям": {
        "Fwd Packet Length Max": "Наибольший размер пакета вперёд, байт",
        "Fwd Packet Length Min": "Наименьший размер пакета вперёд, байт",
        "Fwd Packet Length Mean": "Средний размер пакета вперёд, байт",
        "Fwd Packet Length Std": "Ст. отклонение размера пакета вперёд",
        "Bwd Packet Length Max": "Наибольший размер пакета обратно, байт",
        "Bwd Packet Length Min": "Наименьший размер пакета обратно, байт",
        "Bwd Packet Length Mean": "Средний размер пакета обратно, байт",
        "Bwd Packet Length Std": "Ст. отклонение размера пакета обратно",
    },
    "10. Скорость потока": {
        "Flow Bytes/s": "Байт в секунду",
        "Flow Packets/s": "Пакетов в секунду",
    },
    "11. Интервалы между пакетами": {
        "Flow IAT Mean": "Средний интервал между пакетами, мкс",
        "Flow IAT Std": "Ст. отклонение интервала между пакетами",
        "Flow IAT Max": "Наибольший интервал между пакетами, мкс",
        "Flow IAT Min": "Наименьший интервал между пакетами, мкс",
    },
    "12. Интервалы между пакетами по направлениям": {
        "Fwd IAT Total": "Сумма интервалов вперёд, мкс",
        "Fwd IAT Mean": "Средний интервал вперёд, мкс",
        "Fwd IAT Std": "Ст. отклонение интервала вперёд",
        "Fwd IAT Max": "Наибольший интервал вперёд, мкс",
        "Fwd IAT Min": "Наименьший интервал вперёд, мкс",
        "Bwd IAT Total": "Сумма интервалов обратно, мкс",
        "Bwd IAT Mean": "Средний интервал обратно, мкс",
        "Bwd IAT Std": "Ст. отклонение интервала обратно",
        "Bwd IAT Max": "Наибольший интервал обратно, мкс",
        "Bwd IAT Min": "Наименьший интервал обратно, мкс",
    },
    "13. Флаг PSH по направлениям": {
        "Fwd PSH Flags": "Пакетов с флагом PSH вперёд",
        "Bwd PSH Flags": "Пакетов с флагом PSH обратно",
    },
    "14. Флаг URG по направлениям": {
        "Fwd URG Flags": "Пакетов с флагом URG вперёд",
        "Bwd URG Flags": "Пакетов с флагом URG обратно",
    },
    "15. Длина заголовков": {
        "Fwd Header Length": "Длина заголовков вперёд, байт",
        "Bwd Header Length": "Длина заголовков обратно, байт",
    },
    "16. Скорость по направлениям": {
        "Fwd Packets/s": "Пакетов в секунду вперёд",
        "Bwd Packets/s": "Пакетов в секунду обратно",
    },
    "17. Размер пакета без деления на направления": {
        "Packet Length Min": "Наименьший размер пакета, байт",
        "Packet Length Max": "Наибольший размер пакета, байт",
        "Packet Length Mean": "Средний размер пакета, байт",
        "Packet Length Std": "Ст. отклонение размера пакета",
        "Packet Length Variance": "Дисперсия размера пакета",
    },
    "18. Число пакетов с флагами TCP": {
        "FIN Flag Count": "Пакетов с флагом FIN",
        "SYN Flag Count": "Пакетов с флагом SYN",
        "RST Flag Count": "Пакетов с флагом RST",
        "PSH Flag Count": "Пакетов с флагом PSH",
        "ACK Flag Count": "Пакетов с флагом ACK",
        "URG Flag Count": "Пакетов с флагом URG",
    },
    "19. Флаги CWR и ECE": {
        "CWR Flag Count": "Пакетов с флагом CWR",
        "ECE Flag Count": "Пакетов с флагом ECE",
    },
    "20. Отношение обратных пакетов к прямым": {
        "Down/Up Ratio": "Отношение числа пакетов обратно к числу пакетов вперёд",
    },
    "21. Средний размер пакета": {
        "Average Packet Size": "Средний размер пакета в потоке, байт",
    },
    "22. Средний размер сегмента": {
        "Fwd Segment Size Avg": "Средний размер сегмента вперёд, байт",
        "Bwd Segment Size Avg": "Средний размер сегмента обратно, байт",
    },
    "23. Передача блоками": {
        "Fwd Bytes/Bulk Avg": "Байт в блоке вперёд, в среднем",
        "Fwd Packet/Bulk Avg": "Пакетов в блоке вперёд, в среднем",
        "Fwd Bulk Rate Avg": "Скорость передачи блоков вперёд, в среднем",
        "Bwd Bytes/Bulk Avg": "Байт в блоке обратно, в среднем",
        "Bwd Packet/Bulk Avg": "Пакетов в блоке обратно, в среднем",
        "Bwd Bulk Rate Avg": "Скорость передачи блоков обратно, в среднем",
    },
    "24. Подпотоки": {
        "Subflow Fwd Packets": "Пакетов в подпотоке вперёд",
        "Subflow Fwd Bytes": "Байт в подпотоке вперёд",
        "Subflow Bwd Packets": "Пакетов в подпотоке обратно",
        "Subflow Bwd Bytes": "Байт в подпотоке обратно",
    },
    "25. Начальное окно TCP вперёд": {
        "FWD Init Win Bytes": "Начальное окно TCP вперёд, байт",
    },
    "26. Начальное окно TCP обратно": {
        "Bwd Init Win Bytes": "Начальное окно TCP обратно, байт",
    },
    "27. Пакеты с данными": {
        "Fwd Act Data Pkts": "Пакетов с данными вперёд",
    },
    "28. Наименьший размер сегмента": {
        "Fwd Seg Size Min": "Наименьший размер сегмента вперёд, байт",
    },
    "29. Время активности": {
        "Active Mean": "Среднее время активности, мкс",
        "Active Std": "Ст. отклонение времени активности",
        "Active Max": "Наибольшее время активности, мкс",
        "Active Min": "Наименьшее время активности, мкс",
    },
    "30. Время простоя": {
        "Idle Mean": "Среднее время простоя, мкс",
        "Idle Std": "Ст. отклонение времени простоя",
        "Idle Max": "Наибольшее время простоя, мкс",
        "Idle Min": "Наименьшее время простоя, мкс",
    },
    "31. Метка класса": {
        "Label": "Метка",
    },
    "Нет в документе, есть в исправленной версии датасета": {
        "id": "Номер строки в файле дня",
        "Fwd RST Flags": "Пакетов с флагом RST вперёд",
        "Bwd RST Flags": "Пакетов с флагом RST обратно",
        "ICMP Code": "Код ICMP",
        "ICMP Type": "Тип ICMP",
        "Total TCP Flow Time": "Общее время TCP-соединения, мкс",
        "Attempted Category": "Категория попытки атаки",
    },
    "Добавлено при загрузке": {
        "Day": "День недели",
        "Attack": "Вид атаки",
        "Traffic Type": "Тип трафика",
    },
}

# Словарь "колонка -> русское название". Используется во всех подписях.
RU = {
    column: russian_name
    for columns in ATTRIBUTE_GROUPS.values()
    for column, russian_name in columns.items()
}


def label_ru(label):
    """Метка для подписей: 'BENIGN' -> 'Норма', 'DoS Hulk - Attempted' -> 'DoS Hulk (попытка)'.

    Сами названия атак не переводим: это названия программ и приёмов.
    """
    if label == "BENIGN":
        return "Норма"
    return label.replace(ATTEMPTED_SUFFIX, " (попытка)")


def translate(name):
    """Русская подпись для названия колонки или метки. Остальные значения возвращает как есть."""
    if name in RU:
        return RU[name]
    if isinstance(name, str):
        return label_ru(name)
    return name


# ---------------------------------------------------------------------------
# Оформление таблиц и графиков
# ---------------------------------------------------------------------------

BACKGROUND_COLOR = "#fcfcfb"
GRID_COLOR = "#e1e0d9"
AXIS_COLOR = "#c3c2b7"
TEXT_COLOR = "#0b0b0b"

# Основной цвет столбцов и приглушённый серый для того, что служит фоном для сравнения
MAIN_COLOR = "#2a78d6"
MUTED_COLOR = "#c3c2b7"

# Шкала "чем больше, тем темнее" для тепловых карт с долями от 0 до 100%
LIGHT_TO_DARK_BLUE = [[0.0, "#f0efec"], [0.5, "#6da7ec"], [1.0, "#0d366b"]]


def with_spaces(number):
    """Записывает целое число с пробелами между разрядами: 2099976 -> '2 099 976'."""
    return f"{number:,}".replace(",", " ")


def show_table(table, digits=2):
    """Показывает таблицу с русскими названиями признаков и меток и с пробелами между разрядами."""
    table = table.rename(index=translate, columns=translate)
    display(table.style.format(precision=digits, thousands=" ", decimal=",", na_rep=""))


def style(fig, title, x_title=None, y_title=None, height=450):
    """Задаёт графику общий вид: заголовок, подписи осей, шрифт, фон и сетку."""
    top_margin, bottom_margin = 110, 60
    plot_height = height - top_margin - bottom_margin

    fig.update_layout(
        # Заголовок стоит в левом верхнем углу, на 28 пикселей ниже края
        title=dict(
            text=title,
            font=dict(size=17, color=TEXT_COLOR),
            x=0,
            xref="paper",
            y=1 - 28 / height,
            yref="container",
            yanchor="top",
        ),
        # Легенда стоит между заголовком и областью графика, на 26 пикселей выше области
        legend=dict(orientation="h", x=0, y=1 + 26 / plot_height, yanchor="bottom", bgcolor="rgba(0,0,0,0)"),
        height=height,
        margin=dict(l=70, r=30, t=top_margin, b=bottom_margin),
        font=dict(family="system-ui, -apple-system, 'Segoe UI', sans-serif", size=13, color=TEXT_COLOR),
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        separators=", ",  # дробная часть через запятую, разряды через пробел
        bargap=0.35,
        barcornerradius=4,
    )
    # exponentformat="none": числа на осях пишутся полностью, без английских сокращений k и M
    axis_style = dict(
        gridcolor=GRID_COLOR, linecolor=AXIS_COLOR, zeroline=False, automargin=True, exponentformat="none"
    )
    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)
    if x_title:
        fig.update_xaxes(title_text=x_title)
    if y_title:
        fig.update_yaxes(title_text=y_title)
    # cufflinks обводит столбцы рамкой цвета столбца. Заменяем её тонкой рамкой цвета фона:
    # она отделяет друг от друга части составного столбца.
    fig.update_traces(marker_line=dict(color=BACKGROUND_COLOR, width=1), selector=dict(type="bar"))
    return fig
