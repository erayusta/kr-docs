# Backend Dokümantasyonu - KampanyaRadar

## 📋 Genel Bakış

KampanyaRadar backend'i Laravel 12 framework'ü kullanılarak geliştirilmiş modern bir REST API'dir. Türkiye'nin en güncel kampanya ve indirim platformu için güçlü bir backend altyapısı sağlar.

## 🛠️ Teknoloji Stack'i

### Ana Framework
- **Laravel 12** - PHP web framework'ü
- **PHP 8.2** - Modern PHP versiyonu
- **MySQL/SQLite** - Veritabanı sistemi

### Admin Panel
- **Filament 3.2** - Modern admin panel framework'ü
- **Livewire** - Reactive PHP components
- **Alpine.js** - Lightweight JavaScript framework

### Authentication & Security
- **Laravel Sanctum 4.2** - API token authentication
- **CSRF Protection** - Cross-site request forgery koruması
- **Rate Limiting** - API abuse koruması

### Storage & CDN
- **BunnyCDN** - Global CDN servisi
- **Laravel Storage** - File storage abstraction
- **Image Optimization** - Otomatik görsel optimizasyonu

### Database & Caching
- **Eloquent ORM** - Laravel'in ORM'i
- **Redis** - Cache ve session storage
- **Database Migrations** - Version controlled schema

### Development Tools
- **Laravel Pint** - Code style fixer
- **Laravel Pail** - Log viewer
- **PHPUnit** - Testing framework
- **Faker** - Test data generator

## 🏗️ Mimari Yapı

### MVC Pattern
```
app/
├── Http/Controllers/Api/V1/    # API Controllers
├── Models/                      # Eloquent Models
├── Services/                    # Business Logic Services
├── Helpers/                     # Utility Classes
├── Observers/                   # Model Observers
├── Providers/                   # Service Providers
└── Filament/                    # Admin Panel Resources
```

### API Versioning
- **v1** - Mevcut API versiyonu
- **RESTful Design** - Standard HTTP methods
- **JSON Response Format** - Consistent API responses

## 🗄️ Veritabanı Yapısı

### Ana Tablolar

#### Users (Kullanıcılar)
```sql
- id (Primary Key)
- name (VARCHAR)
- email (VARCHAR, UNIQUE)
- password (HASHED)
- phone (VARCHAR, NULLABLE)
- birth_date (DATE, NULLABLE)
- gender (ENUM: male,female,other)
- role (VARCHAR, DEFAULT: 'user')
- is_active (BOOLEAN, DEFAULT: true)
- created_at, updated_at
```

#### Campaigns (Kampanyalar)
```sql
- id (Primary Key)
- slug (VARCHAR, UNIQUE)
- title (VARCHAR)
- content (TEXT)
- image (VARCHAR, NULLABLE)
- link (TEXT, NULLABLE)
- start_date (DATETIME)
- end_date (DATETIME)
- is_active (BOOLEAN)
- is_active_button (BOOLEAN)
- is_active_ads (BOOLEAN)
- item_type (ENUM: general,product,car,real_estate)
- item_id (INTEGER, NULLABLE)
- actuals (JSON, NULLABLE)
- coupon_code (VARCHAR, NULLABLE)
- meta (JSON, NULLABLE)
- form_id (FOREIGN KEY -> lead_forms)
- product_id (FOREIGN KEY -> products)
- car_id (FOREIGN KEY -> cars)
- real_estate_id (FOREIGN KEY -> real_estates)
- created_at, updated_at
```

#### Categories (Kategoriler)
```sql
- id (Primary Key)
- name (VARCHAR)
- slug (VARCHAR, UNIQUE)
- is_active (BOOLEAN)
- parent_id (FOREIGN KEY -> categories, NULLABLE)
- content (TEXT, NULLABLE)
- description (TEXT, NULLABLE)
- meta (JSON, NULLABLE)
- created_at, updated_at
```

#### Brands (Markalar)
```sql
- id (Primary Key)
- name (VARCHAR)
- slug (VARCHAR, UNIQUE)
- logo (VARCHAR, NULLABLE)
- is_active (BOOLEAN)
- created_at, updated_at
```

#### Products (Ürünler)
```sql
- id (Primary Key)
- title (VARCHAR)
- description (TEXT, NULLABLE)
- gtin (VARCHAR, NULLABLE)
- attributes (JSON, NULLABLE)
- stores (JSON, NULLABLE)
- brand_id (FOREIGN KEY -> brands)
- created_at, updated_at
```

