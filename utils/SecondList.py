from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib import gridspec

def export_cards_png_from_excel(
    xlsx_path,
    out_png,
    sheet_name="Отчёт",
    # визуальные настройки
    h_gap=0.04, 
    v_gap=0.05,          # было 0.06 → уменьшено в 2 раза
    card_scale=0.86,
    title_fs=9, 
    value_fs=12,
    inner_gap_scale=1.6,
    # заголовок/даты
    title_text="Alura - Еженедельный отчёт",
    date_range_text="06.10.2025 - 12.10.2025",
):
    def fmt_money(v):
        if isinstance(v, (int, float)):
            s = f"{v:,.2f}".replace(",", " ").replace(".", ",")
            return f"{s}"
        return str(v)

    # ---------- читаем totals ----------
    xlsx_path = Path(xlsx_path)
    out_png = Path(out_png)
    print(xlsx_path)
    print(out_png)
    out_png.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_excel(xlsx_path, sheet_name=sheet_name)
    label_col = df.columns[0]
    if "Total:" not in df[label_col].values:
        raise ValueError("Не найдена строка 'Total:' в Excel-файле.")
    totals = df.loc[df[label_col] == "Total:"].iloc[0]

    rev    = float(totals.get("Выручка (продажи - возвраты)", 0) or 0)
    wb     = float(totals.get("Комиссия WB", 0) or 0)
    ekv    = float(totals.get("Комиссия эквайринга", 0) or 0)
    logi   = float(totals.get("Логистика", 0) or 0)
    store  = float(totals.get("Хранение на складе", 0) or 0)
    fines  = float(totals.get("Штрафы", 0) or 0)
    djem   = float(totals.get("Джем", 0) or 0)
    acc    = float(totals.get("Приемка товара", 0) or 0)
    ads    = float(totals.get("Реклама с собственного счёта", 0) or 0) + float(totals.get("Реклама со счёта WB", 0) or 0)
    cogs   = float(totals.get("Общая себестоимость", 0) or 0)
    upsell = float(totals.get("Upsell-услуги (5%)", 0) or 0)
    tobank = float(totals.get("Сумма к перечислению", 0) or 0)
    profit = float(totals.get("Чистая Прибыль", 0) or 0)

    cm = [rev, wb, ekv, logi, store, fines, djem, acc, ads, cogs, upsell]
    comm_total = wb + ekv
    total_exp  = comm_total + logi + store + fines + djem + ads + cogs + upsell + acc

    # ---------- верхняя таблица ----------
    header_cols = [
        "Метрика",
        "Выручка \n(продажи - \nвозвраты)",
        "Комиссия WB",
        "Комиссия \nэквайринга",
        "Логистика",
        "Хранение на \nскладе",
        "Штрафы",
        "Удержания \nплощадки",
        "Приемка \nтовара",
        "Реклама",
        "Общая \nсебестоимость",
        "Upsell-услуги \n(5%)",
    ]

    row_revenue = ["Выручка"] + [
        fmt_money(rev) if i == 1 else "" for i in range(1, len(header_cols))
    ]
    row_commissions = ["Комиссии"] + [
        fmt_money(cm[i - 1]) if i > 1 else ""  for i in range(1, len(cm) + 1)
    ]
    header_df = pd.DataFrame([row_revenue, row_commissions], columns=header_cols)

    # ---------- карточки ----------
    GREY   = "#EDEDED"
    BEIGE  = "#F8E1D2"
    YELLOW = "#F8E79F"
    GREEN  = "#B3D09E"
    RED    = "#F4CCCC"
    GREEN_MAIN = "#8BD15C"
    title_color = "#000000"
    text_color  = "#222222"
    stroke_color = "#BFBFBF"

    rows = [
        [("Выручка", f"{fmt_money(rev)} с", GREEN_MAIN)],
        [("Штрафы", f"{fmt_money(fines)}", GREY),
         ("Логистика", f"{fmt_money(logi)}", GREY),
         ("Хранение", f"{fmt_money(store)}", GREY)],
        [("Приемка", f"{fmt_money(acc)}", GREY),
         ("Комиссия WB и\nэквайринг", f"{fmt_money(comm_total)}", GREY),
         ("Джем", f"{fmt_money(djem)}", GREY)],
        [("Итого к оплате", f"{fmt_money(tobank)}", YELLOW)],
        [("Реклама", f"{fmt_money(ads)}", BEIGE),
         ("Общая себестоимость", f"{fmt_money(cogs)}", BEIGE),
         ("Upsell-услуги (5%)", f"{fmt_money(upsell)}", BEIGE)],
        [("Общие расходы", f"{fmt_money(total_exp)}", RED),
         ("Чистая прибыль", f"{fmt_money(profit)}", GREEN)],
    ]

    # ---------- фигура ----------
    plt.rcParams["font.family"] = "DejaVu Sans"
    fig = plt.figure(figsize=(22, 13))
    gs = gridspec.GridSpec(
        nrows=2, ncols=1,
        height_ratios=[0.25, 0.75],  # раньше 0.35/0.65 → верх стал компактнее
        hspace=-0.15                   # уменьшен зазор между таблицей и карточками
    )
    ax_top = fig.add_subplot(gs[0])
    ax_bot = fig.add_subplot(gs[1])

    # ======= Верх: заголовок + таблица =======
    ax_top.axis("off")

    full_title = f"{title_text} - {date_range_text}"
    ax_top.text(
        0.5, 0.98, full_title,
        ha="center", va="top",
        fontsize=11, fontweight="bold", color=title_color,
        transform=ax_top.transAxes
    )

    # Рисуем таблицу с уменьшенной высотой
    tbl = ax_top.table(
        cellText=header_df.values,
        colLabels=header_df.columns,
        cellLoc="center",
        # ↓↓↓ уменьшили высоту bbox в 2 раза (0.78 → 0.39)
        bbox=[0.02, 0.40, 0.96, 0.39]
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(4)
    # Шапка
    n_cols = header_df.shape[1]
    for c in range(n_cols):
        hcell = tbl[(0, c)]
        hcell.set_text_props(weight="bold")
        hcell.set_facecolor("#D9D9D9")
        hcell.set_edgecolor("#000000")
    # Две строки данных — «Выручка» (r=1) и «Комиссии» (r=2):
    for r in (1, 2):
        for c in range(n_cols):
            cell = tbl[(r, c)]
            cell.set_facecolor("#FFFFFF")
            cell.set_edgecolor("#000000")
            # ↓ уменьшаем высоту в 2 раза
            cell.set_height(cell.get_height() * 0.5)

    # Оформление ячеек
    n_cols = header_df.shape[1]
    for (r, c), cell in tbl.get_celld().items():
        if r == 0:
            cell.set_text_props(weight="bold")
            cell.set_facecolor("#D9D9D9")
        else:
            cell.set_facecolor("#FFFFFF")
        cell.set_edgecolor("#000000")


    # ======= Низ: карточки =======
    ax_bot.set_xlim(0, 1)
    ax_bot.set_ylim(0, 1)
    ax_bot.axis("off")

    n_rows = len(rows)
    max_cols = max(len(r) for r in rows)
    base_row_h = (1.0 - (n_rows + 1) * v_gap) / n_rows
    base_card_w = (1.0 - (max_cols - 1) * h_gap) / max_cols
    row_h  = base_row_h * card_scale
    card_w = base_card_w * card_scale

    TITLE_Y = 0.78
    VALUE_Y = 0.22  # немного выше, чтобы ближе к центру

    for r_idx, row in enumerate(rows):
        strip_top = 1.0 - (r_idx) * (base_row_h + v_gap) - v_gap
        y_bottom  = strip_top - row_h
        cols_in_row = len(row)

        eff_gap = h_gap * inner_gap_scale if cols_in_row > 1 else 0.0
        row_block_w = cols_in_row * card_w + (cols_in_row - 1) * eff_gap

        if row_block_w > 1.0:
            shrink = (1.0 - (cols_in_row - 1) * eff_gap) / (cols_in_row * card_w)
            shrink = max(0.6, min(1.0, shrink))
            card_w_adj = card_w * shrink
            row_block_w = cols_in_row * card_w_adj + (cols_in_row - 1) * eff_gap
        else:
            card_w_adj = card_w
        
        x_left = (1.0 - row_block_w) / 2.0

        for c_idx, (title, value, face) in enumerate(row):
            x = x_left + c_idx * (card_w_adj + eff_gap)
            y = y_bottom

            rect = FancyBboxPatch(
                (x, y), card_w_adj, row_h,
                boxstyle="round,pad=0.02,rounding_size=0.02",
                linewidth=1.2, edgecolor=stroke_color, facecolor=face,
                transform=ax_bot.transAxes,
            )
            ax_bot.add_patch(rect)

            ax_bot.text(
                x + card_w_adj/2, y + row_h * TITLE_Y,
                title, ha="center", va="center",
                fontsize=title_fs, fontweight="bold", color=title_color,
                transform=ax_bot.transAxes,
            )
            ax_bot.text(
                x + card_w_adj/2, y + row_h * VALUE_Y,
                value, ha="center", va="center",
                fontsize=value_fs, fontweight="bold", color=text_color,
                transform=ax_bot.transAxes,
            )

    # ---------- сохраняем ----------
    fig.set_size_inches(8.27, 11.69)  # A4 формат
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"✅ PNG сохранён в формате A4: {out_png}")
