"""
Dummy Data Generator for Agricultural Dashboard
Generates realistic sample data for testing
"""
import requests
import random
import numpy as np
from datetime import datetime, timedelta

API_BASE_URL = "http://localhost:8000/api/v1"
FIELD_ID = "field_001"

def generate_pest_grid(width=50, height=50, create_hotspot=False, crop_types=["wheat", "corn"]):
    """Generate realistic pest grid with count and crop_type per cell.

    Each cell in the grid contains {count: int, crop_type: str}.
    Produces clustered hotspots per crop type, background noise, and multi-crop patterns.

    Args:
        width: Grid width
        height: Grid height
        create_hotspot: Force at least one tight, high-density hotspot
        crop_types: List of crop types to distribute across grid

    Returns:
        2D list where each cell is {count: int, crop_type: str}
    """
    # Initialize empty grid
    grid = [[{"count": 0, "crop_type": "none"} for _ in range(width)] for _ in range(height)]
    
    # Assign crop types to different regions of the field (spatial distribution)
    # This simulates multi-crop fields with different zones
    num_crop_zones = min(len(crop_types), random.randint(1, 3))
    selected_crops = random.sample(crop_types, num_crop_zones)
    
    # Create crop zones (divide field into regions)
    crop_zone_map = {}
    if num_crop_zones == 1:
        crop_zone_map[(0, width, 0, height)] = selected_crops[0]
    elif num_crop_zones == 2:
        # Split horizontally or vertically
        if random.random() < 0.5:
            split = width // 2
            crop_zone_map[(0, split, 0, height)] = selected_crops[0]
            crop_zone_map[(split, width, 0, height)] = selected_crops[1]
        else:
            split = height // 2
            crop_zone_map[(0, width, 0, split)] = selected_crops[0]
            crop_zone_map[(0, width, split, height)] = selected_crops[1]
    else:  # 3 zones
        # Create 3 strips
        if random.random() < 0.5:
            # Horizontal strips
            h1 = height // 3
            h2 = 2 * height // 3
            crop_zone_map[(0, width, 0, h1)] = selected_crops[0]
            crop_zone_map[(0, width, h1, h2)] = selected_crops[1]
            crop_zone_map[(0, width, h2, height)] = selected_crops[2]
        else:
            # Vertical strips
            w1 = width // 3
            w2 = 2 * width // 3
            crop_zone_map[(0, w1, 0, height)] = selected_crops[0]
            crop_zone_map[(w1, w2, 0, height)] = selected_crops[1]
            crop_zone_map[(w2, width, 0, height)] = selected_crops[2]
    
    # Helper to get crop type for a position
    def get_crop_at_position(x, y):
        for (x0, x1, y0, y1), crop in crop_zone_map.items():
            if x0 <= x < x1 and y0 <= y < y1:
                return crop
        return selected_crops[0] if selected_crops else "none"
    
    # Generate pest infestation patterns per crop type
    for crop_type in selected_crops:
        # Decide how many pests for this crop
        base_pests = random.randint(10, 40)
        
        # Create 1-3 hotspots for this crop
        num_hotspots = random.randint(1, 3) if create_hotspot else random.randint(0, 2)
        
        for _ in range(num_hotspots):
            # Find a good center in this crop's zone
            # Pick random zone with this crop
            matching_zones = [(x0,x1,y0,y1) for (x0,x1,y0,y1), c in crop_zone_map.items() if c == crop_type]
            if not matching_zones:
                continue
            zone = random.choice(matching_zones)
            x0, x1, y0, y1 = zone
            
            # Center hotspot within zone
            hx = random.randint(x0 + 5, x1 - 5) if x1 - x0 > 10 else (x0 + x1) // 2
            hy = random.randint(y0 + 5, y1 - 5) if y1 - y0 > 10 else (y0 + y1) // 2
            hotspot_pests = random.randint(20, 40)  # Increased for better hotspots
            spread = random.uniform(1.5, 3.5)  # Tighter spread for denser hotspots
            
            # Distribute pests in hotspot with gaussian
            # Make hotspot cells have 8-15 pests to trigger critical alerts (threshold: 10)
            for _ in range(hotspot_pests):
                px = int(round(np.clip(np.random.normal(hx, spread), x0, x1-1)))
                py = int(round(np.clip(np.random.normal(hy, spread), y0, y1-1)))
                # Higher counts to trigger alerts: 3-6 pests per detection
                count_add = random.randint(3, 6)
                grid[py][px]["count"] += count_add
                grid[py][px]["crop_type"] = crop_type
        
        # Add background pests for this crop across its zones
        bg_pests = random.randint(10, 25)
        for _ in range(bg_pests):
            # Pick a random zone with this crop
            matching_zones = [(x0,x1,y0,y1) for (x0,x1,y0,y1), c in crop_zone_map.items() if c == crop_type]
            if not matching_zones:
                continue
            zone = random.choice(matching_zones)
            x0, x1, y0, y1 = zone
            px = random.randint(x0, x1-1)
            py = random.randint(y0, y1-1)
            count_add = random.randint(1, 2)
            grid[py][px]["count"] += count_add
            grid[py][px]["crop_type"] = crop_type
    
    # Fill crop_type for cells with no pests (assign based on zone)
    for y in range(height):
        for x in range(width):
            if grid[y][x]["count"] == 0:
                grid[y][x]["crop_type"] = get_crop_at_position(x, y)
    
    return grid