#### Cars (Araçlar)
```sql
- id (Primary Key)
- brand (VARCHAR)
- model (VARCHAR)
- attributes (JSON, NULLABLE)
- images (JSON, NULLABLE)
- colors (JSON, NULLABLE)
- euroncap (JSON, NULLABLE)
- history_prices (JSON, NULLABLE)
- created_at, updated_at
```

#### Real Estates (Emlak)
```sql
- id (Primary Key)
- name (VARCHAR)
- delivery_date (DATE, NULLABLE)
- property_type (VARCHAR, NULLABLE)
- number_of_units (INTEGER, NULLABLE)
- floor_count (INTEGER, NULLABLE)
- city (VARCHAR, NULLABLE)
- district (VARCHAR, NULLABLE)
- images (JSON, NULLABLE)
- price_plans (JSON, NULLABLE)
- maps_url (TEXT, NULLABLE)
- heating (VARCHAR, NULLABLE)
- parking (VARCHAR, NULLABLE)
- elevator (VARCHAR, NULLABLE)
- created_at, updated_at
```

#### Leads (Lead'ler)
```sql
- id (Primary Key)
- campaign_id (FOREIGN KEY -> campaigns)
- name (VARCHAR)
- email (VARCHAR)
- phone (VARCHAR)
- form_data (JSON, NULLABLE)
- form_values (JSON, NULLABLE)
- interest_categories (JSON, NULLABLE)
- ip_address (VARCHAR, NULLABLE)
- user_agent (TEXT, NULLABLE)
- status (ENUM: new,contacted,converted,rejected)
- created_at, updated_at
```

### Pivot Tablolar

#### campaign_brand
```sql
- campaign_id (FOREIGN KEY -> campaigns)
- brand_id (FOREIGN KEY -> brands)
- PRIMARY KEY (campaign_id, brand_id)
```

#### campaign_category
```sql
- campaign_id (FOREIGN KEY -> campaigns)
- category_id (FOREIGN KEY -> categories)
- PRIMARY KEY (campaign_id, category_id)
```

#### brand_category
```sql
- brand_id (FOREIGN KEY -> brands)
- category_id (FOREIGN KEY -> categories)
- PRIMARY KEY (brand_id, category_id)
```

## 🔌 API Endpoints

### Base URL
- **Development**: `http://localhost:8000/api/v1`
- **Production**: `https://eru.kampanyaradar.com/api/v1`

### Authentication Endpoints

#### POST /auth/login
Kullanıcı girişi
```json
Request:
{
  "email": "user@example.com",
  "password": "password",
  "remember": false
}

Response:
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "user@example.com",
    "role": "user",
    "is_active": true
  },
  "token": "1|abc123...",
  "expires_at": "2024-01-16T10:00:00Z"
}
```

#### POST /auth/register
Kullanıcı kaydı
```json
Request:
{
  "name": "John Doe",
  "email": "user@example.com",
  "password": "password",
  "password_confirmation": "password",
  "phone": "+905551234567",
  "birth_date": "1990-01-01",
  "gender": "male"
}
```

#### GET /auth/me
Mevcut kullanıcı bilgileri (Authentication required)
```json
Response:
{
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "user@example.com",
    "phone": "+905551234567",
    "birth_date": "1990-01-01",
    "gender": "male",
    "role": "user",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

#### POST /auth/logout
Kullanıcı çıkışı (Authentication required)

### Ana Sayfa Endpoints

#### GET /
Ana sayfa verileri
```json
Response:
{
  "categories": [...],
  "sliders": [...],
  "brands": [...],
  "ads": [...],
  "posts": [...]
}
```

### Kampanya Endpoints

#### GET /campaigns
Kampanya listesi (filtreleme ve sayfalama ile)
```json
Query Parameters:
- page: Sayfa numarası (default: 1)
- startDate: Başlangıç tarihi filtresi
- endDate: Bitiş tarihi filtresi
- category: Kategori slug'ı
- brand: Marka slug'ı
- search: Arama terimi

