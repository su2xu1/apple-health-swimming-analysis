"""
Apple Health Swimming Data Analysis Tool

Extracts swimming data from Apple Health export files and 
performs set-level analysis.
"""

import xmltodict
import pandas as pd
from datetime import datetime
import math
from typing import List, Dict, Optional, Any


# ===========================================
# Configuration and Constants
# ===========================================
class Config:
    """Class to manage configuration values"""
    
    # Date filtering settings
    TARGET_YEAR: Optional[int] = None    # Specify year or None
    TARGET_MONTH: Optional[int] = None   # Specify month or None  
    TARGET_DAY: Optional[int] = None     # Specify day or None
    
    # File paths
    EXPORT_XML_PATH = "./apple_health_export/export.xml"
    WORKOUT_SUMMARY_CSV = "swimming_summary1.csv"
    SETS_ANALYSIS_CSV = "swimming_sets_by_rest.csv"
    
    # Set analysis settings
    REST_THRESHOLD_SEC = 30  # Rest time threshold between sets (seconds)
    LAP_DISTANCE_M = 25     # Distance per lap (meters)
    PACE_DISTANCE_M = 50    # Reference distance for pace calculation (meters)


class Constants:
    """Class to manage constant values"""
    
    # Apple Health swimming activity types
    SWIM_ACTIVITIES = {
        'HKWorkoutActivityTypeSwimming',
        'HKWorkoutActivityTypePoolSwimming',
        'HKWorkoutActivityTypeOpenWaterSwimming'
    }
    
    # Stroke type mapping
    STROKE_MAP = {
        '1': 'Mixed',
        '2': 'Freestyle',
        '3': 'Backstroke',
        '4': 'Breaststroke',
        '5': 'Butterfly',
        '6': 'Other/Drill'
    }
    
    # Apple Health metrics identifiers
    DISTANCE_METRIC = 'HKQuantityTypeIdentifierDistanceSwimming'
    ENERGY_METRIC = 'HKQuantityTypeIdentifierActiveEnergyBurned'
    HEART_RATE_METRIC = 'HKQuantityTypeIdentifierHeartRate'
    LAP_EVENT_TYPE = 'HKWorkoutEventTypeLap'
    STROKE_STYLE_KEY = 'HKSwimmingStrokeStyle'
    SWOLF_KEY = 'HKSWOLFScore'


# ===========================================
# Utility Functions
# ===========================================
def filter_by_date(workout_date: datetime) -> bool:
    """Function to filter by specified year, month, and day"""
    if Config.TARGET_YEAR is not None and workout_date.year != Config.TARGET_YEAR:
        return False
    if Config.TARGET_MONTH is not None and workout_date.month != Config.TARGET_MONTH:
        return False
    if Config.TARGET_DAY is not None and workout_date.day != Config.TARGET_DAY:
        return False
    return True


def display_filter_info() -> None:
    """Function to display date filtering information"""
    filter_info = []
    if Config.TARGET_YEAR is not None:
        filter_info.append(f"Year: {Config.TARGET_YEAR}")
    if Config.TARGET_MONTH is not None:
        filter_info.append(f"Month: {Config.TARGET_MONTH}")
    if Config.TARGET_DAY is not None:
        filter_info.append(f"Day: {Config.TARGET_DAY}")

    if filter_info:
        print(f"# Date filtering applied: {', '.join(filter_info)}")
    else:
        print("# Analyzing all dates")


def format_numeric_value(value: float) -> float:
    """Function to format numeric values with floor to 1 decimal place"""
    if pd.notnull(value) and value != float('inf'):
        return math.floor(value * 10) / 10
    return value


