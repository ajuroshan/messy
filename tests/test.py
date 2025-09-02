from datetime import date


# Hostel class should inherit from object, and __init__ should be defined properly
class Hostel:
    def __init__(self):
        self.name = ""


# Create hostel instances
h1 = Hostel()
h1.name = "Swaraj"

h2 = Hostel()
h2.name = "Sagar"


# Messcut class with proper __init__ method
class Messcut:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date


# Function to calculate messcut days based on conditions
def calculate_total_messcut_days(messcuts, hostel):
    total_days = 0
    if hostel.name == "Swaraj":
        for messcut in messcuts:
            days = (messcut.end_date - messcut.start_date).days + 1
            if days == 2:
                total_days += 1
            elif days == 3:
                total_days += 2
            else:
                total_days += days
        return total_days
    else:
        return sum(
            (messcut.end_date - messcut.start_date).days + 1 for messcut in messcuts
        )


# ----- Test -----

# Create some Messcut entries
messcuts = [
    Messcut(date(2025, 8, 1), date(2025, 8, 2)),  # 2 days → +1
    Messcut(date(2025, 8, 5), date(2025, 8, 7)),  # 3 days → +2
    Messcut(date(2025, 8, 10), date(2025, 8, 12)),  # 3 days → +2
    Messcut(date(2025, 8, 15), date(2025, 8, 19)),  # 5 days → +5
]

# Calculate total messcut days for h1 (Swaraj)
total = calculate_total_messcut_days(messcuts, h1)
print("Total messcut days for", h1.name, "=", total)

# If you test for h2 (Sagar), it will return 0
print(
    "Total messcut days for", h2.name, "=", calculate_total_messcut_days(messcuts, h2)
)
