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


def build_report_dataframe():
    """Формирует основной DataFrame с данными из pandas"""

    data_path = Path("data") / "wb_data.xlsx"
    df = read_excel(data_path)

    cfg_path = Path("configs") / "alura.json"
    with open(cfg_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    products = data["products"]

    reklama_path = Path("data") / "wb_rekalama_data.xlsx"
    df_reklama = read_excel(reklama_path)

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

    rekl = f_reklama(df_reklama)

    corrections = [[f_correction(df)], [f_correction_sales(df)], [rekl]]

    warehouse_storage = f_warehouse_storage(df)
    djem = f_djem(df)
    ads_wb = f_ads_wb(df)
#    site_retention = f_site_retention(df)
    acceptence_of_goods = f_acceptence_of_goods(df)
    ads = (rub_to_kgs(rekl)) - djem - ads_wb

    # собираем данные
    number_of_sales, revenue, wb_commission, ekv_commission, \
    amount_to_be_transfered, logistic, unit_cost_of_goods, \
    total_unit_cost, upsell_service, sum_of_fines = [], [], [], [], [], [], [], [], [], []

    for a in articuls:
        n_sales = count_of_sales(a, df)
        total_rev = sum_of_revenue(a, df)
        ekv_sum = sum_of_ekv_commission(a, df)
        to_transfer = f_amount_to_be_transfered(a, df)
        logis = f_logistic(a, df)
        cost = products.get(a, {}).get("unit_price", 0)

        number_of_sales.append(n_sales)
        revenue.append(total_rev)
        wb_commission.append(total_rev * WB_COMMISSION_RATE)
        ekv_commission.append(ekv_sum)
        amount_to_be_transfered.append(to_transfer)
        logistic.append(logis)
        unit_cost_of_goods.append(cost)
        total_unit_cost.append(cost * n_sales)
        upsell_service.append(total_rev * UPSELL_RATE)

    for f in fines:
        fine_sum = f_sum_of_fine(f, df)
        sum_of_fines.append(fine_sum)

    transfered_to_the_bank = (
        sum(amount_to_be_transfered) - sum(logistic) - warehouse_storage - sum(sum_of_fines) - djem - ads_wb
    )
    net_profit = (
        sum(amount_to_be_transfered)
        - ads
        - sum(total_unit_cost)
        - sum(logistic)
        - sum(upsell_service)
        - warehouse_storage
        - djem
        - ads_wb
    )

    # основной блок
    result_df = pd.DataFrame({
        "Артикул поставщика": articuls,
        "Кол-во продаж": number_of_sales,
        "Выручка (продажи - возвраты)": revenue,
        "Комиссия WB": wb_commission,
        "Комиссия эквайринга": ekv_commission,
        "Сумма к перечислению": amount_to_be_transfered,
        "Логистика": logistic
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
        "Общая себестоимость": total_unit_cost,
        "Upsell-услуги (5%)": upsell_service,
    })

    last_df = pd.DataFrame([{
        "Чистая Прибыль": net_profit
    }])

    return result_df, fines_df, summary_df, pre_last_df, last_df, corrections
