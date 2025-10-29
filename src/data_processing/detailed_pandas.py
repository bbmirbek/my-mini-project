from pathlib import Path
import json
from src.utils.constants import WB_COMMISSION_RATE, UPSELL_RATE
from src.core.calculations import (
    count_of_sales, sum_of_revenue, sum_of_ekv_commission,
    f_amount_to_be_transfered, f_logistic,
    f_storage_cost, f_penalties_amount, f_receiving_fee, f_ad_spend,
    f_reklama, f_buyout_rate, f_djem, corr1, corr2, corr3
)
from src.utils.io_utils import read_excel
from src.core.currency import rub_to_kgs
import pandas as pd


def build_detailed_report(df_data, df_storage):
    cfg_paths = Path("configs")
    products = {}

    for cfg_path in cfg_paths.rglob("*"):

        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        products = products | data["products"]


    articuls = (
        df_storage["Артикул продавца"]
        .replace("", pd.NA)
        .dropna()
        .unique()
    )

    len_articuls_of_0 = len( 
        (
             df_data["Артикул поставщика"]
             .replace("", pd.NA)
             .dropna()
             .unique()
        )
    )

    sales_qty, revenue_net, revenue_pct, commission_wb, acquiring_fee = [], [], [], [], []
    payout_amount, logistics_cost, logistics_pct, storage_cost, storage_pct_of_own_income = [], [], [], [], []
    storage_pct_of_total, penalties_amount, platform_withholdings, receiving_fee, transferred_to_bank = [], [], [], [], []
    ad_spend,  ad_pct, unit_cost, total_cost, cost_pct = [], [], [], [], [] 
    upsell_fee_5pct, net_profit, net_profit_pct, buyout_rate = [], [], [], []

    for a in articuls:
        articul = a.lower()
        n_sales = count_of_sales(articul, df_data)
        rev_net = sum_of_revenue(articul, df_data)
        ack_sum = sum_of_ekv_commission(articul, df_data)
        to_transfer = f_amount_to_be_transfered(articul, df_data)
        logis = f_logistic(articul, df_data)
        storage = rub_to_kgs(f_storage_cost(a, df_storage))
        penalty = f_penalties_amount(articul, df_data, len_articuls_of_0)
        withholdings = f_djem(df_data) / len(articuls)
        rcv_fee = f_receiving_fee(articul, df_data)
        trf_to_bank = rev_net - (rev_net * WB_COMMISSION_RATE) - ack_sum - logis - storage - penalty - withholdings - rcv_fee
        ads = rub_to_kgs(f_ad_spend(articul, df_reklama))
        cost = products.get(articul, {}).get("unit_price", 0)
        profit = trf_to_bank - ads - (cost * n_sales) - (rev_net * UPSELL_RATE)

        sales_qty.append(n_sales)
        revenue_net.append(rev_net)
        commission_wb.append(rev_net * WB_COMMISSION_RATE)
        acquiring_fee.append(ack_sum)
        payout_amount.append(to_transfer)
        logistics_cost.append(logis)
        storage_cost.append(storage)
        penalties_amount.append(penalty)
        platform_withholdings.append(round(withholdings, 2))
        receiving_fee.append(rcv_fee)
        transferred_to_bank.append(trf_to_bank)
        ad_spend.append(ads)
        unit_cost.append(cost)
        total_cost.append(cost * n_sales)
        upsell_fee_5pct.append(rev_net * UPSELL_RATE)
        net_profit.append(profit)

    for i in range(0, len(articuls)):
        a = articuls[i].lower()

        total_rev = sum(revenue_net)
        total_storage = sum(storage_cost)

        rev_pct = f"{round(revenue_net[i] / total_rev * 100, 2)}%"
        logic_pct = f"{round(logistics_cost[i] / revenue_net[i] * 100, 2)}%"
        stor_pct_income = f"{round(storage_cost[i] / revenue_net[i] * 100, 2)}%"
        stor_pct_total = f"{round(storage_cost[i] / total_storage * 100, 2)}%"
        ads_pct = f"{round(ad_spend[i] / revenue_net[i] * 100, 2)}%"
        cost_pc = f"{round(total_cost[i] / revenue_net[i] * 100, 2)}%"
        profit_pct = f"{round(net_profit[i]/revenue_net[i] * 100, 2)}%"
        buyout_pct = f"{round(f_buyout_rate(a, df_data), 2)}%"

        revenue_pct.append(rev_pct)
        logistics_pct.append(logic_pct)
        storage_pct_of_own_income.append(stor_pct_income)
        storage_pct_of_total.append(stor_pct_total)
        ad_pct.append(ads_pct)
        cost_pct.append(cost_pc)
        net_profit_pct.append(profit_pct)
        buyout_rate.append(buyout_pct)

    result_df = pd.DataFrame({
        "Артикул поставщика": articuls,
        "Кол-во продаж": sales_qty,
        "Выручка (продажи - возвраты)": revenue_net,
        "Выручка %": revenue_pct,
        "Комиссия WB": commission_wb,
        "Комиссия эквайринга": acquiring_fee,
        "Сумма к перечислению": payout_amount,
        "Логистика": logistics_cost,
        "Логистика %": logistics_pct,
        "Хранение на складе": storage_cost,
        "Хранение % от собственного дохода": storage_pct_of_own_income,
        "Хранение % от всей суммы": storage_pct_of_total,
        "Штрафы": penalties_amount,
        "Джем": platform_withholdings,
        "Приемка товара": receiving_fee,
        "Перечислено банку": transferred_to_bank,
        "Реклама": ad_spend,
        "Реклама %": ad_pct,
        "Себестоимость единицы товара": unit_cost,
        "Общая себестоимость": total_cost,
        "Себестоимость %": cost_pct,
        "Upsell-услуги (5%)": upsell_fee_5pct,
        "Чистая Прибыль": net_profit,
        "Чистая Прибыль %": net_profit_pct,
        "Выкуп": buyout_rate
    })

    corrections = [[-corr1("Добровольная компенсация при возврате", df_data)], 
                   [-corr1("Добровольная компенсация при возврате", df_data)],
                   [-(corr1("Коррекция продаж", df_data)+
                     corr1("Коррекция возвратов", df_data)-
                     corr1("Корректировка эквайринга", df_data))]]

    cnt_up = 0
    cnt_dw = 0
    for articul in articuls:
        a = articul.lower()
        cnt_up += corr2(a, df_data)
        cnt_dw += corr2(a, df_data) + corr3(a, df_data)
    
    Buyout = cnt_up / cnt_dw * 100

    return result_df, corrections, Buyout
