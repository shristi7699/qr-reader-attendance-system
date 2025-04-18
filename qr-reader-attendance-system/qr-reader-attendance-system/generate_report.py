import pandas as pd
from datetime import datetime

csv_file = './attendance.csv'
report_file = './weekly_report.csv'

# Read the attendance CSV file, skipping bad lines or issuing warnings
try:
    df = pd.read_csv(csv_file, on_bad_lines='skip')  # Skip bad lines
except pd.errors.ParserError as e:
    print(f"Error while reading the CSV file: {e}")
    exit(1)

# Filter data for the last 7 days
df['In-Time'] = pd.to_datetime(df['In-Time'], errors='coerce')
df['Out-Time'] = pd.to_datetime(df['Out-Time'], errors='coerce')
last_week = df[df['In-Time'] >= (datetime.now() - pd.Timedelta(days=7))]

# Group by user to calculate summary
summary = last_week.groupby(['Username', 'Name', 'Class']).size().reset_index(name='Attendance Count')

# Save the report
summary.to_csv(report_file, index=False)
print(f"Weekly report saved as {report_file}")
