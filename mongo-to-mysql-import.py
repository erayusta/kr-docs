#!/usr/bin/env python3
"""
MongoDB to MySQL Migration Script v2
Converts MongoDB BSON backup files to MySQL without ID conflicts
"""

import json
import mysql.connector
from datetime import datetime
import os
from pathlib import Path
from bson import decode_all, ObjectId
import hashlib

# Configuration
MONGO_BACKUP_PATH = "/Users/erayusta/code/kampanyaradar-project/docs/mongodb_backup/kampanyaradar"
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'kampanyaradar',
    'password': 'appRadar3434**',
    'database': 'kampanyaradar',
    'port': 3307
}

# ID mapping to track MongoDB ObjectId to MySQL ID conversions
id_mappings = {
    'users': {},
    'categories': {},
    'brands': {},
    'campaigns': {},
    'lead_forms': {},
    'banks': {},
    'posts': {},
    'pages': {},
    'sliders': {},
    'ads': {},
    'products': {},
    'cars': {},
    'real_estates': {},
    'attributes': {},
    'leads': {}
}

def read_bson_file(filepath):
    """Read BSON file and return documents"""
    with open(filepath, 'rb') as f:
        data = f.read()
        try:
            return decode_all(data)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return []

def convert_objectid_to_string(obj):
    """Recursively convert ObjectId to string"""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectid_to_string(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_string(item) for item in obj]
    elif isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    return obj

def get_mysql_connection():
    """Create MySQL connection"""
    return mysql.connector.connect(**MYSQL_CONFIG)

def truncate_all_tables():
    """Truncate all tables to start fresh"""
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    # Disable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    tables = [
        'campaign_brand', 'campaign_category', 'category_post',
        'leads', 'campaigns', 'brands', 'categories', 'users',
        'lead_forms', 'banks', 'posts', 'pages', 'sliders',
        'ads', 'products', 'product_price_histories', 'cars',
        'real_estates', 'attributes'
        # Note: 'settings' is not truncated as it has default values from migration
    ]
    
    for table in tables:
        try:
            cursor.execute(f"TRUNCATE TABLE {table}")
            print(f"Truncated table: {table}")
        except Exception as e:
            print(f"Error truncating {table}: {e}")
    
    # Re-enable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    conn.commit()
    cursor.close()
    conn.close()

def migrate_settings():
    """Migrate settings collection to key-value structure"""
    print("Migrating Settings...")
    
    bson_file = os.path.join(MONGO_BACKUP_PATH, "Setting.bson")
    if not os.path.exists(bson_file):
        print("Settings file not found")
        return
    
    documents = read_bson_file(bson_file)
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    if documents:  # Should only have one settings document
        doc = documents[0]
        
        # Map old settings to new key-value structure
        settings_map = {
            'site_logo': doc.get('logo', '/logo.png'),
            'meta_title': doc.get('metaTitle', 'KampanyaRadar'),
            'meta_description': doc.get('metaDescription', 'Türkiye\'nin en güncel kampanya platformu'),
            'meta_keywords': doc.get('metaKeywords', 'kampanya, indirim, fırsat'),
            'meta_separator': doc.get('metaSeperate', '|'),
            'head_after_code': doc.get('headAfterCode', ''),
            'body_after_code': doc.get('bodyAfterCode', ''),
        }
        
        for key, value in settings_map.items():
            try:
                # Update existing or skip if already exists
                cursor.execute("""
                    UPDATE settings 
                    SET value = %s, updated_at = %s
                    WHERE `key` = %s
                """, (value, datetime.now(), key))
                
                if cursor.rowcount == 0:
                    print(f"Setting {key} not found in database, skipping...")
            except Exception as e:
                print(f"Error migrating setting {key}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Settings migration completed")

