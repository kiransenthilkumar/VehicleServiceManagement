#!/usr/bin/env python
"""
Generate placeholder car images matching the seeded vehicles in the database.
This script reads vehicle data from the database and creates images with matching filenames.
Run with: python generate_placeholder_images.py
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

def generate_image(filename, brand, model, fuel_type):
    """Generate a placeholder car image"""
    
    # Brand-specific colors
    brand_colors = {
        'Maruti Suzuki': (66, 135, 245),      # Blue
        'Hyundai': (237, 100, 166),            # Pink/Magenta
        'Honda': (255, 165, 0),                # Orange
        'Toyota': (76, 175, 80),               # Green
        'Tata': (156, 39, 176),                # Purple
    }
    
    color = brand_colors.get(brand, (100, 149, 237))
    
    # Create image
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(img)
    
    # Try to load fonts
    try:
        title_font = ImageFont.truetype("arial.ttf", 48)
        info_font = ImageFont.truetype("arial.ttf", 32)
        small_font = ImageFont.truetype("arial.ttf", 24)
    except:
        title_font = ImageFont.load_default()
        info_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Text color (white for dark bg, black for light)
    avg_color = (color[0] + color[1] + color[2]) // 3
    text_color = (255, 255, 255) if avg_color < 128 else (0, 0, 0)
    
    # Draw title
    title = f"{brand} {model}"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = bbox[2] - bbox[0]
    title_x = (width - title_width) // 2
    draw.text((title_x, 100), title, fill=text_color, font=title_font)
    
    # Draw fuel type
    fuel_text = f"Fuel: {fuel_type}"
    bbox = draw.textbbox((0, 0), fuel_text, font=info_font)
    fuel_width = bbox[2] - bbox[0]
    fuel_x = (width - fuel_width) // 2
    draw.text((fuel_x, 250), fuel_text, fill=text_color, font=info_font)
    
    # Draw filename
    bbox = draw.textbbox((0, 0), filename, font=small_font)
    filename_width = bbox[2] - bbox[0]
    filename_x = (width - filename_width) // 2
    draw.text((filename_x, 400), filename, fill=text_color, font=small_font)
    
    return img


def main():
    """Generate placeholder images for all vehicles in the database"""
    
    print("\n" + "="*60)
    print("🚗 GENERATING PLACEHOLDER CAR IMAGES")
    print("="*60 + "\n")
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    uploads_dir = os.path.join(basedir, 'static', 'uploads', 'vehicles')
    
    # Create uploads directory
    os.makedirs(uploads_dir, exist_ok=True)
    print(f"📁 Directory: {uploads_dir}\n")
    
    # Read from database
    try:
        from app import create_app
        from app.models import Vehicle
        
        app = create_app()
        with app.app_context():
            vehicles = Vehicle.query.all()
            
            if not vehicles:
                print("❌ No vehicles found in database!")
                print("   📋 Run: python seed_data.py")
                return
            
            images_created = []
            skipped_count = 0
            
            # Generate image for each vehicle
            for vehicle in vehicles:
                if not vehicle.image_path:
                    print(f"⚠️  Skipping vehicle '{vehicle.brand} {vehicle.model}' (no image_path set)")
                    continue
                
                filename = vehicle.image_path
                filepath = os.path.join(uploads_dir, filename)
                
                # Skip if already exists
                if os.path.exists(filepath):
                    print(f"⏭️  {filename} already exists")
                    skipped_count += 1
                    continue
                
                try:
                    # Generate image
                    img = generate_image(filename, vehicle.brand, vehicle.model, vehicle.fuel_type)
                    img.save(filepath, 'JPEG', quality=85)
                    
                    size_kb = os.path.getsize(filepath) / 1024
                    images_created.append((filename, size_kb))
                    print(f"✅ Created: {filename} ({size_kb:.1f}KB)")
                    
                except Exception as e:
                    print(f"❌ Error creating {filename}: {str(e)}")
            
            # Summary
            print("\n" + "="*60)
            print("✨ IMAGE GENERATION COMPLETE")
            print("="*60)
            
            total_size = sum(size for _, size in images_created)
            print(f"\n📊 Statistics:")
            print(f"   • Created: {len(images_created)} new images")
            print(f"   • Skipped: {skipped_count} existing images")
            print(f"   • Total size: ~{total_size:.0f}KB")
            print(f"   • Location: static/uploads/")
            
            if images_created:
                print(f"\n🎨 Created images:")
                for fname, size in sorted(images_created):
                    print(f"   • {fname} ({size:.1f}KB)")
            
            print("\n" + "="*60)
            print("✅ READY TO TEST!")
            print("="*60)
            print("\n🚀 Next steps:")
            print("  1. python run.py")
            print("  2. Login with: sundar / password123")
            print("  3. Go to 'My Vehicles' to see images!")
            print("\n" + "="*60 + "\n")
    
    except ImportError as e:
        print(f"❌ Error importing app: {e}")
        print("   Make sure you're in the project root directory")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == '__main__':
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("❌ Pillow (PIL) not installed!")
        print("\n📦 Install with:")
        print("   pip install Pillow\n")
        sys.exit(1)
    
    main()