Response:
{
  "data": [...],
  "pagination": {
    "currentPage": 1,
    "totalPages": 10,
    "totalCount": 180,
    "hasNextPage": true,
    "hasPrevPage": false,
    "nextPage": 2,
    "prevPage": null
  }
}
```

#### GET /campaigns/{slug}
Kampanya detayı
```json
Response:
{
  "data": {
    "id": 1,
    "title": "iPhone 15 İndirimi",
    "slug": "iphone-15-indirimi",
    "content": "Kampanya içeriği...",
    "image": "https://kampanyaradar-static.b-cdn.net/...",
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-12-31T23:59:59Z",
    "is_active": true,
    "brands": [...],
    "categories": [...],
    "lead_form": {...},
    "product": {...},
    "car": {...},
    "real_estate": {...},
    "item_type": "product"
  },
  "related": [...]
}
```

### Kategori Endpoints

#### GET /categories
Kategori listesi
```json
Response:
[
  {
    "id": 1,
    "name": "Elektronik",
    "slug": "elektronik",
    "is_active": true,
    "parent_id": null,
    "campaigns_count": 25
  }
]
```

#### GET /categories/{slug}
Kategori detayı ve kampanyaları

### Marka Endpoints

#### GET /brands
Marka listesi
#### GET /brands/all
Tüm markalar (admin için)
#### GET /brands/{slug}
Marka detayı ve kampanyaları

### Blog Endpoints

#### GET /posts
Blog post listesi
#### GET /posts/{slug}
Blog post detayı

### Lead Endpoints

#### POST /leads
Lead formu gönderimi
```json
Request:
{
  "campaign_id": 1,
  "name": "John Doe",
  "email": "user@example.com",
  "phone": "+905551234567",
  "form_data": {
    "additional_field": "value"
  }
}