def migrate_users():
    """Migrate users collection"""
    print("Migrating Users...")
    
    bson_file = os.path.join(MONGO_BACKUP_PATH, "User.bson")
    if not os.path.exists(bson_file):
        print("Users file not found")
        return
    
    documents = read_bson_file(bson_file)
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    for doc in documents:
        try:
            # Generate a simple password hash (in production, this should be bcrypt)
            password = doc.get('password', 'password123')
            if not password.startswith('$2'):  # Not already hashed
                password = f"$2y$12${hashlib.sha256(password.encode()).hexdigest()[:22]}"
            
            cursor.execute("""
                INSERT INTO users (first_name, last_name, email, phone, password, role, 
                                 is_banned, is_active, last_login, birth_date, gender, 
                                 created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                doc.get('firstName', ''),
                doc.get('lastName', ''),
                doc.get('email', ''),
                doc.get('phone', ''),
                password,
                doc.get('role', 'user'),
                doc.get('isBanned', False),
                doc.get('isActive', True),
                doc.get('lastLogin', datetime.now()),
                doc.get('birthDate'),
                doc.get('gender'),
                doc.get('createdAt', datetime.now()),
                doc.get('updatedAt', datetime.now())
            ))
            
            # Store the mapping
            id_mappings['users'][str(doc['_id'])] = cursor.lastrowid
            
        except Exception as e:
            print(f"Error migrating user {doc.get('email', 'unknown')}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Users migration completed")

def migrate_categories():
    """Migrate categories collection"""
    print("Migrating Categories...")
    
    bson_file = os.path.join(MONGO_BACKUP_PATH, "Category.bson")
    if not os.path.exists(bson_file):
        print("Categories file not found")
        return
    
    documents = read_bson_file(bson_file)
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    # First pass - insert all categories without parent
    for doc in documents:
        try:
            cursor.execute("""
                INSERT INTO categories (name, slug, parent_id, is_active, 
                                      content, description, meta, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                doc.get('name', ''),
                doc.get('slug', ''),
                None,  # Parent will be updated in second pass
                doc.get('isActive', True),
                doc.get('content', ''),
                doc.get('description', ''),
                json.dumps(convert_objectid_to_string(doc.get('meta', {}))),
                doc.get('created_at', datetime.now()),
                doc.get('updated_at', datetime.now())
            ))
            
            # Store the mapping
            id_mappings['categories'][str(doc['_id'])] = cursor.lastrowid
            
        except Exception as e:
            print(f"Error migrating category {doc.get('name', 'unknown')}: {e}")
    
    conn.commit()
    
    # Second pass - update parent relationships
    for doc in documents:
        if doc.get('parentId'):
            try:
                parent_mongo_id = str(doc['parentId'])
                if parent_mongo_id in id_mappings['categories']:
                    cursor.execute("""
                        UPDATE categories SET parent_id = %s WHERE id = %s
                    """, (
                        id_mappings['categories'][parent_mongo_id],
                        id_mappings['categories'][str(doc['_id'])]
                    ))
            except Exception as e:
                print(f"Error updating parent for category {doc.get('name', 'unknown')}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Categories migration completed")