# ===========================================
# Data Processing Functions
# ===========================================
def load_health_data(file_path: str) -> Dict[str, Any]:
    """Load Apple Health XML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = xmltodict.parse(file.read())
        print("# XML file loading completed")
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise Exception(f"Failed to load XML file: {e}")


def extract_workout_statistics(workout: Dict[str, Any]) -> Dict[str, Optional[float]]:
    """Extract workout statistics information"""
    stats = workout.get('WorkoutStatistics', [])
    if not isinstance(stats, list):
        stats = [stats]

    distance = None
    energy = None
    heart_rate = None

    for s in stats:
        metric = s.get('@type')
        if metric == Constants.DISTANCE_METRIC:
            distance = float(s.get('@sum', 0))
        elif metric == Constants.ENERGY_METRIC:
            energy = float(s.get('@sum', 0))
        elif metric == Constants.HEART_RATE_METRIC:
            heart_rate = float(s.get('@average', 0))

    return {
        'distance': distance,
        'energy': energy,
        'heart_rate': heart_rate
    }


def process_swim_workouts(raw_workouts: List[Dict[str, Any]]) -> pd.DataFrame:
    """Process swimming workout data"""
    print("# Filtering swimming workouts")
    
    swim_workouts = []
    
    for workout in raw_workouts:
        if workout['@workoutActivityType'] not in Constants.SWIM_ACTIVITIES:
            continue
            
        workout_start = pd.to_datetime(workout['@startDate'])
        
        # Apply date filtering
        if not filter_by_date(workout_start):
            continue
        
        # Extract statistics
        stats = extract_workout_statistics(workout)
        
        swim_workouts.append({
            'start': workout_start,
            'end': pd.to_datetime(workout['@endDate']),
            'duration_min': float(workout.get('@duration', 0)),
            'distance_m': stats['distance'],
            'calories_kcal': stats['energy'],
            'avg_hr': stats['heart_rate']
        })

    return pd.DataFrame(swim_workouts)


def extract_lap_metadata(metadata: List[Dict[str, str]]) -> Dict[str, Any]:
    """Extract lap metadata"""
    if isinstance(metadata, dict):
        metadata = [metadata]
    
    stroke_style = None
    swolf = None
    
    for m in metadata:
        if m.get('@key') == Constants.STROKE_STYLE_KEY:
            stroke_style = Constants.STROKE_MAP.get(
                m['@value'], 
                f"Unknown ({m['@value']})"
            )
        elif m.get('@key') == Constants.SWOLF_KEY:
            swolf = float(m['@value'])
    
    return {
        'stroke_style': stroke_style,
        'swolf': swolf
    }


def process_lap_data(raw_workouts: List[Dict[str, Any]]) -> pd.DataFrame:
    """Process lap-level data"""
    print("# Processing lap data...")
    
    lap_data = []
    
    for workout in raw_workouts:
        if workout.get('@workoutActivityType') not in Constants.SWIM_ACTIVITIES:
            continue
            
        workout_date = workout.get('@startDate')
        workout_start = pd.to_datetime(workout_date)
        
        # Apply date filtering
        if not filter_by_date(workout_start):
            continue
            
        events = workout.get('WorkoutEvent', [])
        if not events:
            continue
        if not isinstance(events, list):
            events = [events]

        for event in events:
            if event.get('@type') != Constants.LAP_EVENT_TYPE:
                continue
                
            duration = float(event.get('@duration', 0))  # in minutes
            timestamp = event.get('@date')
            
            # Extract metadata
            metadata = event.get('MetadataEntry', [])
            lap_metadata = extract_lap_metadata(metadata)
            
            lap_data.append({
                'lap_time_min': duration,
                'stroke_style': lap_metadata['stroke_style'],
                'swolf': lap_metadata['swolf'],
                'lap_start': pd.to_datetime(timestamp)
            })

    return pd.DataFrame(lap_data)


def analyze_swim_sets(lap_df: pd.DataFrame) -> pd.DataFrame:
    """Analyze swim sets based on rest time"""
    print("\n# Executing set analysis based on rest time...")
    
    # Sort by lap start time
    lap_df = lap_df.sort_values(by='lap_start').reset_index(drop=True)
    
    # Calculate time difference from previous lap
    lap_df['lap_start_diff_sec'] = lap_df['lap_start'].diff().dt.total_seconds()
    
    # Mark laps exceeding rest threshold as start of new set
    lap_df['is_new_set'] = lap_df['lap_start_diff_sec'] > Config.REST_THRESHOLD_SEC
    lap_df.loc[lap_df['is_new_set'].isna(), 'is_new_set'] = True
    
    # Assign set IDs
    lap_df['set_id'] = lap_df['is_new_set'].cumsum()
    
    # Aggregate by set
    set_summary = lap_df.groupby('set_id').agg({
        'lap_start': 'first',
        'lap_time_min': 'sum',
        'swolf': 'mean',
        'stroke_style': lambda styles: '/'.join(sorted(set(styles.dropna()))),
        'lap_start_diff_sec': 'count'  # Number of laps
    }).rename(columns={
        'lap_start': 'set_start_time',
        'lap_time_min': 'total_time_sec',
        'swolf': 'avg_swolf',
        'stroke_style': 'stroke_combo',
        'lap_start_diff_sec': 'lap_count'
    })
    
    # Calculate distance and pace
    set_summary['distance_m'] = set_summary['lap_count'] * Config.LAP_DISTANCE_M
    # Convert minutes to seconds
    set_summary['total_time_sec'] = set_summary['total_time_sec'] * 60
    set_summary['pace_sec_per_50m'] = (
        set_summary['total_time_sec'] / (set_summary['distance_m'] / Config.PACE_DISTANCE_M)
    )
    
    return set_summary.reset_index(drop=True)


def format_output_data(set_summary: pd.DataFrame) -> pd.DataFrame:
    """Format output data"""
    print("# Formatting data...")
    
    # Format time by removing timezone
    set_summary['set_start_time'] = set_summary['set_start_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Floor numeric columns to 1 decimal place
    numeric_columns = ['total_time_sec', 'avg_swolf', 'pace_sec_per_50m']
    for col in numeric_columns:
        if col in set_summary.columns:
            set_summary[col] = set_summary[col].apply(format_numeric_value)
    
    return set_summary


def save_results(swim_df: pd.DataFrame, set_summary: pd.DataFrame) -> None:
    """Save results to CSV files"""
    try:
        swim_df.to_csv(Config.WORKOUT_SUMMARY_CSV, index=True)
        set_summary.to_csv(Config.SETS_ANALYSIS_CSV, index=False)
        print(f"# Results saved:")
        print(f"  - Workout summary: {Config.WORKOUT_SUMMARY_CSV}")
        print(f"  - Set analysis: {Config.SETS_ANALYSIS_CSV}")
    except Exception as e:
        print(f"# CSV save error: {e}")


# ===========================================
# Main Execution
# ===========================================
def main():
    """Main execution function"""
    try:
        print("# Starting Apple Health swimming data analysis")
        
        # Display configuration information
        display_filter_info()
        
        # Load XML data
        data = load_health_data(Config.EXPORT_XML_PATH)
        raw_workouts = data['HealthData']['Workout']
        print(f"# Total workouts: {len(raw_workouts)}")
        
        # Process swimming workouts
        swim_df = process_swim_workouts(raw_workouts)
        print(f"# Swimming workouts after filtering: {len(swim_df)}")
        print(swim_df)
        
        # Process lap data
        lap_df = process_lap_data(raw_workouts)
        print(f"# Total laps: {len(lap_df)}")
        
        # Execute set analysis
        set_summary = analyze_swim_sets(lap_df)
        
        # Format data
        set_summary = format_output_data(set_summary)
        
        # Display results
        print("\n🏁 Swim Set Analysis Results (Rest Time Based):")
        print(set_summary)
        
        # Save results
        save_results(swim_df, set_summary)
        
        print("\n# Analysis completed!")
        
    except Exception as e:
        print(f"# Error occurred: {e}")
        raise


if __name__ == "__main__":
    main()