Response:
{
  "message": "Lead submitted successfully",
  "data": {
    "id": 1,
    "campaign_id": 1,
    "name": "John Doe",
    "email": "user@example.com",
    "phone": "+905551234567",
    "status": "new",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### Kredi Endpoints

#### GET /loans
Kredi türleri listesi
#### POST /loans/calculations
Kredi hesaplama
#### GET /loan/offers
Kredi teklifleri
#### GET /loan/{loanType}
Kredi türü detayı

### Diğer Endpoints

#### GET /product
Ürün listesi
#### GET /page/{slug}
Statik sayfa içeriği
#### GET /settings
Sistem ayarları
#### GET /settings/group/{group}
Grup bazında ayarlar
#### GET /settings/{key}
Tekil ayar değeri

## 🎛️ Admin Panel (Filament)

### Panel Konfigürasyonu
- **URL**: `/admin`
- **Brand Name**: KampanyaRadar Yönetim Paneli
- **Primary Color**: #f97316 (Orange)
- **Authentication**: Laravel Auth

### Dashboard Widgets
- **StatsOverviewWidget**: Genel istatistikler
- **CampaignsChartWidget**: Kampanya grafikleri
- **LatestCampaignsWidget**: Son kampanyalar

### Resource Management
- **Campaigns**: Kampanya yönetimi
- **Categories**: Kategori yönetimi
- **Brands**: Marka yönetimi
- **Products**: Ürün yönetimi
- **Cars**: Araç yönetimi
- **Real Estates**: Emlak yönetimi
- **Leads**: Lead yönetimi
- **Posts**: Blog yönetimi
- **Users**: Kullanıcı yönetimi
- **Settings**: Sistem ayarları

### File Management
- **Image Upload**: BunnyCDN entegrasyonu
- **Bulk Operations**: Toplu işlemler
- **Export/Import**: Excel entegrasyonu

## 🔧 Services ve Helpers

### BunnyCDNService
CDN dosya yönetimi servisi
```php
// Dosya yükleme
$service->uploadFile($filePath, $remotePath);

// Dosya silme
$service->deleteFile($remotePath);

// CDN URL alma
$service->getCdnUrl($remotePath);

// Dosya varlık kontrolü
$service->fileExists($remotePath);
```

### ImageHelper
Görsel URL helper'ı
```php
// Marka logosu
ImageHelper::getBrandLogo($logo);

// Kampanya görseli
ImageHelper::getCampaignImage($image, $campaignId);

// Blog görseli
ImageHelper::getPostImage($image);

// Slider görseli
ImageHelper::getSliderImage($image);
```

## 🔄 Model Relationships

### Campaign Model
```php
// Many-to-many relationships
public function brands(): BelongsToMany
public function categories(): BelongsToMany

// Belongs to relationships
public function leadForm(): BelongsTo
public function product(): BelongsTo
public function car(): BelongsTo
public function realEstate(): BelongsTo

// Has many relationships
public function leads(): HasMany
```

### Category Model
```php
// Self-referencing
public function parent(): BelongsTo
public function children(): HasMany

// Many-to-many relationships
public function brands(): BelongsToMany
public function campaigns(): BelongsToMany
public function posts(): BelongsToMany
```

## 🛡️ Security & Middleware

### Authentication Middleware
- **Sanctum**: API token authentication
- **CSRF**: Cross-site request forgery protection
- **Rate Limiting**: API abuse prevention

### Custom Middleware
- **ForceUtf8**: UTF-8 encoding enforcement

### Security Features
- **Password Hashing**: Bcrypt hashing
- **Token Expiration**: Configurable token expiry
- **Input Validation**: Request validation
- **SQL Injection Protection**: Eloquent ORM protection

## 📊 Observers ve Events

### CampaignObserver
Kampanya modeli için observer
- **Creating**: Slug generation
- **Updating**: Cache invalidation
- **Deleting**: Related data cleanup

### PostObserver
Blog post modeli için observer
- **Creating**: Slug generation
- **Updating**: SEO meta update

## 🚀 Deployment ve Production

### Docker Konfigürasyonu
```dockerfile
FROM php:8.2-fpm

# System dependencies
RUN apt-get update && apt-get install -y \
    git curl libpng-dev libonig-dev libxml2-dev \
    libicu-dev libzip-dev zip unzip nginx supervisor

# PHP extensions
RUN docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd intl zip
RUN pecl install redis && docker-php-ext-enable redis

# Application setup
WORKDIR /var/www/html
COPY . /var/www/html
RUN composer install --no-dev --optimize-autoloader
RUN php artisan key:generate
RUN php artisan config:cache
RUN php artisan route:cache
RUN php artisan view:cache

EXPOSE 8000
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
```

### Environment Variables
```bash
# Application
APP_NAME=KampanyaRadar
APP_ENV=production
APP_KEY=base64:...
APP_DEBUG=false
APP_URL=https://eru.kampanyaradar.com

# Database
DB_CONNECTION=mysql
DB_HOST=mysql
DB_PORT=3306
DB_DATABASE=kampanyaradar
DB_USERNAME=root
DB_PASSWORD=password

# Redis
REDIS_HOST=redis
REDIS_PASSWORD=null
REDIS_PORT=6379

# BunnyCDN
BUNNYCDN_STORAGE_API_KEY=your_api_key
BUNNYCDN_STORAGE_ZONE_NAME=kampanyaradar-static
BUNNYCDN_URL=https://kampanyaradar-static.b-cdn.net

# Mail
MAIL_MAILER=smtp
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_password
MAIL_ENCRYPTION=tls
```

### Production Optimizations
- **Config Caching**: `php artisan config:cache`
- **Route Caching**: `php artisan route:cache`
- **View Caching**: `php artisan view:cache`
- **Autoloader Optimization**: `composer install --optimize-autoloader --no-dev`
- **OPcache**: PHP OPcache enable
- **Redis Caching**: Session ve cache için Redis

## 📈 Performance Monitoring

### Database Optimization
- **Indexing**: Proper database indexes
- **Query Optimization**: Eager loading ile N+1 problem çözümü
- **Connection Pooling**: Database connection optimization

### Caching Strategy
- **Redis**: Session ve cache storage
- **CDN**: BunnyCDN ile static asset delivery
- **Browser Caching**: HTTP cache headers

### Monitoring
- **Laravel Pail**: Real-time log monitoring
- **Error Tracking**: Comprehensive error logging
- **Performance Metrics**: Response time monitoring

## 🔧 Development Commands

### Artisan Commands
```bash
# Development server
php artisan serve

# Queue worker
php artisan queue:work

# Cache management
php artisan cache:clear
php artisan config:clear
php artisan route:clear
php artisan view:clear

# Database
php artisan migrate
php artisan migrate:fresh --seed
php artisan db:seed

# Filament
php artisan filament:upgrade
php artisan filament:install --panels
```

### Composer Scripts
```bash
# Development with all services
composer run dev

# Testing
composer run test

# Code style fixing
./vendor/bin/pint
```

Bu backend, modern Laravel best practice'lerini kullanarak geliştirilmiş, scalable, secure ve performant bir API platformudur.