def migrate_brands():
    """Migrate brands collection"""
    print("Migrating Brands...")
    
    bson_file = os.path.join(MONGO_BACKUP_PATH, "Brand.bson")
    if not os.path.exists(bson_file):
        print("Brands file not found")
        return
    
    documents = read_bson_file(bson_file)
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    # Get existing brands from database
    cursor.execute("SELECT name, slug FROM brands")
    existing_brands = cursor.fetchall()
    existing_names = {row[0] for row in existing_brands}
    existing_slugs = {row[1] for row in existing_brands}
    
    for doc in documents:
        try:
            name = doc.get('name', '')
            slug = doc.get('slug', '')
            
            # Skip if name already exists in database
            if name in existing_names:
                print(f"Skipping duplicate brand name: {name}")
                # Still need to map the ID for relationships
                cursor.execute("SELECT id FROM brands WHERE name = %s", (name,))
                result = cursor.fetchone()
                if result:
                    id_mappings['brands'][str(doc['_id'])] = result[0]
                continue
            
            # Make slug unique if needed
            original_slug = slug
            counter = 1
            while slug in existing_slugs:
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            cursor.execute("""
                INSERT INTO brands (name, slug, logo, is_active, content, 
                                  created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                name,
                slug,
                doc.get('logo'),
                doc.get('isActive', True),
                doc.get('content', ''),
                doc.get('created_at', datetime.now()),
                doc.get('updated_at', datetime.now())
            ))
            
            # Store the mapping
            id_mappings['brands'][str(doc['_id'])] = cursor.lastrowid
            existing_names.add(name)
            existing_slugs.add(slug)
            
        except Exception as e:
            print(f"Error migrating brand {doc.get('name', 'unknown')}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Brands migration completed")

def migrate_campaigns():
    """Migrate campaigns collection"""
    print("Migrating Campaigns...")
    
    bson_file = os.path.join(MONGO_BACKUP_PATH, "Campaign.bson")
    if not os.path.exists(bson_file):
        print("Campaigns file not found")
        return
    
    documents = read_bson_file(bson_file)
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    # Track existing slugs
    existing_slugs = set()
    
    for doc in documents:
        try:
            # Map lead form ID
            lead_form_id = None
            if doc.get('leadFormId'):
                mongo_lead_form_id = str(doc['leadFormId'])
                if mongo_lead_form_id in id_mappings['lead_forms']:
                    lead_form_id = id_mappings['lead_forms'][mongo_lead_form_id]
            
            # Make slug unique if needed
            slug = doc.get('slug', '')
            original_slug = slug
            counter = 1
            while slug in existing_slugs:
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            cursor.execute("""
                INSERT INTO campaigns (slug, title, is_active, is_active_button, image, content,
                                     link, start_date, end_date, item_type, item_id,
                                     actuals, coupon_code, meta, is_active_ads, form_id,
                                     created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                slug,
                doc.get('title', ''),
                doc.get('isActive', True),
                doc.get('isActiveButton', 'join'),
                doc.get('image'),
                doc.get('content', ''),
                doc.get('link'),
                doc.get('startDate'),
                doc.get('endDate'),
                doc.get('itemType', 'general'),
                doc.get('itemId'),
                json.dumps(convert_objectid_to_string(doc.get('actuals', []))),
                doc.get('couponCode'),
                json.dumps(convert_objectid_to_string(doc.get('meta', {}))),
                doc.get('isActiveAds', True),
                lead_form_id,
                doc.get('created_at', datetime.now()),
                doc.get('updated_at', datetime.now())
            ))
            
            campaign_id = cursor.lastrowid
            id_mappings['campaigns'][str(doc['_id'])] = campaign_id
            existing_slugs.add(slug)
            
            # Add brand relationships
            if doc.get('brandIds'):
                for brand_mongo_id in doc['brandIds']:
                    if str(brand_mongo_id) in id_mappings['brands']:
                        cursor.execute("""
                            INSERT INTO campaign_brand (campaign_id, brand_id)
                            VALUES (%s, %s)
                        """, (campaign_id, id_mappings['brands'][str(brand_mongo_id)]))
            
            # Add category relationships
            if doc.get('categoryIds'):
                for cat_mongo_id in doc['categoryIds']:
                    if str(cat_mongo_id) in id_mappings['categories']:
                        cursor.execute("""
                            INSERT INTO campaign_category (campaign_id, category_id)
                            VALUES (%s, %s)
                        """, (campaign_id, id_mappings['categories'][str(cat_mongo_id)]))
            
        except Exception as e:
            print(f"Error migrating campaign {doc.get('title', 'unknown')}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Campaigns migration completed")

