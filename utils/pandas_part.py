from pathlib import Path
import json
from utils.constants import WB_COMMISSION_RATE, UPSELL_RATE
from utils.calculations import (
    count_of_sales, sum_of_revenue, sum_of_ekv_commission,
    f_amount_to_be_transfered, f_logistic,
    f_warehouse_storage, f_acceptence_of_goods,
    f_sum_of_fine, f_djem, f_ads_wb, f_correction,
    f_correction_sales, f_reklama
)
from utils.io_utils import read_excel
from utils.currency import rub_to_kgs
import pandas as pd


def build_report_dataframe(dt_path):
    """Формирует основной DataFrame с данными из pandas"""

    data_path = dt_path / "0.xlsx"
    df = read_excel(data_path)

    cfg_paths = Path("configs")
    products = {}

    for cfg_path in cfg_paths.rglob("*"):

        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        products = products | data["products"]

    reklama_path = dt_path / "1.xlsx"
    rekl = 0
    if reklama_path.exists():
        df_reklama = read_excel(reklama_path)
        rekl = f_reklama(df_reklama)

    articuls = (
        df["Артикул поставщика"]
        .replace("", pd.NA)
        .dropna()
        .unique()
    )

    fines = (
        df.loc[df["Общая сумма штрафов"] != 0, "Виды логистики, штрафов и корректировок ВВ"]
        .replace("", pd.NA)
        .dropna()
        .unique()
    )


    corrections = [[f_correction(df)], [f_correction_sales(df)], [rekl]]

    warehouse_storage = f_warehouse_storage(df)
    djem = f_djem(df)
    ads_wb = f_ads_wb(df)
#    site_retention = f_site_retention(df)
    acceptence_of_goods = f_acceptence_of_goods(df)
    ads = (rub_to_kgs(rekl)) - ads_wb

    if ads_wb * 0.05 > ads:
        ads = 0
    
    # собираем данные
    sales_qty, revenue_net, commission_wb, acquiring_fee = [], [], [], []
    payout_amount, logistics_cost, unit_cost_of_goods = [], [], []
    total_cost, upsell_fee_5pct, sum_of_fines = [], [], []

    for a in articuls:
        n_sales = count_of_sales(a, df)
        total_rev = sum_of_revenue(a, df)
        ekv_sum = sum_of_ekv_commission(a, df)
        to_transfer = f_amount_to_be_transfered(a, df)
        logis = f_logistic(a, df)
        cost = products.get(a, {}).get("unit_price", 0)

        sales_qty.append(n_sales)
        revenue_net.append(total_rev)
        commission_wb.append(total_rev * WB_COMMISSION_RATE)
        acquiring_fee.append(ekv_sum)
        payout_amount.append(to_transfer)
        logistics_cost.append(logis)
        unit_cost_of_goods.append(cost)
        total_cost.append(cost * n_sales)
        upsell_fee_5pct.append(total_rev * UPSELL_RATE)

    for f in fines:
        fine_sum = f_sum_of_fine(f, df)
        sum_of_fines.append(fine_sum)

    transfered_to_the_bank = (
        sum(payout_amount) - sum(logistics_cost) - warehouse_storage - sum(sum_of_fines) - djem - ads_wb
    )
    net_profit = (
        sum(payout_amount)
        - ads
        - sum(total_cost)
        - sum(logistics_cost)
        - sum(upsell_fee_5pct)
        - warehouse_storage
        - djem
        - ads_wb
        - sum(sum_of_fines)
    )

    # основной блок
    result_df = pd.DataFrame({
        "Артикул поставщика": articuls,
        "Кол-во продаж": sales_qty,
        "Выручка (продажи - возвраты)": revenue_net,
        "Комиссия WB": commission_wb,
        "Комиссия эквайринга": acquiring_fee,
        "Сумма к перечислению": payout_amount,
        "Логистика": logistics_cost
    })

    fines_df = pd.DataFrame({
        "Виды штрафов": fines,
        "Штрафы": sum_of_fines
    })

    summary_df = pd.DataFrame([{
        "Хранение на складе": warehouse_storage,
        "Джем": djem,
        "Реклама со счёта WB": ads_wb,
#        "Удержания площадки (Джем/Реклама)": site_retention,
        "Приемка товара": acceptence_of_goods,
        "Перечислено банку": transfered_to_the_bank,
        "Реклама с собственного счёта": ads
    }])

    pre_last_df = pd.DataFrame({
        "Себестоимость единицы товара": unit_cost_of_goods,
        "Общая себестоимость": total_cost,
        "Upsell-услуги (5%)": upsell_fee_5pct,
    })

    last_df = pd.DataFrame([{
        "Чистая Прибыль": net_profit
    }])

    return result_df, fines_df, summary_df, pre_last_df, last_df, corrections
