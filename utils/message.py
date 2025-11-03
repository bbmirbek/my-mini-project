import pandas as pd

def write_message(path, xlsx_path, brand, begin_date, end_date, sheet_name = "Отчёт") :

    df = pd.read_excel(xlsx_path, sheet_name=sheet_name)
    label_col = df.columns[0]
    if "Total:" not in df[label_col].values:
        raise ValueError("Не найдена строка 'Total:' в Excel-файле.")
    totals = df.loc[df[label_col] == "Total:"].iloc[0]

    def fmt_money(v):
        if isinstance(v, (int, float)):
            s = f"{v:,.2f}".replace(",", " ").replace(".", ",")
            return f"{s}"
        return str(v)

    rev    = float(totals.get("Выручка (продажи - возвраты)", 0) or 0)
    wb     = float(totals.get("Комиссия WB", 0) or 0)
    ekv    = float(totals.get("Комиссия эквайринга", 0) or 0)
    logi   = float(totals.get("Логистика", 0) or 0)
    store  = float(totals.get("Хранение на складе", 0) or 0)
    fines  = float(totals.get("Штрафы", 0) or 0)
    djem_and_wb   = float(totals.get("Джем", 0) or 0) + float(totals.get("Реклама со счёта WB", 0) or 0)
    acc    = float(totals.get("Приемка товара", 0) or 0)
    ads    = float(totals.get("Реклама с собственного счёта", 0) or 0) 
    cogs   = float(totals.get("Общая себестоимость", 0) or 0)
    upsell = float(totals.get("Upsell-услуги (5%)", 0) or 0)
    profit = float(totals.get("Чистая Прибыль", 0) or 0)

    comm_total = wb + ekv
    total_exp  = comm_total + logi + store + fines + djem_and_wb + ads + cogs + upsell + acc

    with open (path, "w", encoding="utf-8") as file:
        file.write(f'Добрый день, {brand}!\n')
        file.write(f'Отчёт за период {str(begin_date)} - {str(end_date)}:\n')
        file.write(f'Продажи составили: {fmt_money(rev)}\n')
        file.write(f'Общие расходы: {fmt_money(total_exp)}\n')
        file.write(f'Чистая прибыль: {fmt_money(profit)}(значение зависит от цены за единицу товара и может быть неточным)\n')
        file.write(f'Подробная информация по расчётам указана в прикреплённых PDF-файлах.\n')
        file.write(f'С уважением, Upsell team')