def migrate_posts():
    """Migrate posts collection"""
    print("Migrating Posts...")
    
    bson_file = os.path.join(MONGO_BACKUP_PATH, "Post.bson")
    if not os.path.exists(bson_file):
        print("Posts file not found")
        return
    
    documents = read_bson_file(bson_file)
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    for doc in documents:
        try:
            cursor.execute("""
                INSERT INTO posts (slug, title, content, image, meta,
                                 created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                doc.get('slug', ''),
                doc.get('title', ''),
                doc.get('content', ''),
                doc.get('image'),
                json.dumps(convert_objectid_to_string(doc.get('meta', {}))),
                doc.get('created_at', datetime.now()),
                doc.get('updated_at', datetime.now())
            ))
            
            post_id = cursor.lastrowid
            id_mappings['posts'][str(doc['_id'])] = post_id
            
            # Add category relationships
            if doc.get('categoryIds'):
                for cat_mongo_id in doc['categoryIds']:
                    if str(cat_mongo_id) in id_mappings['categories']:
                        cursor.execute("""
                            INSERT INTO category_post (category_id, post_id)
                            VALUES (%s, %s)
                        """, (id_mappings['categories'][str(cat_mongo_id)], post_id))
            
        except Exception as e:
            print(f"Error migrating post {doc.get('title', 'unknown')}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Posts migration completed")

def migrate_lead_forms():
    """Migrate leadforms collection"""
    print("Migrating Lead Forms...")
    
    bson_file = os.path.join(MONGO_BACKUP_PATH, "LeadForm.bson")
    if not os.path.exists(bson_file):
        print("Lead Forms file not found")
        return
    
    documents = read_bson_file(bson_file)
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    for doc in documents:
        try:
            cursor.execute("""
                INSERT INTO lead_forms (name, description, button_text, is_category_show,
                                      fields, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                doc.get('name', ''),
                doc.get('description', ''),
                doc.get('buttonText', 'Gönder'),
                doc.get('isCategoryShow', False),
                json.dumps(convert_objectid_to_string(doc.get('fields', []))),
                doc.get('created_at', datetime.now()),
                doc.get('updated_at', datetime.now())
            ))
            
            id_mappings['lead_forms'][str(doc['_id'])] = cursor.lastrowid
            
        except Exception as e:
            print(f"Error migrating lead form {doc.get('name', 'unknown')}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Lead Forms migration completed")

def migrate_pages():
    """Migrate pages collection"""
    print("Migrating Pages...")
    
    bson_file = os.path.join(MONGO_BACKUP_PATH, "Page.bson")
    if not os.path.exists(bson_file):
        print("Pages file not found")
        return
    
    documents = read_bson_file(bson_file)
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    for doc in documents:
        try:
            cursor.execute("""
                INSERT INTO pages (slug, title, content, meta,
                                 created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                doc.get('slug', ''),
                doc.get('title', ''),
                doc.get('content', ''),
                json.dumps(convert_objectid_to_string(doc.get('meta', {}))),
                doc.get('createdAt', datetime.now()),
                doc.get('updatedAt', datetime.now())
            ))
            
            id_mappings['pages'][str(doc['_id'])] = cursor.lastrowid
            
        except Exception as e:
            print(f"Error migrating page {doc.get('title', 'unknown')}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Pages migration completed")

def migrate_banks():
    """Migrate banks collection"""
    print("Migrating Banks...")
    
    bson_file = os.path.join(MONGO_BACKUP_PATH, "Bank.bson")
    if not os.path.exists(bson_file):
        print("Banks file not found")
        return
    
    documents = read_bson_file(bson_file)
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    for doc in documents:
        try:
            # Map brand ID
            brand_id = None
            if doc.get('brandId'):
                mongo_brand_id = str(doc['brandId'])
                if mongo_brand_id in id_mappings['brands']:
                    brand_id = id_mappings['brands'][mongo_brand_id]
                else:
                    print(f"Brand not found for bank: {mongo_brand_id}")
                    continue
            
            cursor.execute("""
                INSERT INTO banks (brand_id, content, faqs, personal, mortgage,
                                 new_car, used_car, is_active, sponsored_status,
                                 created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                brand_id,
                doc.get('content', ''),
                json.dumps(convert_objectid_to_string(doc.get('faqs', []))),
                json.dumps(convert_objectid_to_string(doc.get('personal', {}))),
                json.dumps(convert_objectid_to_string(doc.get('mortgage', {}))),
                json.dumps(convert_objectid_to_string(doc.get('newCar', {}))),
                json.dumps(convert_objectid_to_string(doc.get('usedCar', {}))),
                doc.get('isActive', True),
                doc.get('sponsoredStatus', False),
                datetime.now(),
                datetime.now()
            ))
            
            id_mappings['banks'][str(doc['_id'])] = cursor.lastrowid
            
        except Exception as e:
            print(f"Error migrating bank: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Banks migration completed")

