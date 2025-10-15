import requests

def count_of_sales(articul, df):
    sales = len(df[(df["Артикул поставщика"] == articul) & (df["Обоснование для оплаты"] == "Продажа")])
    returns = len(df[(df["Артикул поставщика"] == articul) & (df["Обоснование для оплаты"] == "Возврат")])
    return sales - returns


def sum_of_revenue(articul, df):
    sold = df.loc[(df["Артикул поставщика"] == articul) & (df["Обоснование для оплаты"] == "Продажа"),
                  "Цена розничная с учетом согласованной скидки"].sum()
    refunded = df.loc[(df["Артикул поставщика"] == articul) & (df["Обоснование для оплаты"] == "Возврат"),
                      "Цена розничная с учетом согласованной скидки"].sum()
    return sold - refunded


def sum_of_ekv_commission(articul, df):
    sold = df.loc[(df["Артикул поставщика"] == articul) & (df["Обоснование для оплаты"] == "Продажа"),
                  "Эквайринг/Комиссии за организацию платежей"].sum()
    refunded = df.loc[(df["Артикул поставщика"] == articul) & (df["Обоснование для оплаты"] == "Возврат"),
                      "Эквайринг/Комиссии за организацию платежей"].sum()
    return sold - refunded


def f_amount_to_be_transfered(articul, df):
    sold = df.loc[(df["Артикул поставщика"] == articul) & (df["Обоснование для оплаты"] == "Продажа"),
                  "К перечислению Продавцу за реализованный Товар"].sum()
    refunded = df.loc[(df["Артикул поставщика"] == articul) & (df["Обоснование для оплаты"] == "Возврат"),
                      "К перечислению Продавцу за реализованный Товар"].sum()
    voluntary = df.loc[(df["Артикул поставщика"] == articul) & (
        df["Обоснование для оплаты"] == "Добровольная компенсация при возврате"),
        "К перечислению Продавцу за реализованный Товар"].sum()
    return sold - refunded + voluntary


def f_logistic(articul, df):
    return df.loc[df["Артикул поставщика"] == articul, "Услуги по доставке товара покупателю"].sum()

def f_sum_of_fine(articul, df):
    return df.loc[df["Виды логистики, штрафов и корректировок ВВ"] == articul, "Общая сумма штрафов"].sum()

def f_warehouse_storage(df):
    return df["Хранение"].sum()


def f_djem(df):
    return df.loc[df["Виды логистики, штрафов и корректировок ВВ"] == "Предоставление услуг по подписке «Джем»", "Удержания"].sum()


def f_ads_wb(df):
    return df.loc[df["Виды логистики, штрафов и корректировок ВВ"] == "Оказание услуг «WB Продвижение»", "Удержания"].sum()


def f_site_retention(df):
    return df["Удержания"].sum()


def f_acceptence_of_goods(df):
    return df["Платная приемка"].sum()


def f_correction(df):
    return -df.loc[df["К перечислению Продавцу за реализованный Товар"] == "Добровольная компенсация при возврате", "Услуги по доставке товара покупателю"].sum()


def f_correction_sales(df):
    sold = df.loc[df["К перечислению Продавцу за реализованный Товар"] == "Коррекция продаж", "Услуги по доставке товара покупателю"].sum()

    refunded = df.loc[df["К перечислению Продавцу за реализованный Товар"] == "Коррекция возвратов", "Услуги по доставке товара покупателю"].sum()

    ekv = df.loc[df["К перечислению Продавцу за реализованный Товар"] == "Корректировка эквайринга", "Услуги по доставке товара покупателю"].sum()

    return -(sold + refunded - ekv)

def f_reklama(df):
    return df["Сумма"].sum()