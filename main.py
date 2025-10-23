from utils.pandas_part import build_report_dataframe
from utils.excel_formatting import format_and_save_report
from utils.SecondList import export_cards_png_from_excel
from utils.detailed_pandas import build_detailed_report
from utils.detailed_excel_fromatting import format_and_save_detailed_report
from utils.currency import rub_to_kgs

from pathlib import Path

def main():
    data_root = Path("data")    
    for p in data_root.rglob("*"):
        parts = p.parts
        if (p.suffix == ".xlsx"):
            company = parts[1]
            st = str(p)
            rs = st[5:-7]
            rs = "reports/" + rs
            report_path = Path(rs)
            data_path = Path(st[:-7])            
            if not report_path.exists():
                report_path.mkdir(parents=True, exist_ok=True)
                result_df, fines_df, summary_df, pre_last_df, last_df, corr = build_report_dataframe(data_path)
                format_and_save_report(result_df, fines_df, summary_df, pre_last_df, last_df, corr, report_path / "report.xlsx")
                export_cards_png_from_excel(rs + "/report.xlsx", rs + "/image_report.png", str(report_path.name), str(company))
                
                detailed_result_df, corr2, Buyout = build_detailed_report(data_path)
                format_and_save_detailed_report(detailed_result_df, corr2, Buyout, report_path / "detailed_report.xlsx")
    

if __name__ == "__main__":
    main()