def migrate_sliders():
    """Migrate sliders collection"""
    print("Migrating Sliders...")
    
    bson_file = os.path.join(MONGO_BACKUP_PATH, "Slider.bson")
    if not os.path.exists(bson_file):
        print("Sliders file not found")
        return
    
    documents = read_bson_file(bson_file)
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    for doc in documents:
        try:
            cursor.execute("""
                INSERT INTO sliders (name, image, link, is_active,
                                   created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                doc.get('name', ''),
                doc.get('image'),
                doc.get('link'),
                doc.get('isActive', True),
                doc.get('createdAt', datetime.now()),
                doc.get('updatedAt', datetime.now())
            ))
            
            id_mappings['sliders'][str(doc['_id'])] = cursor.lastrowid
            
        except Exception as e:
            print(f"Error migrating slider {doc.get('name', 'unknown')}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Sliders migration completed")

def migrate_ads():
    """Migrate ads collection"""
    print("Migrating Ads...")
    
    bson_file = os.path.join(MONGO_BACKUP_PATH, "Ads.bson")
    if not os.path.exists(bson_file):
        print("Ads file not found")
        return
    
    documents = read_bson_file(bson_file)
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    for doc in documents:
        try:
            cursor.execute("""
                INSERT INTO ads (name, type, item_type, device, item, image, link,
                               code, is_active, position, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                doc.get('name', ''),
                doc.get('type', ''),
                doc.get('itemType', ''),
                doc.get('device'),
                doc.get('item'),
                doc.get('image'),
                doc.get('link'),
                doc.get('code'),
                doc.get('isActive', True),
                doc.get('position', ''),
                doc.get('createdAt', datetime.now()),
                doc.get('updatedAt', datetime.now())
            ))
            
            id_mappings['ads'][str(doc['_id'])] = cursor.lastrowid
            
        except Exception as e:
            print(f"Error migrating ad {doc.get('name', 'unknown')}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Ads migration completed")

