# Apple Health Swimming Data Analysis Tool

A Python tool to analyze swimming data from Apple Health export files, providing detailed insights into swimming workouts and set-level performance analysis.

## Features

- **Swimming Workout Extraction**: Automatically filters and extracts swimming activities from Apple Health data
- **Set Analysis**: Analyzes swimming sets based on rest time between laps
- **Performance Metrics**: Calculates pace, SWOLF scores, distance, and time metrics
- **Date Filtering**: Analyze specific dates, months, or years
- **Multiple Output Formats**: Generates both workout summaries and detailed set analysis
- **Stroke Recognition**: Identifies different swimming strokes (Freestyle, Backstroke, Breaststroke, Butterfly, etc.)

## Requirements

- Python 3.7+
- Required packages (install via pip):
  ```bash
  pip install -r requirements.txt
  ```

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/apple-health-swimming-analysis.git
   cd apple-health-swimming-analysis
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Setup

1. **Export Apple Health Data**:
   - Open Apple Health app on your iPhone
   - Go to your profile (top right)
   - Tap "Export All Health Data"
   - Save and extract the ZIP file
   - Place the `export.xml` file in a folder named `apple_health_export`

2. **File Structure**:
   ```
   apple-health-swimming-analysis/
   ├── swimming.py
   ├── requirements.txt
   ├── README.md
   ├── LICENSE
   └── apple_health_export/          # Create this folder
       └── export.xml                # Place your export file here
   ```

## Configuration

Edit the `Config` class in `swimming.py` to customize analysis settings:

```python
class Config:
    # Date filtering (set to None to analyze all dates)
    TARGET_YEAR: Optional[int] = 2025    # Specify year or None
    TARGET_MONTH: Optional[int] = 10     # Specify month or None  
    TARGET_DAY: Optional[int] = 12       # Specify day or None
    
    # Analysis settings
    REST_THRESHOLD_SEC = 30  # Rest time threshold between sets (seconds)
    LAP_DISTANCE_M = 25     # Distance per lap (meters)
    PACE_DISTANCE_M = 50    # Reference distance for pace calculation (meters)
```

## Usage

Run the analysis:
```bash
python swimming.py
```

The tool will generate two CSV files:
- `swimming_summary1.csv`: Overall workout summaries
- `swimming_sets_by_rest.csv`: Detailed set-by-set analysis

## Output Columns

### Workout Summary (`swimming_summary1.csv`)
- `start`: Workout start time
- `end`: Workout end time
- `duration_min`: Total workout duration in minutes
- `distance_m`: Total distance in meters
- `calories_kcal`: Calories burned
- `avg_hr`: Average heart rate

### Set Analysis (`swimming_sets_by_rest.csv`)
- `set_start_time`: When the set started
- `total_time_sec`: Total time for the set in seconds
- `avg_swolf`: Average SWOLF score for the set
- `stroke_combo`: Swimming strokes used in the set
- `lap_count`: Number of laps in the set
- `distance_m`: Total distance of the set in meters
- `pace_sec_per_50m`: Pace per 50 meters in seconds

## Examples

### Analyze All Swimming Data
```python
TARGET_YEAR = None
TARGET_MONTH = None
TARGET_DAY = None
```

### Analyze Specific Month
```python
TARGET_YEAR = 2025
TARGET_MONTH = 10
TARGET_DAY = None
```

### Analyze Specific Day
```python
TARGET_YEAR = 2025
TARGET_MONTH = 10
TARGET_DAY = 12
```

## Understanding SWOLF

SWOLF is a swimming efficiency metric that combines the number of strokes and time for a lap. Lower SWOLF scores indicate better efficiency.

## Troubleshooting

### Common Issues

1. **File not found error**: Ensure `export.xml` is in the `apple_health_export` folder
2. **No swimming data**: Check if your Apple Watch recorded swimming workouts
3. **Empty results**: Verify your date filtering settings

### Error Messages

- `File not found`: Check the path to your export.xml file
- `Failed to load XML file`: Ensure the export.xml file is not corrupted
- `No swimming workouts found`: Check your date filtering or ensure you have swimming data

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this tool.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Apple Health for providing comprehensive health data export
- The swimming community for inspiring detailed performance analysis

---

**Note**: This tool only analyzes data that you have explicitly exported from your own Apple Health app. It does not access or transmit any personal data.