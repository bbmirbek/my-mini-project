from utils.pandas_part import build_report_dataframe
from utils.excel_formatting import format_and_save_report
from utils.SecondList import export_cards_png_from_excel
from pathlib import Path

def main():

    data_root = Path("data")    
    reports_root = Path("reports")
    for p in data_root.rglob("*"):
        if (p.suffix == ".xlsx"):
            st = str(p)
            rs = st[5:-7]
            rs = "reports/" + rs
            report_path = Path(rs)
            data_path = Path(st[:-7])
            print(rs, report_path)
            if not report_path.exists():
                report_path.mkdir(parents=True, exist_ok=True)
                result_df, fines_df, summary_df, pre_last_df, last_df, corr = build_report_dataframe(data_path)
                format_and_save_report(result_df, fines_df, summary_df, pre_last_df, last_df, corr, report_path / "report.xlsx")
                export_cards_png_from_excel(rs + "/report.xlsx", rs + "/image_report.png", str(report_path.name))
    

if __name__ == "__main__":
    main()
