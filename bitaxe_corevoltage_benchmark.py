import requests
import time
import json
import re


# Initialize lists and variables for data and min/max values
core_voltage_data = []
core_voltage_actual_data = []
min_voltage_actual = float('inf')
max_voltage_actual = float('-inf')

def format_time(seconds):
    """Convert seconds into a human-readable format."""
    minutes, seconds = divmod(int(seconds), 60)
    return f"{minutes} min and {seconds} sec" if minutes else f"{seconds} sec"

def get_ip_address():
    """Prompt the user for an IP address and validate it."""
    while True:
        ip_address = input("Enter the IP address of the Bitaxe (e.g., 192.168.2.117): ").strip()
        if validate_ip_address(ip_address):
            return ip_address
        else:
            print("Invalid IP address format. Please enter a valid IP address.")

def validate_ip_address(ip_address):
    """Validate the IP address format."""
    ip_pattern = re.compile(r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
    return re.match(ip_pattern, ip_address) is not None

def get_user_input():
    try:
        ip_address = get_ip_address()
        duration = int(input("Enter the duration for data collection (in minutes): ")) * 60
        interval = int(input("Enter the interval between data samples (in seconds): "))
        if duration <= 0 or interval <= 0:
            raise ValueError("Duration and interval must be positive integers.")
        return ip_address, duration, interval
    except ValueError as e:
        print(f"Invalid input: {e}. Using default values (1 minute, 3 seconds).")
        return "192.168.2.117", 1 * 60, 3  # Default values

def get_data(url):
    """Fetch data from the API."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()
        return data.get('coreVoltage'), data.get('coreVoltageActual')
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None, None

def collect_data(url, duration, interval):
    """Collect data for the given duration and interval."""
    global min_voltage_actual, max_voltage_actual  # Declare global to modify the variables
    core_voltage_data = []
    core_voltage_actual_data = []
    start_time = time.time()
    
    while time.time() - start_time < duration:
        core_voltage, core_voltage_actual = get_data(url)
        if core_voltage is not None and core_voltage_actual is not None:
            core_voltage_data.append(core_voltage)
            core_voltage_actual_data.append(core_voltage_actual)
            # Update min and max voltage actual
            if core_voltage_actual < min_voltage_actual:
                min_voltage_actual = core_voltage_actual
            if core_voltage_actual > max_voltage_actual:
                max_voltage_actual = core_voltage_actual
            elapsed_time = time.time() - start_time
            remaining_samples = total_samples - len(core_voltage_data)
            if remaining_samples % status_update_interval == 0:  # Update based on user input
               formatted_elapsed_time = format_time(elapsed_time)
               print(f"{remaining_samples} samples left to collect. Time elapsed: {formatted_elapsed_time}.")
        time.sleep(interval)

    return core_voltage_data, core_voltage_actual_data

def calculate_summary(core_voltage_data, core_voltage_actual_data):
    """Calculate and print summary of percentage differences."""
    if not core_voltage_data or not core_voltage_actual_data:
        print("No data collected, unable to compute percentage differences.")
        return
    
    percentage_differences = [
        (actual - target) / target * 100 for actual, target in zip(core_voltage_actual_data, core_voltage_data)
    ]

    percentage_below = [p for p in percentage_differences if p < 0]
    percentage_above = [p for p in percentage_differences if p > 0]

    average_percentage_below = (sum(percentage_below) / len(percentage_below)) if percentage_below else 0
    average_percentage_above = (sum(percentage_above) / len(percentage_above)) if percentage_above else 0

    avg_duration_below, avg_duration_above = calculate_duration_percentages(percentage_differences, interval)

    # Calculate actual average voltages
    avg_voltage = sum(core_voltage_data) / len(core_voltage_data)
    avg_voltage_below = avg_voltage * (1 + average_percentage_below / 100)
    avg_voltage_above = avg_voltage * (1 + average_percentage_above / 100)

    # Format the summary text with actual calculated voltage values
    summary_text = (
        f"Core Voltage Actual was on average {abs(average_percentage_below):.2f}% below Core Voltage "
        f"({avg_voltage_below:.3f} V), which corresponds to approximately "
        f"{avg_duration_below:.2f} minutes of the total monitoring period. On average, Core Voltage Actual was "
        f"{average_percentage_above:.2f}% higher than Core Voltage ({avg_voltage_above:.3f} V), "
        f"which corresponds to approximately {avg_duration_above:.2f} minutes of the total monitoring period.\n"
        f"Lowest Core Voltage Actual Spike: {min_voltage_actual:.3f} V\n"
        f"Highest Core Voltage Actual Spike: {max_voltage_actual:.3f} V"
    )

    print("Summary of voltage differences:")
    print(summary_text)
    print("Detailed summary (JSON format):")
    print(json.dumps({
        "Average Percentage below": average_percentage_below,
        "Average_Percentage above": average_percentage_above,
        "Avarage Duration below": avg_duration_below,
        "Avarage Duration above": avg_duration_above,
        "ASIC Voltage Requested": avg_voltage,
        "Avarage Voltage below": avg_voltage_below,
        "Avarage Voltage above": avg_voltage_above,
        "Lowest Voltage measured": min_voltage_actual,
        "Highest Voltage measured": max_voltage_actual
    }, indent=4))

def calculate_duration_percentages(percentage_differences, time_per_sample):
    """Calculate duration corresponding to percentage differences."""
    below_count = len([p for p in percentage_differences if p < 0])
    above_count = len([p for p in percentage_differences if p > 0])

    avg_duration_below = (below_count * time_per_sample) / 60  # Average duration in minutes
    avg_duration_above = (above_count * time_per_sample) / 60  # Average duration in minutes

    return avg_duration_below, avg_duration_above

# Main logic
ip_address, duration, interval = get_user_input()
url = f"http://{ip_address}/api/system/info"
total_samples = duration // interval
status_update_interval = max(1, total_samples // (duration // 60))  # Update status every minute or less

print(f"Starting data collection every {interval} seconds for {duration // 60} minutes.")
print(f"{total_samples} samples to be collected.")
core_voltage_data, core_voltage_actual_data = collect_data(url, duration, interval)
calculate_summary(core_voltage_data, core_voltage_actual_data)
