# Обнаружение сетевых атак на CIC-IDS2017

Разведочный анализ исправленной версии датасета CIC-IDS2017 и сравнение моделей классического машинного обучения.

## Что в проекте

| Путь | Что это |
|---|---|
| `notebooks/EDA.ipynb` | Разведочный анализ данных |
| `notebooks/extract_tsfresh_features.ipynb` | Извлечение tsfresh из секундных рядов и сохранение матрицы признаков |
| `notebooks/EDA_tsfresh.ipynb` | Статистика всех признаков tsfresh, KDE и боксплоты, сравнение по дням и разметке |
| `notebooks/baseline_models.ipynb` | Сравнение моделей |
| `notebooks/tsfresh_analysis.ipynb` | Признаки секундных рядов и диагностика аномальных минут |

| `notebooks/cic_common.py` | Общий код блокнотов: загрузка данных, русские названия признаков, оформление графиков |
| `data/` | Здесь должен лежать dataset |
| `requirements.txt` | Зависимости с закрепленными версиями |

## Состав проекта

- Python 3.10 или 3.11.
- Около 1 ГБ на диске под окружение и 0,4 ГБ под датасет.
- Оперативная память: `EDA.ipynb` занимает около 5 ГБ. Для `baseline_models.ipynb` пик не измерялся, скорее всего до 16 ГБ.
- Только для macOS: библиотека OpenMP, без неё не загрузятся XGBoost и LightGBM.

  ```bash
  brew install libomp
  ```

## Установка

Команды выполняются из корня проекта.

```bash
python3.11 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Данные

Нужен один файл: `data/CICIDS2017_improved.zip` (328 МБ). Распаковывать его не нужно.

```bash
mkdir -p data
curl -L -o data/CICIDS2017_improved.zip https://intrusion-detection.distrinet-research.be/CNS2022/Datasets/CICIDS2017_improved.zip
```

Страница датасета: https://intrusion-detection.distrinet-research.be/CNS2022/Dataset_Download.html

## Запуск

Блокноты можно открыть в VS Code (выбрать интерпретатор из `.venv`) или в JupyterLab:

```bash
jupyter lab
```

Эксперимент tsfresh использует отдельное окружение.

Для пересчёта признаков откройте [ноутбук извлечения](notebooks/extract_tsfresh_features.ipynb)
в окружении `.venv-tsfresh`. 

```bash
python3.11 -m venv .venv-tsfresh
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-tsfresh.txt
```

После расчёта [EDA](notebooks/EDA_tsfresh.ipynb) загружает `analysis/tsfresh/results/comprehensive_features.csv.gz`.