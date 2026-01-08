def calculate_conversion_rate(visitors, buyers):
    # BUG: If visitors is 0, this crashes.
    # We forgot to handle the edge case.
    return (buyers / visitors) * 100

def generate_report(data):
    print("Generating Analytics Report...")
    for day in data:
        rate = calculate_conversion_rate(day['visitors'], day['buyers'])
        print(f"Date: {day['date']}, Conversion: {rate}%")