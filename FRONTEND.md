# Frontend Dokümantasyonu - KampanyaRadar

## 📋 Genel Bakış

KampanyaRadar frontend'i Next.js 14.2.3 framework'ü kullanılarak geliştirilmiş modern bir web uygulamasıdır. Türkiye'nin en güncel kampanya ve indirim platformu olarak tasarlanmıştır.

## 🛠️ Teknoloji Stack'i

### Ana Framework
- **Next.js 14.2.3** - React framework'ü
- **React 18** - UI kütüphanesi
- **Tailwind CSS 3.4.1** - CSS framework'ü

### UI Kütüphaneleri
- **Radix UI** - Accessible UI bileşenleri
  - Accordion, Avatar, Checkbox, Dialog, Dropdown Menu
  - Label, Menubar, Navigation Menu, Popover, Progress
  - Select, Separator, Slider, Slot, Tabs, Toast
- **Framer Motion 11.2.6** - Animasyonlar
- **Lucide React** - İkonlar
- **Embla Carousel** - Carousel bileşenleri
- **Swiper** - Touch slider

### Form ve Validasyon
- **React Hook Form 7.51.5** - Form yönetimi
- **Yup 1.4.0** - Schema validasyonu
- **Zod 3.23.8** - TypeScript-first schema validasyonu

### Grafik ve Veri Görselleştirme
- **Nivo Line 0.87.0** - Line chart'lar

### HTTP İstemcisi
- **Axios 1.7.1** - API istekleri

### Diğer Kütüphaneler
- **Iron Session 8.0.1** - Session yönetimi
- **Next SEO 6.5.0** - SEO optimizasyonu
- **Sharp 0.33.4** - Image optimizasyonu

## 🌐 CDN ve Static Asset Yapısı

### CDN Konfigürasyonu
```javascript
// next.config.js
images: {
  remotePatterns: [
    {
      protocol: 'https',
      hostname: 'kampanyaradar-static.b-cdn.net',
      port: '',
      pathname: '/kampanyaradar/**',
    },
  ],
}
```

