from app.report.formatter import generate_daily_report

if __name__ == "__main__":
    report = generate_daily_report()
    print(report)