def migrate_leads():
    """Migrate leads collection"""
    print("Migrating Leads...")
    
    bson_file = os.path.join(MONGO_BACKUP_PATH, "Lead.bson")
    if not os.path.exists(bson_file):
        print("Leads file not found")
        return
    
    documents = read_bson_file(bson_file)
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    for doc in documents:
        try:
            # Map campaign ID
            campaign_id = None
            if doc.get('campaignId'):
                mongo_campaign_id = str(doc['campaignId'])
                if mongo_campaign_id in id_mappings['campaigns']:
                    campaign_id = id_mappings['campaigns'][mongo_campaign_id]
            
            # Map user ID
            user_id = None
            if doc.get('userId'):
                mongo_user_id = str(doc['userId'])
                if mongo_user_id in id_mappings['users']:
                    user_id = id_mappings['users'][mongo_user_id]
            
            # Map form ID
            form_id = None
            if doc.get('formId'):
                mongo_form_id = str(doc['formId'])
                if mongo_form_id in id_mappings['lead_forms']:
                    form_id = id_mappings['lead_forms'][mongo_form_id]
            
            cursor.execute("""
                INSERT INTO leads (campaign_id, form_values, interest_categories,
                                 created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                campaign_id,
                json.dumps(convert_objectid_to_string(doc.get('formValues', []))),
                json.dumps(convert_objectid_to_string(doc.get('interestCategories', []))),
                doc.get('createdAt', datetime.now()),
                doc.get('updatedAt', datetime.now())
            ))
            
            id_mappings['leads'][str(doc['_id'])] = cursor.lastrowid
            
        except Exception as e:
            print(f"Error migrating lead: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Leads migration completed")

def migrate_products():
    """Migrate products collection"""
    print("Migrating Products...")
    
    bson_file = os.path.join(MONGO_BACKUP_PATH, "Product.bson")
    if not os.path.exists(bson_file):
        print("Products file not found")
        return
    
    documents = read_bson_file(bson_file)
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    # Get brand name to ID mapping
    cursor.execute("SELECT id, name FROM brands")
    brand_mapping = {row[1]: row[0] for row in cursor.fetchall()}
    
    for doc in documents:
        try:
            # Map brand name to brand_id
            brand_name = doc.get('brand', '')
            brand_id = brand_mapping.get(brand_name) if brand_name else None
            
            # Handle datetime - could be datetime object or timestamp
            created_at = doc.get('createdAt', datetime.now())
            if isinstance(created_at, (int, float)):
                # Convert timestamp (milliseconds) to datetime
                created_at = datetime.fromtimestamp(created_at / 1000)
            elif not isinstance(created_at, datetime):
                created_at = datetime.now()
                
            updated_at = doc.get('updatedAt', datetime.now())
            if isinstance(updated_at, (int, float)):
                updated_at = datetime.fromtimestamp(updated_at / 1000)
            elif not isinstance(updated_at, datetime):
                updated_at = datetime.now()
            
            # Extract price from stores
            stores = doc.get('stores', [])
            price = None
            image = None
            images = []
            
            if stores and len(stores) > 0:
                # Get lowest price from stores
                prices = [float(store.get('price', 0)) for store in stores if store.get('price')]
                if prices:
                    price = min(prices)
                
                # Get first available image
                for store in stores:
                    if store.get('image_link'):
                        if not image:
                            image = store.get('image_link')
                        images.append(store.get('image_link'))
            
            cursor.execute("""
                INSERT INTO products (title, gtin, description, brand_id,
                                    attributes, stores, images, image, price,
                                    created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                doc.get('title'),
                doc.get('gtin', ''),
                doc.get('description'),
                brand_id,
                json.dumps(convert_objectid_to_string(doc.get('attributes', []))),
                json.dumps(convert_objectid_to_string(stores)),
                json.dumps(images) if images else None,
                image,
                price,
                created_at,
                updated_at
            ))
            
            id_mappings['products'][str(doc['_id'])] = cursor.lastrowid
            
        except Exception as e:
            print(f"Error migrating product {doc.get('gtin', 'unknown')}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Products migration completed")

def migrate_product_price_histories():
    """Migrate product price histories collection"""
    print("Migrating Product Price Histories...")
    
    bson_file = os.path.join(MONGO_BACKUP_PATH, "ProductPriceHistory.bson")
    if not os.path.exists(bson_file):
        print("Product Price Histories file not found")
        return
    
    documents = read_bson_file(bson_file)
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    for doc in documents:
        try:
            gtin = doc.get('gtin', '')
            
            # Check if product exists
            cursor.execute("SELECT id FROM products WHERE gtin = %s", (gtin,))
            result = cursor.fetchone()
            
            if result:
                # Insert price history with gtin, date, store_price, store_brand
                cursor.execute("""
                    INSERT INTO product_price_histories (gtin, date, store_price, store_brand, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    gtin,
                    doc.get('date', datetime.now().date()),
                    doc.get('storePrice', 0.0),
                    doc.get('storeBrand', ''),
                    datetime.now(),
                    datetime.now()
                ))
            else:
                print(f"Product not found for GTIN: {gtin}")
            
        except Exception as e:
            print(f"Error migrating product price history: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Product Price Histories migration completed")

def migrate_cars():
    """Migrate cars collection"""
    print("Migrating Cars...")
    
    bson_file = os.path.join(MONGO_BACKUP_PATH, "Car.bson")
    if not os.path.exists(bson_file):
        print("Cars file not found")
        return
    
    documents = read_bson_file(bson_file)
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    for doc in documents:
        try:
            cursor.execute("""
                INSERT INTO cars (model, brand, history_prices, attributes,
                                images, euroncap, colors, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                doc.get('model', ''),
                doc.get('brand', ''),
                json.dumps(convert_objectid_to_string(doc.get('historyPrices', []))),
                json.dumps(convert_objectid_to_string(doc.get('attributes', []))),
                json.dumps(convert_objectid_to_string(doc.get('images', []))),
                json.dumps(convert_objectid_to_string(doc.get('euroncap', {}))),
                json.dumps(convert_objectid_to_string(doc.get('colors', []))),
                datetime.now(),
                datetime.now()
            ))
            
            id_mappings['cars'][str(doc['_id'])] = cursor.lastrowid
            
        except Exception as e:
            print(f"Error migrating car {doc.get('model', 'unknown')}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Cars migration completed")

