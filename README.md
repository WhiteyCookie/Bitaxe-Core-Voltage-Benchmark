# Bitaxe-Core-Voltage-Benchmark

Spend the last couple of hours (by the help of GPT) to create a small python script for benchmarking the core voltage fluctuactions of the Bitaxe.
Its simple and follows users input to create something like this:

Summary of voltage differences:
Core Voltage Actual was on average 0.96% below Core Voltage (1188.447 V), which corresponds to approximately 1.90 minutes of the total monitoring period. On average, Core Voltage Actual was 1.44% higher than Core Voltage (1217.317 V), which corresponds to approximately 0.68 minutes of the total monitoring period.
Lowest Core Voltage Actual Spike: 1167.000 V
Highest Core Voltage Actual Spike: 1239.000 V
Detailed summary (JSON format):
{
    "Average Percentage below": -0.9627192982456146,
    "Average_Percentage above": 1.443089430894309,
    "Avarage Duration below": 1.9,
    "Avarage Duration above": 0.6833333333333333,
    "ASIC Voltage Requested": 1200.0,
    "Avarage Voltage below": 1188.4473684210525,
    "Avarage Voltage above": 1217.3170731707316,
    "Lowest Voltage measured": 1167,
    "Highest Voltage measured": 1239
}

All you need to provide is your bitaxe ip, the duration in minutes and the intveral to fetch the data.

Hope you found this a little bit usefull
