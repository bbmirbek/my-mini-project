from utils.pandas_part import build_report_dataframe
from utils.excel_formatting import format_and_save_report
from utils.SecondList import export_cards_png_from_excel

def main():
    result_df, fines_df, summary_df, pre_last_df, last_df, corr = build_report_dataframe()
    format_and_save_report(result_df, fines_df, summary_df, pre_last_df, last_df, corr)
    export_cards_png_from_excel()

if __name__ == "__main__":
    main()