def migrate_real_estates():
    """Migrate real estates collection"""
    print("Migrating Real Estates...")
    
    bson_file = os.path.join(MONGO_BACKUP_PATH, "RealEstate.bson")
    if not os.path.exists(bson_file):
        print("Real Estates file not found")
        return
    
    documents = read_bson_file(bson_file)
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    for doc in documents:
        try:
            cursor.execute("""
                INSERT INTO real_estates (name, delivery_date, unit_delivery, property_type,
                                        number_of_units, floor_count, elevator, parking,
                                        heating, maps_url, images, price_plans, owners,
                                        country, city, district, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                doc.get('name', ''),
                doc.get('deliveryDate'),
                doc.get('unitDelivery', ''),
                doc.get('propertyType', ''),
                doc.get('numberOfUnits', 0),
                doc.get('floorCount', 0),
                doc.get('elevator', ''),
                doc.get('parking', ''),
                doc.get('heating', ''),
                doc.get('mapsUrl', ''),
                json.dumps(convert_objectid_to_string(doc.get('images', []))),
                json.dumps(convert_objectid_to_string(doc.get('pricePlans', []))),
                json.dumps(convert_objectid_to_string(doc.get('owners', []))),
                doc.get('country', 'Turkiye'),
                doc.get('city', ''),
                doc.get('district', ''),
                datetime.now(),
                datetime.now()
            ))
            
            id_mappings['real_estates'][str(doc['_id'])] = cursor.lastrowid
            
        except Exception as e:
            print(f"Error migrating real estate {doc.get('name', 'unknown')}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Real Estates migration completed")

def migrate_attributes():
    """Migrate attributes collection"""
    print("Migrating Attributes...")
    
    bson_file = os.path.join(MONGO_BACKUP_PATH, "Attribute.bson")
    if not os.path.exists(bson_file):
        print("Attributes file not found")
        return
    
    documents = read_bson_file(bson_file)
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    for doc in documents:
        try:
            cursor.execute("""
                INSERT INTO attributes (name, type, created_at, updated_at)
                VALUES (%s, %s, %s, %s)
            """, (
                doc.get('name', ''),
                doc.get('type', ''),
                datetime.now(),
                datetime.now()
            ))
            
            id_mappings['attributes'][str(doc['_id'])] = cursor.lastrowid
            
        except Exception as e:
            print(f"Error migrating attribute {doc.get('name', 'unknown')}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Attributes migration completed")

def migrate_all():
    """Run all migrations in order"""
    print("Starting MongoDB to MySQL migration...")
    print("=" * 50)
    
    # Truncate all tables first
    truncate_all_tables()
    
    # Run migrations in order (respecting foreign key dependencies)
    migrate_settings()
    migrate_users()
    migrate_categories()
    migrate_brands()
    migrate_attributes()
    migrate_lead_forms()  # Must be before campaigns
    migrate_banks()
    migrate_campaigns()
    migrate_posts()
    migrate_pages()
    migrate_sliders()
    migrate_ads()
    migrate_products()
    migrate_product_price_histories()  # Must be after products
    migrate_cars()
    migrate_real_estates()
    migrate_leads()  # Must be after campaigns and users
    
    print("=" * 50)
    print("Migration completed!")
    print(f"Total records migrated:")
    for table, mapping in id_mappings.items():
        if mapping:
            print(f"  {table}: {len(mapping)}")

if __name__ == "__main__":
    migrate_all()