def generate_bounding_boxes(count=100, create_hotspot=False):
    """Generate realistic pest bounding boxes.

    Produces clustered hotspots, background noise, occasional widespread outbreaks,
    and border/strip-aligned clusters so heatmaps show clear multi-zone infestations.

    - `count` is the total number of boxes to return.
    - `create_hotspot` forces at least one tight, high-density hotspot.
    """
    boxes = []
    width_m = 50
    height_m = 50

    remaining = max(0, int(count))

    # helper to pick a coordinate with bounds clamped to the field
    def pick_x(low, high):
        low = max(0, int(low))
        high = min(width_m - 1, int(high))
        if low > high:
            return width_m // 2
        return random.randint(low, high)

    def pick_y(low, high):
        low = max(0, int(low))
        high = min(height_m - 1, int(high))
        if low > high:
            return height_m // 2
        return random.randint(low, high)

    # Determine cluster strategy
    # If user asked for create_hotspot, reserve a tight hotspot of 15-25 boxes
    if create_hotspot and remaining > 0:
        hotspot_n = min(remaining, random.randint(15, 25))
        remaining -= hotspot_n
        # choose hotspot center reasonably within field bounds (20%..80% by default)
        hx = pick_x(int(width_m * 0.2), int(width_m * 0.8))
        hy = pick_y(int(height_m * 0.2), int(height_m * 0.8))
        for _ in range(hotspot_n):
            # tight gaussian around center
            x = int(round(np.clip(np.random.normal(hx, 2), 0, width_m-1)))
            y = int(round(np.clip(np.random.normal(hy, 2), 0, height_m-1)))
            w = random.randint(3, 8)
            h = random.randint(3, 8)
            boxes.append([x, y, w, h])

    # Create 1-3 additional clusters (medium density)
    num_clusters = random.choices([1,2,3], weights=[50,35,15])[0]
    cluster_total = int(remaining * random.uniform(0.45, 0.75)) if remaining > 0 else 0
    per_cluster = []
    if num_clusters > 0 and cluster_total > 0:
        # split cluster_total into num_clusters parts
        parts = np.random.multinomial(cluster_total, [1/num_clusters]*num_clusters)
        for n in parts:
            per_cluster.append(int(n))

    for n in per_cluster:
        if n <= 0:
            continue
        # pick cluster center with safe margins (10% padding)
        cx = pick_x(int(width_m * 0.1), int(width_m * 0.9))
        cy = pick_y(int(height_m * 0.1), int(height_m * 0.9))
        # cluster tightness: small -> tight, large -> spread
        spread = random.choice([1.5, 2.5, 3.5])
        for _ in range(n):
            x = int(round(np.clip(np.random.normal(cx, spread), 0, width_m-1)))
            y = int(round(np.clip(np.random.normal(cy, spread), 0, height_m-1)))
            # slightly smaller boxes in clusters
            w = random.randint(3, 10)
            h = random.randint(3, 10)
            boxes.append([x, y, w, h])

    # Remaining are background noise + occasional edge clusters
    remaining = count - len(boxes)
    # occasional outbreak mode: spread many small boxes across several patches
    outbreak = (random.random() < 0.12)
    if outbreak and remaining > 0:
        # create several small patches
        patches = random.randint(3, 6)
        per_patch = max(1, remaining // patches)
        for _ in range(patches):
            px = pick_x(3, width_m-4)
            py = pick_y(3, height_m-4)
            patch_spread = random.randint(3, max(3, min(8, int(min(width_m, height_m)/3))))
            for i in range(per_patch):
                x = int(round(np.clip(np.random.normal(px, patch_spread), 0, width_m-1)))
                y = int(round(np.clip(np.random.normal(py, patch_spread), 0, height_m-1)))
                w = random.randint(2, 8)
                h = random.randint(2, 8)
                boxes.append([x, y, w, h])
        remaining = count - len(boxes)

    # small chance to place border clusters (pests often gather near edges)
    # only create an edge cluster when there are at least a few boxes remaining
    if remaining >= 3 and random.random() < 0.25:
        edge_side = random.choice(['top','bottom','left','right'])
        n_edge = random.randint(3, min(10, remaining))
        for _ in range(n_edge):
            if edge_side in ('top','bottom'):
                x = pick_x(2, width_m-3)
                y = 2 if edge_side=='top' else height_m-2
            else:
                x = 2 if edge_side=='left' else width_m-2
                y = pick_y(2, height_m-3)
            w = random.randint(4, 12)
            h = random.randint(4, 12)
            boxes.append([x + random.randint(-2,2), y + random.randint(-2,2), w, h])
        remaining = count - len(boxes)

    # Fill the rest with background detections (sparser)
    for _ in range(remaining):
        # Background is not uniform - prefer interior but a bit of randomness
        x = int(round(np.clip(np.random.beta(2.0,2.0) * (width_m-1), 0, width_m-1)))
        y = int(round(np.clip(np.random.beta(2.0,2.0) * (height_m-1), 0, height_m-1)))
        w = random.randint(5, 18)
        h = random.randint(5, 18)
        boxes.append([x, y, w, h])

    # Final small jitter to avoid exact integer repetition and ensure in-bounds
    final = []
    for (x,y,w,h) in boxes[:count]:
        x = int(np.clip(int(round(x + random.uniform(-1,1))), 0, width_m-1))
        y = int(np.clip(int(round(y + random.uniform(-1,1))), 0, height_m-1))
        w = int(np.clip(w, 2, 25))
        h = int(np.clip(h, 2, 25))
        final.append([x,y,w,h])

    return final

def generate_canopy_cover(width=100, height=80, create_low_zone=False):
    """Generate realistic canopy coverage grid.

    Approach:
    - Create multi-scale noise (base + low-frequency blobs) and smooth with a small Gaussian-like filter
    - Overlay irrigation strips (rows or columns) to simulate planting/irrigation patterns
    - Add a few stress patches (circular regions with low canopy)
    - Apply edge effects and clamp values to realistic bounds
    """
    # Base canopy coverage (mean) in percent
    base_coverage = random.uniform(60, 75)

    # Create low-frequency random field using normal noise and simple separable blur
    def gaussian_kernel1d(sigma, radius=None):
        if radius is None:
            radius = int(max(1, sigma * 3))
        x = np.arange(-radius, radius+1)
        k = np.exp(-(x**2) / (2 * sigma**2))
        k = k / k.sum()
        return k

    def blur2d(arr, sigma=1.5):
        k = gaussian_kernel1d(sigma)
        # convolve rows
        tmp = np.apply_along_axis(lambda m: np.convolve(m, k, mode='same'), axis=1, arr=arr)
        # convolve cols
        out = np.apply_along_axis(lambda m: np.convolve(m, k, mode='same'), axis=0, arr=tmp)
        return out

    # Multi-octave noise: combine a couple of scales to get realistic blobs
    noise_small = np.random.normal(scale=1.0, size=(height, width))
    noise_med = np.random.normal(scale=1.0, size=(height, width))
    noise_large = np.random.normal(scale=1.0, size=(height, width))

    # Smooth each octave with different sigma
    noise = 0.6 * blur2d(noise_large, sigma=8.0) + 0.3 * blur2d(noise_med, sigma=3.0) + 0.1 * blur2d(noise_small, sigma=1.0)

    # Normalize noise to roughly +/- 12% variation
    nmin, nmax = noise.min(), noise.max()
    if nmax - nmin > 0:
        noise = (noise - (nmin + nmax) / 2.0) / (nmax - nmin)
    noise = noise * 12.0  # scale to +/-12%

    # Irrigation/planting strips: alternating slightly higher coverage bands
    strips = np.zeros((height, width))
    orientation = random.choice(['horizontal', 'vertical'])
    strip_width = random.choice([4, 6, 8, 10])  # meters
    amplitude = random.uniform(2.0, 6.0)  # extra canopy in strips
    offset = random.randint(0, strip_width - 1)
    if orientation == 'horizontal':
        for y in range(height):
            if ((y + offset) // strip_width) % 2 == 0:
                strips[y, :] += amplitude * (0.6 + 0.4 * np.random.rand())
    else:
        for x in range(width):
            if ((x + offset) // strip_width) % 2 == 0:
                strips[:, x] += amplitude * (0.6 + 0.4 * np.random.rand())

    # Start assembling canopy grid
    canopy = np.full((height, width), base_coverage, dtype=float)
    canopy += noise
    canopy += strips

    # Add a few random stress patches (low canopy)
    num_patches = random.choice([1, 2, 2, 3])  # More frequent stress patches
    for _ in range(num_patches):
        px = random.randint(10, width-10)
        py = random.randint(8, height-8)
        radius = random.randint(6, 15)  # Larger stress zones
        depth = random.uniform(15, 35)  # Deeper canopy reduction (was 8-25)
        for y in range(max(0, py-radius), min(height, py+radius)):
            for x in range(max(0, px-radius), min(width, px+radius)):
                d = np.sqrt((x-px)**2 + (y-py)**2)
                if d <= radius:
                    # falloff towards edges of the patch
                    canopy[y, x] -= depth * (1 - (d / radius))

    # Optionally create one large low canopy zone if requested
    if create_low_zone:
        low_x = random.randint(20, width-20)
        low_y = random.randint(15, height-15)
        low_r = random.randint(8, 16)
        for y in range(max(0, low_y-low_r), min(height, low_y+low_r)):
            for x in range(max(0, low_x-low_r), min(width, low_x+low_r)):
                d = np.sqrt((x-low_x)**2 + (y-low_y)**2)
                if d <= low_r:
                    canopy[y, x] -= random.uniform(12, 28) * (1 - d/low_r)

    # Edge effect: slightly lower coverage near borders
    for y in range(height):
        for x in range(width):
            edge_factor = min(x, width-1-x, y, height-1-y) / max(1, min(width, height) / 10)
            canopy[y, x] -= (1 - edge_factor) * random.uniform(0.0, 4.0)

    # Final clamp to realistic bounds
    canopy = np.clip(canopy, 15.0, 95.0)

    # Round and convert to python lists
    grid = [[round(float(canopy[y, x]), 2) for x in range(width)] for y in range(height)]
    return grid

def generate_daily_data(days_back=0):
    """Generate daily data for a specific day"""
    date = datetime.utcnow() - timedelta(days=days_back)
    
    # Vary pest intensity over time (simulate seasonal pattern)
    base_intensity = random.uniform(0.3, 0.7)  # intensity factor for pest distribution
    
    # Create alerts on most days (70% chance for hotspot, 50% for low canopy)
    # This ensures alerts are generated frequently for testing the recommendation system
    create_hotspot = random.random() < 0.7  # Increased from 0.5
    create_low_zone = random.random() < 0.5  # Increased from 0.3
    
    # Available crop types
    crop_types = ["wheat", "corn"]
    
    # Use 50x50 logical grid by default
    width = 50
    height = 50

    data = {
        "field_id": FIELD_ID,
        "pest_grid": generate_pest_grid(width=width, height=height, create_hotspot=create_hotspot, crop_types=crop_types),
        "canopy_cover": generate_canopy_cover(width=width, height=height, create_low_zone=create_low_zone),
        "field_dimensions": {
            "width_m": width,
            "height_m": height,
            "grid_resolution": 1.0
        },
        "timestamp": date.isoformat()
    }
    
    return data

def post_data(endpoint, data):
    """POST data to API"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error posting to {endpoint}: {e}")
        return None

def delete_data(endpoint):
    """DELETE data from API"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        response = requests.delete(url, timeout=10)
        response.raise_for_status()
        return response.json() if response.text else {"status": "success"}
    except requests.exceptions.RequestException as e:
        print(f"❌ Error deleting from {endpoint}: {e}")
        return None

def generate_drone_data():
    """Generate drone status and flight history"""
    try:
        # Generate flight history for the last 30 days
        flights_logged = 0
        
        for days_back in range(30, 0, -1):
            flight_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Simulate flights every 1-3 days
            if random.random() > 0.6:
                duration = random.randint(25, 35)  # minutes
                distance = round(random.uniform(3.5, 6.2), 1)  # km
                battery_used = random.randint(45, 75)  # percentage
                images = random.randint(150, 300)
                status = random.choices(
                    ['success', 'partial', 'failed'],
                    weights=[85, 12, 3]
                )[0]
                
                flight_data = {
                    "date": flight_date.isoformat(),
                    "duration": duration,
                    "distance_covered": distance,
                    "battery_used": battery_used,
                    "images_captured": images,
                    "status": status,
                    "field_id": FIELD_ID
                }
                
                response = post_data("/drone/log-flight", flight_data)
                if response:
                    flights_logged += 1
        
        # Update drone status
        battery_level = random.randint(75, 95)
        drone_status = {
            "battery_level": battery_level,
            "operational_status": "standby" if battery_level > 30 else "charging",
            "health_status": random.choice(["excellent", "good"])
        }
        
        post_data("/drone/update-status?drone_id=drone_001", drone_status)
        
        # Upgrade drone to DJI AGRAS T50 specs (ensures correct model/camera/specs)
        print("   Upgrading drone to DJI AGRAS T50 specifications...")
        try:
            upgrade_url = f"{API_BASE_URL}/drone/upgrade-to-t50?drone_id=drone_001"
            upgrade_response = requests.post(upgrade_url, timeout=10)
            upgrade_response.raise_for_status()
            print("   ✅ Drone upgraded to DJI AGRAS T50")
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️  Could not upgrade drone (may need manual upgrade): {e}")
        
        return {"flights_logged": flights_logged}
    except Exception as e:
        print(f"Error generating drone data: {e}")
        return None

def clear_database():
    """Clear all daily data and alerts from the database"""
    print("\n🗑️  Clearing database...")
    
    # We'll need to call MongoDB directly or use backend endpoints
    # For now, let's try to delete via API if endpoints exist
    # Otherwise, we'll use pymongo to connect directly
    
    try:
        from pymongo import MongoClient
        
        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client["agri_dashboard"]
        
        # Count before deletion
        daily_count = db["daily_data"].count_documents({})
        alert_count = db["alerts"].count_documents({})
        drone_status_count = db["drone_status"].count_documents({})
        flight_records_count = db["flight_records"].count_documents({})
        
        print(f"   Found {daily_count} daily data records")
        print(f"   Found {alert_count} alerts")
        print(f"   Found {drone_status_count} drone status records")
        print(f"   Found {flight_records_count} flight records")
        
        if daily_count > 0 or alert_count > 0 or drone_status_count > 0 or flight_records_count > 0:
            # Delete all daily data
            daily_result = db["daily_data"].delete_many({})
            print(f"   ✅ Deleted {daily_result.deleted_count} daily data records")
            
            # Delete all alerts
            alert_result = db["alerts"].delete_many({})
            print(f"   ✅ Deleted {alert_result.deleted_count} alerts")
            
            # Delete drone status
            drone_result = db["drone_status"].delete_many({})
            print(f"   ✅ Deleted {drone_result.deleted_count} drone status records")
            
            # Delete flight records
            flight_result = db["flight_records"].delete_many({})
            print(f"   ✅ Deleted {flight_result.deleted_count} flight records")
            
            print("   ✅ Database cleared successfully!\n")
        else:
            print("   ℹ️  Database is already empty\n")
        
        client.close()
        return True
        
    except ImportError:
        print("   ⚠️  pymongo not installed. Install with: pip install pymongo")
        print("   Continuing without clearing database...\n")
        return False
    except Exception as e:
        print(f"   ❌ Error clearing database: {e}")
        print("   Continuing without clearing database...\n")
        return False

def prompt_clear_database():
    """Ask user if they want to clear the database"""
    print("\n⚠️  Database Cleanup Options:")
    print("   1. Clear all existing data (daily data + alerts + drone data)")
    print("   2. Keep existing data and add new data")
    print("   3. Cancel operation")
    
    while True:
        try:
            choice = input("\n   Enter your choice (1/2/3): ").strip()
            if choice == "1":
                return True
            elif choice == "2":
                return False
            elif choice == "3":
                print("\n❌ Operation cancelled by user")
                return None
            else:
                print("   ⚠️  Invalid choice. Please enter 1, 2, or 3")
        except KeyboardInterrupt:
            print("\n\n❌ Operation cancelled by user")
            return None

def main():
    print("🌾 Agricultural Dashboard - Dummy Data Generator")
    print("=" * 50)
    print(f"Target API: {API_BASE_URL}")
    print(f"Field ID: {FIELD_ID}\n")
    
    # Check if backend is available
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        response.raise_for_status()
        print("✅ Backend is running")
    except requests.exceptions.RequestException:
        print("❌ Backend is not running!")
        print("   Start it with: docker-compose -f docker-compose.dev.yml up -d")
        return
    
    # Ask user if they want to clear the database
    should_clear = prompt_clear_database()
    
    if should_clear is None:  # User cancelled
        return
    
    if should_clear:
        if not clear_database():
            print("   ⚠️  Warning: Database clearing failed, but continuing with data generation...")
    else:
        print("\n   ℹ️  Keeping existing data. New data will be added/updated.\n")
    
    # Generate data for last 14 days
    print("📊 Generating 14 days of sample data...")
    success_count = 0
    
    for days_back in range(14, -1, -1):  # 14 days ago to today
        data = generate_daily_data(days_back)
        date_str = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        print(f"   📅 {date_str}: ", end="")
        result = post_data("/ingestion/daily", data)
        
        if result:
            pest_count = result["processing_summary"]["pest_count"]
            avg_canopy = result["processing_summary"]["avg_canopy"]
            alerts = result["processing_summary"]["alerts_generated"]
            print(f"✅ Pests: {pest_count}, Canopy: {avg_canopy:.1f}%, Alerts: {alerts}")
            success_count += 1
        else:
            print("❌ Failed")
    
    # Generate drone status and flight history
    print("\n🚁 Generating drone status and flight history...")
    drone_result = generate_drone_data()
    if drone_result:
        print(f"✅ Drone status created with {drone_result['flights_logged']} flight records")
    else:
        print("❌ Drone data generation failed")
    
    print(f"\n{'='*50}")
    print(f"✅ Successfully inserted {success_count}/15 days of data")
    
    # Summary
    print(f"\n📋 Data Summary:")
    print(f"   • Daily Data: {success_count} records")
    print(f"   • Field Config: 1 record")
    print(f"   • Alerts: Generated based on thresholds")
    print(f"   • Drone Status: 1 record with flight history")
    
    print(f"\n🔗 Next Steps:")
    print(f"   1. View API Docs: http://localhost:8000/docs")
    print(f"   2. Check MongoDB: .\\check_mongodb.ps1")
    print(f"   3. View Dashboard: http://localhost:5173")
    print(f"\n   Test endpoints:")
    print(f"   • Today's KPIs: {API_BASE_URL}/dashboard/kpis/today?field_id={FIELD_ID}")
    print(f"   • Active Alerts: {API_BASE_URL}/alerts/active?field_id={FIELD_ID}")
    print(f"   • Pest Trend: {API_BASE_URL}/pests/trend?field_id={FIELD_ID}&days=7")
    print(f"   • Drone Status: {API_BASE_URL}/drone/status?drone_id=drone_001")

if __name__ == "__main__":
    main()