### Environment Variables
```bash
# Production
NEXT_PUBLIC_API_URL=https://eru.kampanyaradar.com/api/v1
NEXT_PUBLIC_BASE_URL=https://eru.kampanyaradar.com
NEXT_PUBLIC_IMAGE_CDN=https://eru.kampanyaradar.com

# Development
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### CDN Kullanımı
- **Static Assets**: `kampanyaradar-static.b-cdn.net` üzerinden servis ediliyor
- **Image Optimization**: Next.js Image component ile otomatik optimizasyon
- **Path Pattern**: `/kampanyaradar/**` pattern'i ile organize edilmiş

## 🔌 API Endpoints ve Entegrasyon

### API Konfigürasyonu
Frontend iki farklı API client kullanıyor:

#### 1. Client-Side API (`apiRequest.js`)
```javascript
// Browser'da çalışan API istekleri
const apiClient = axios.create({
  headers: {
    'Content-Type': 'application/json'
  },
});

// Authentication token'ı localStorage'dan alır
if (isAuth) {
  const token = localStorage.getItem('token');
  headers['Authorization'] = `Bearer ${token}`;
}
```

#### 2. Server-Side API (`serverApiRequest.js`)
```javascript
// getServerSideProps'da kullanılan API istekleri
// Docker network içinde internal URL kullanır
const apiUrl = process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL;
```

### Kullanılan API Endpoints

#### Ana Sayfa Endpoints
- `GET /` - Ana sayfa verileri (kategoriler, slider'lar, markalar, reklamlar, postlar)

#### Kampanya Endpoints
- `GET /campaigns/{slug}` - Kampanya detayı
- `POST /leads` - Lead formu gönderimi

#### Kategori ve Marka Endpoints
- `GET /categories` - Kategori listesi
- `GET /categories/{slug}` - Kategori detayı
- `GET /brands/{slug}` - Marka detayı

#### Blog Endpoints
- `GET /posts/{slug}` - Blog post detayı
- `GET /posts` - Blog post listesi

#### Kredi Endpoints
- `GET /loan/{type}` - Kredi türü listesi
- `GET /loan/{type}/{bank}` - Banka kredileri
- `GET /loan/{type}/{bank}/detail` - Kredi detayı
- `GET /loan/offers` - Kredi teklifleri

#### Sayfa Endpoints
- `GET /page/{slug}` - Statik sayfa içeriği
- `GET /generate-sitemap` - Sitemap oluşturma

#### Authentication Endpoints
- `POST /auth/login` - Kullanıcı girişi
- `GET /auth/me` - Kullanıcı bilgileri

### API Request Patterns

#### Server-Side Rendering (SSR)
```javascript
export async function getServerSideProps() {
  const data = await serverApiRequest('/','get');
  return {
    props: {
      categories: data?.categories || [],
      carousels: data?.sliders || [],
      brands: data?.brands || [],
      ads: data?.ads || [],
      posts: data?.posts || []
    }
  }
}
```

#### Client-Side Requests
```javascript
// Authentication gerektiren istekler
const data = await apiRequest('/auth/me', 'get', {}, true);

// Form gönderimi
const response = await apiRequest('/leads', 'post', payload);

// Infinite scroll
const response = await apiRequest(`${url}&page=${page}&limit=10`, 'get');
```

### API Response Formatları

#### Ana Sayfa Response
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Elektronik",
      "slug": "elektronik",
      "campaigns": [
        {
          "id": 1,
          "title": "iPhone 15 İndirimi",
          "slug": "iphone-15-indirimi",
          "image": "https://kampanyaradar-static.b-cdn.net/kampanyaradar/campaigns/uploads/image.jpg",
          "endDate": "2024-12-31T23:59:59Z",
          "brands": [
            {
              "id": 1,
              "name": "Apple",
              "logo": "https://kampanyaradar-static.b-cdn.net/kampanyaradar/brands/apple.png"
            }
          ]
        }
      ]
    }
  ],
  "sliders": [
    {
      "id": 1,
      "name": "Ana Banner",
      "image": "https://kampanyaradar-static.b-cdn.net/kampanyaradar/sliders/banner.jpg",
      "link": "/kampanya/iphone-15-indirimi"
    }
  ],
  "brands": [
    {
      "id": 1,
      "name": "Apple",
      "slug": "apple",
      "logo": "https://kampanyaradar-static.b-cdn.net/kampanyaradar/brands/apple.png"
    }
  ],
  "ads": [
    {
      "id": 1,
      "name": "Header Reklam",
      "type": "image",
      "image": "https://kampanyaradar-static.b-cdn.net/kampanyaradar/ads/ad.jpg",
      "link": "https://example.com",
      "position": "home_header"
    }
  ],
  "posts": [
    {
      "id": 1,
      "title": "Kampanya Rehberi",
      "slug": "kampanya-rehberi",
      "image": "https://kampanyaradar-static.b-cdn.net/kampanyaradar/posts/post.jpg",
      "created_at": "15.01.2024"
    }
  ]
}
```

#### Kampanya Detay Response
```json
{
  "data": {
    "id": 1,
    "title": "iPhone 15 İndirimi",
    "slug": "iphone-15-indirimi",
    "content": "iPhone 15'te büyük indirim...",
    "image": "https://kampanyaradar-static.b-cdn.net/kampanyaradar/campaigns/uploads/image.jpg",
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-12-31T23:59:59Z",
    "is_active": true,
    "brands": [...],
    "categories": [...],
    "lead_form": {
      "id": 1,
      "title": "Kampanya Formu",
      "description": "Bilgilerinizi girin",
      "button_text": "Başvur",
      "fields": [
        {
          "name": "name",
          "label": "Ad Soyad",
          "type": "text",
          "required": true
        }
      ]
    },
    "product": {
      "id": 1,
      "title": "iPhone 15",
      "description": "Apple'ın yeni telefonu",
      "gtin": "123456789",
      "attributes": {...},
      "stores": [...],
      "brand": {...},
      "price_histories": [...]
    },
    "item_type": "product"
  },
  "related": [...]
}
```

## 📁 Proje Yapısı

```
frontend/
├── src/
│   ├── components/          # React bileşenleri
│   │   ├── common/         # Ortak bileşenler
│   │   ├── layouts/        # Layout bileşenleri
│   │   └── ui/            # UI bileşenleri
│   ├── hooks/              # Custom React hooks
│   ├── lib/               # Utility fonksiyonları
│   │   ├── apiRequest.js   # Client-side API
│   │   ├── serverApiRequest.js # Server-side API
│   │   └── config.js      # API konfigürasyonu
│   └── pages/              # Next.js sayfaları
│       ├── api/           # API routes
│       ├── blog/          # Blog sayfaları
│       ├── kampanya/      # Kampanya sayfaları
│       ├── kredi/         # Kredi sayfaları
│       ├── kategori/     # Kategori sayfaları
│       └── marka/         # Marka sayfaları
├── public/                 # Static dosyalar
├── .env.production        # Production environment
├── next.config.js         # Next.js konfigürasyonu
├── tailwind.config.js     # Tailwind CSS konfigürasyonu
└── package.json          # Dependencies
```

## 🚀 Build ve Deployment

### Scripts
```json
{
  "dev": "next dev",
  "build": "next build", 
  "start": "next start -H 0.0.0.0 -p 3000",
  "lint": "next lint"
}
```

### Docker Konfigürasyonu
- **Port**: 3000
- **Host**: 0.0.0.0 (Docker için)
- **Volume Mounts**: 
  - `./frontend:/app` - Source code
  - `/app/node_modules` - Dependencies
  - `/app/.next` - Build cache

### Environment Variables
- **Development**: `http://localhost:8000/api/v1`
- **Production**: `https://eru.kampanyaradar.com/api/v1`
- **Docker Internal**: `http://backend:8000/api/v1`

## 🔧 Özellikler

### SEO Optimizasyonu
- Next.js SEO ile meta tag yönetimi
- Sitemap.xml otomatik oluşturma
- Canonical URL'ler
- Server-side rendering

### Performance
- Image optimization (Sharp)
- Large page data bytes: 800KB
- Static asset CDN
- React strict mode

### User Experience
- Responsive design (Tailwind CSS)
- Smooth animations (Framer Motion)
- Infinite scroll
- Form validation
- Loading states

### Authentication
- JWT token tabanlı auth
- Session management (Iron Session)
- Protected routes
- User profile management

## 📊 Analytics ve Monitoring

### Google Analytics
- `NEXT_PUBLIC_GA_ID` - Google Analytics ID
- `NEXT_PUBLIC_GTM_ID` - Google Tag Manager ID

### Error Handling
- Comprehensive API error logging
- Client-side error boundaries
- Server-side error handling in SSR

## 🔄 Development Workflow

1. **Local Development**: `npm run dev`
2. **API Integration**: Environment variables ile backend bağlantısı
3. **Build Process**: `npm run build`
4. **Production**: Docker container olarak deploy

## 🎨 UI/UX Özellikleri

### Responsive Design
- **Mobile First**: Tailwind CSS ile responsive tasarım
- **Breakpoints**: sm (640px), md (768px), lg (1024px), xl (1280px), 2xl (1536px)
- **Grid System**: CSS Grid ve Flexbox kombinasyonu
- **Typography**: Inter font family ile modern tipografi

### Animasyonlar ve Etkileşimler
- **Framer Motion**: Sayfa geçişleri ve hover efektleri
- **Smooth Scrolling**: Native smooth scroll behavior
- **Loading States**: Skeleton loader'lar ve progress indicator'lar
- **Micro-interactions**: Button hover, card hover efektleri

### Accessibility
- **ARIA Labels**: Screen reader desteği
- **Keyboard Navigation**: Tab order ve focus management
- **Color Contrast**: WCAG 2.1 AA uyumlu renk kontrastları
- **Semantic HTML**: Proper heading hierarchy ve landmark'lar

## 🔧 Performance Optimizasyonları

### Image Optimization
- **Next.js Image Component**: Otomatik format dönüşümü (WebP, AVIF)
- **Lazy Loading**: Intersection Observer API ile lazy loading
- **CDN Integration**: BunnyCDN ile global image delivery
- **Responsive Images**: srcset ile farklı ekran boyutları için optimize edilmiş görseller

### Code Splitting
- **Dynamic Imports**: Route-based code splitting
- **Component Lazy Loading**: React.lazy() ile component-level splitting
- **Bundle Analysis**: Webpack Bundle Analyzer ile bundle boyutu optimizasyonu

### Caching Strategy
- **Static Generation**: getStaticProps ile static sayfa generation
- **ISR (Incremental Static Regeneration)**: revalidate ile cache invalidation
- **Browser Caching**: Cache-Control headers ile browser-level caching
- **CDN Caching**: BunnyCDN ile edge caching

## 🛡️ Security Features

### Authentication & Authorization
- **JWT Tokens**: Secure token-based authentication
- **Token Storage**: HttpOnly cookies ile güvenli token storage
- **Route Protection**: Middleware ile protected route'lar
- **CSRF Protection**: CSRF token validation

### Data Validation
- **Client-side**: Yup schema validation
- **Server-side**: API endpoint validation
- **Input Sanitization**: XSS koruması için input sanitization
- **Rate Limiting**: API rate limiting ile abuse koruması

## 📊 Analytics ve Monitoring

### Google Analytics 4
- **Event Tracking**: Custom event tracking
- **E-commerce Tracking**: Kampanya conversion tracking
- **User Journey**: Page view ve user flow analizi
- **Performance Monitoring**: Core Web Vitals tracking

### Error Monitoring
- **Error Boundaries**: React error boundary'ler
- **Console Logging**: Structured logging
- **Performance Monitoring**: Web Vitals ve Core Web Vitals
- **User Feedback**: Error reporting ve user feedback sistemi

## 🌐 SEO ve Marketing

### Technical SEO
- **Meta Tags**: Dynamic meta tag generation
- **Open Graph**: Social media sharing optimization
- **Twitter Cards**: Twitter sharing optimization
- **Structured Data**: JSON-LD structured data
- **Sitemap**: XML sitemap generation
- **Robots.txt**: Search engine crawling directives

### Content SEO
- **URL Structure**: SEO-friendly URL patterns
- **Heading Hierarchy**: Proper H1-H6 structure
- **Internal Linking**: Strategic internal linking
- **Image Alt Tags**: Descriptive alt text for images
- **Schema Markup**: Rich snippets için structured data

Bu frontend, modern web development best practice'lerini kullanarak geliştirilmiş, SEO-friendly, performant ve kullanıcı dostu bir kampanya platformudur.
