import os
import pandas as pd
import datetime
from models import Facility
from database import db
from sqlalchemy import text

def load_facilities_from_csv(app):
    """Load facilities data from CSV file"""
    csv_path = os.path.join(app.root_path, 'data', 'Health_Facilities.csv')
    if not os.path.exists(csv_path):
        app.logger.warning(f"CSV file not found at {csv_path}")
        return False

    try:
        # Clear existing facilities
        db.session.execute(text('TRUNCATE TABLE health_facilities RESTART IDENTITY CASCADE;'))
        db.session.commit()
        
        # Read CSV file
        data = pd.read_csv(csv_path)
        app.logger.info(f"Found {len(data)} facilities in CSV file")
        
        # Keep track of processed facilities
        added_count = 0
        error_count = 0
        skipped_count = 0
        
        # Process facilities in batches
        batch_size = 500
        facilities_to_add = []
        current_time = datetime.datetime.now()
        
        for _, row in data.iterrows():
            try:
                facility_number = str(row.get('Facility Number', '')).strip()
                if not facility_number:
                    skipped_count += 1
                    continue
                
                # Try to convert latitude and longitude
                try:
                    latitude = float(row['Latitude']) if pd.notna(row.get('Latitude')) else None
                    longitude = float(row['Longitude']) if pd.notna(row.get('Longitude')) else None
                except (ValueError, TypeError) as e:
                    app.logger.warning(f"Invalid coordinates for facility {facility_number}: {e}")
                    latitude = None
                    longitude = None
                
                # Prepare facility data
                facility_data = {
                    'facility_number': facility_number,
                    'facility_name': str(row.get('Facility Name', '')).strip(),
                    'hmis': str(row.get('HMIS', '')).strip(),
                    'province': str(row.get('Province', '')).strip(),
                    'district': str(row.get('District', '')).strip(),
                    'division': str(row.get('Division', '')).strip(),
                    'location': str(row.get('LOCATION', '')).strip(),
                    'sub_location': str(row.get('Sub Location', '')).strip(),
                    'facility_type': str(row.get('Facility Type', '')).strip(),
                    'agency': str(row.get('Agency', '')).strip(),
                    'latitude': latitude,
                    'longitude': longitude,
                    'assigned_service': str(row.get('Assigned Service', '')).strip(),
                    'assigned_insurance': str(row.get('Assigned Insurance', '')).strip(),
                    'created_at': current_time,
                    'updated_at': current_time
                }
                
                # Create new facility
                facilities_to_add.append(Facility(**facility_data))
                added_count += 1
                
                # Process in batches
                if len(facilities_to_add) >= batch_size:
                    try:
                        db.session.bulk_save_objects(facilities_to_add)
                        db.session.commit()
                        facilities_to_add = []
                    except Exception as e:
                        db.session.rollback()
                        error_count += len(facilities_to_add)
                        app.logger.error(f"Error saving batch: {e}")
                        facilities_to_add = []
                    
            except Exception as e:
                error_count += 1
                app.logger.error(f"Error processing facility {facility_number}: {e}")
                continue
        
        # Add any remaining facilities
        if facilities_to_add:
            try:
                db.session.bulk_save_objects(facilities_to_add)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                error_count += len(facilities_to_add)
                app.logger.error(f"Error saving final batch: {e}")
        
        app.logger.info(
            f"Facilities data processed: {added_count} added, "
            f"{error_count} errors, {skipped_count} skipped"
        )
        return True
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error loading facilities data: {e}")
        return False
