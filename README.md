# HENDOSHI - Wear Your Weird 🖤⚡

![HENDOSHI Logo Banner](assets/readme/logo-banner.png)

[![Live Website](https://img.shields.io/badge/Live-Website-ff1493?style=for-the-badge)](https://hendoshi-store.onrender.com)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-000000?style=for-the-badge&logo=github)](https://github.com/dannykadoshi/Hendoshi_Ecommerce)
[![Business Model](https://img.shields.io/badge/Business-Model-CCFF00?style=for-the-badge)](BUSINESS_MODEL.md)
[![Testing Guide](https://img.shields.io/badge/Testing-Guide-9C27B0?style=for-the-badge)](TESTING.md)
[![Django](https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-316192?style=for-the-badge&logo=postgresql)](https://www.postgresql.org/)
[![Stripe](https://img.shields.io/badge/Stripe-Payments-008CDD?style=for-the-badge&logo=stripe)](https://stripe.com/)

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Business Model](#-business-model)
- [UX Design](#-ux-design)
  - [Agile Methodology](#agile-methodology)
  - [User Stories](#user-stories)
  - [Brand Identity & Mascot](#brand-identity--mascot)
  - [Design Philosophy](#design-philosophy)
  - [Color Scheme](#color-scheme)
  - [Typography](#typography)
  - [Wireframes](#wireframes)
- [Features](#-features)
  - [Navigation & Layout](#navigation--layout)
  - [Core E-commerce Features](#core-e-commerce-features)
    - [1. Product Catalog](#1-product-catalog)
    - [2. Product Detail Page](#2-product-detail-page)
    - [3. Shopping Cart & Checkout](#3-shopping-cart--checkout)
    - [4. User Authentication & Profiles](#4-user-authentication--profiles)
    - [5. Sale](#5-sale)
    - [6. New Drops](#6-new-drops)
    - [7. Collections](#7-collections)
    - [8. Product Types](#8-product-types)
    - [9. Shop by Audience](#9-shop-by-audience)
  - [Unique Features](#unique-features)
    - [10. Battle Vest (Wishlist)](#10-battle-vest-wishlist)
    - [11. The Vault (Community Gallery)](#11-the-vault-community-gallery)
    - [12. Seasonal Themes](#12-seasonal-themes)
    - [13. Product Reviews & Ratings](#13-product-reviews--ratings)
    - [14. Email Communications & Notifications](#14-email-communications--notifications)
  - [Informational Pages](#informational-pages)
    - [15. About Page](#15-about-page)
    - [16. FAQ Page](#16-faq-page)
    - [17. Track Order](#17-track-order)
    - [18. Contact Page](#18-contact-page)
    - [19. Size Guide, Shipping & Returns](#19-size-guide-shipping--returns)
    - [20. Custom Error Pages](#20-custom-error-pages)
    - [21. Cookie Consent Management](#21-cookie-consent-management)
  - [AI-Powered Features](#ai-powered-features)
    - [22. AI Content Generation (Google Gemini)](#22-ai-content-generation-google-gemini)
  - [Admin Features](#admin-features)
    - [23. Custom Admin Dashboard](#23-custom-admin-dashboard)
  - [Discount Codes & Promotional Banner](#discount-codes--promotional-banner)
    - [24. Discount Codes & Promotional Banner](#24-discount-codes--promotional-banner)
  - [Social Media Presence](#social-media-presence)
    - [25. Social Media Channels](#25-social-media-channels)
- [Database Schema](#-database-schema)
- [Technologies Used](#-technologies-used)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [SEO & Marketing](#-seo--marketing)
- [Credits](#-credits)
- [Acknowledgments](#-acknowledgments)
- [Contact](#-contact)

---

## 🎯 Project Overview

**HENDOSHI** is a full-stack Django e-commerce platform specializing in metal-inspired apparel and accessories featuring original skull, animal, and gym designs. The tagline "Wear Your Weird" embodies a brand philosophy celebrating individuality, alternative fashion, and the metal/gothic lifestyle.

### Project Goals

1. **Create a distinctive brand identity** - Stand out in the alternative fashion market with unique designs and a cohesive dark aesthetic
2. **Build a community** - Foster engagement through the Vault (community gallery) and Battle Vest (wishlist) features
3. **Deliver seamless UX** - Provide intuitive navigation, fast performance, and mobile-first design
4. **Implement robust e-commerce** - Secure payments, inventory management, and order tracking
5. **Demonstrate technical proficiency** - Showcase advanced Django development skills for Code Institute assessment

### Target Audience

- **Metal & Alternative Music Fans** - Everyone who love heavy metal, rock, and gothic culture
- **Alternative Fashion Enthusiasts** - Individuals seeking unique, edgy apparel beyond mainstream fashion
- **Gym & Fitness Community** - People who want motivational skull/dark-themed workout gear
- **Art Collectors** - Fans of original skull and animal illustrations
- **Gift Shoppers** - Looking for unique gifts for alternative lifestyle friends/family

---

## 💼 Business Model

[![Business Model Documentation](https://img.shields.io/badge/Business_Model-Documentation-CCFF00?style=for-the-badge)](BUSINESS_MODEL.md)

HENDOSHI operates on a **B2C (Business-to-Consumer) e-commerce model** with Print-on-Demand (POD) integration for sustainable inventory management.

### Revenue Streams

1. **Direct Product Sales** - T-shirts, hoodies, stickers, accessories (€15–€100 price range)
2. **Premium Collections** - Limited edition designs at higher price points
3. **Seasonal Campaigns** - Holiday-themed products and animations

### Value Proposition

- **Unique Original Designs** - No generic stock art — all illustrations created specifically for HENDOSHI
- **Quality Storytelling** - Each design has a "Design Story" explaining its inspiration and meaning
- **Community Engagement** - Vault gallery allows customers to share photos wearing HENDOSHI gear
- **Personalized Experience** - Battle Vest wishlist, custom seasonal themes, and curated recommendations

---

## 🎨 UX Design

### Agile Methodology

This project was developed using **Agile principles** with iterative development cycles and continuous feedback integration.

[![GitHub Projects Board](https://img.shields.io/badge/GitHub-Projects_Board-00ACC1?style=for-the-badge&logo=github&logoColor=white)](https://github.com/users/dannykadoshi/projects/7)

The project board is **publicly visible** and demonstrates full Agile project management:

- **Total Issues:** 54 (all publicly tracked)
  - ✅ **Completed:** 54 issues closed (all mapped to user stories)

- **Board Columns** (Kanban status):
  - 📋 **Backlog** — Issues identified but not yet scheduled
  - 📝 **Todo** — Scheduled for current sprint
  - 🔄 **In Progress** — Actively being developed
  - ✅ **Done** — Completed and verified
  - 🔮 **Future Enhancements** — Post-launch nice-to-haves

- **10 Epics** organised by feature area (GitHub labels: `epic: *`):
  1. `epic: authentication` — Registration, login, password reset, profiles (#1–5)
  2. `epic: products` — Product catalog, filtering, sorting, search, detail pages (#6–11)
  3. `epic: checkout` — Cart, shipping, Stripe payments, order confirmation (#12–19)
  4. `epic: wishlist` — Battle Vest wishlist, price-drop notifications (#20–22)
  5. `epic: design-stories` — Design story content, admin management (#23–25)
  6. `epic: vault` — Community gallery, moderation, Hall of Fame, likes, votes (#26–29, #51–55)
  7. `epic: marketing` — Newsletter, SEO, Facebook page, social sharing (#30–33)
  8. `epic: admin` — Product CRUD, order management, Vault moderation (#34–38, #52)
  9. `epic: ux` — Navigation, 404 page, responsive design, light/dark mode (#39–42, #46)
  10. `epic: orders` — Order history, order detail, customer support (#43–45)

- **Prioritisation Labels** (MoSCoW method):
  - 🔴 **Must-Have** — Core MVP features: **26 issues**
  - 🟡 **Should-Have** — Important for UX, non-blocking: **16 issues**
  - 🟢 **Could-Have** — Nice-to-have enhancements: **12 issues** (includes 3 AI feature issues)

- **Issue Structure** — Every issue follows standard format:
  - **Title:** `[USER STORY]: User-centric feature description`
  - **Description:** User story ("As a [role], I can [action] so that [benefit]")
  - **Acceptance Criteria:** Step-by-step validation requirements
  - **Epic Label:** Links to parent epic (e.g., `epic: checkout`)
  - **Priority Label:** MoSCoW classification (must-have / should-have / could-have)
  - **Milestone:** Sprint week assignment
  - **Status:** Backlog / Todo / In Progress / Done / Future Enhancements


- **4 Sprint Milestones** (matching GitHub milestone names):
  - **Milestone 1:** Setup & Authentication (Week 1–2) — #1–5, #39–41
  - **Milestone 2:** Product Catalog & Checkout (Week 3–4) — #6–19, #34–36
  - **Milestone 3:** Custom Features & Testing (Week 5–6) — #20–29, #37–38, #42–46, #48–55
  - **Milestone 4:** SEO, Marketing & Deployment (Week 7–8) — #30–33

The Agile approach enabled:
- ✅ Flexible response to changing requirements (e.g., added seasonal themes mid-project)
- ✅ Clear prioritisation of MVP features vs. enhancements using MoSCoW
- ✅ Systematic tracking of progress across 4 sprints and 10 epics
- ✅ Evidence-based demonstration of Code Institute competencies
- ✅ Continuous delivery mindset with weekly deployments to production

![GitHub Projects Board](assets/readme/agile-board.png)

### User Stories

#### **Epic 1: Shopping Experience**
- ✅ As a **shopper**, I can **browse products by collection** so that **I can find designs that match my interests**
- ✅ As a **shopper**, I can **view detailed product information** so that **I can make informed purchase decisions**
- ✅ As a **shopper**, I can **filter and sort products** so that **I can quickly find what I'm looking for**
- ✅ As a **shopper**, I can **search for specific products** so that **I can locate items by name or keyword**
- ✅ As a **shopper**, I can **see product reviews and ratings** so that **I can assess quality before buying**
- ✅ As a **shopper**, I can **browse products by audience** (Men/Women/Kids/Unisex) so that **I can find designs suited to me**
- ✅ As a **shopper**, I can **view a size guide** so that **I can choose the correct size before purchasing**
- ✅ As a **shopper**, I can **read a design story** so that **I can understand the inspiration behind the artwork**

#### **Epic 2: Cart & Checkout**
- ✅ As a **customer**, I can **add items to my cart** so that **I can purchase multiple products**
- ✅ As a **customer**, I can **view my cart contents** so that **I can review my selection before checkout**
- ✅ As a **customer**, I can **apply discount codes** so that **I can save money on purchases**
- ✅ As a **customer**, I can **select a shipping method** so that **I can choose my preferred delivery option**
- ✅ As a **customer**, I can **complete secure checkout** so that **my payment information is protected**
- ✅ As a **customer**, I can **receive order confirmation** so that **I know my purchase was successful**
- ✅ As a **customer**, I can **track my order** so that **I know when to expect delivery**
- ✅ As a **customer**, I can **download an invoice** so that **I have a receipt for my purchase**

#### **Epic 3: Account Management**
- ✅ As a **user**, I can **create an account** so that **I can save my information for future purchases**
- ✅ As a **user**, I can **view my order history** so that **I can track past purchases**
- ✅ As a **user**, I can **save multiple shipping addresses** so that **checkout is faster**
- ✅ As a **user**, I can **manage notification preferences** so that **I control what emails I receive**
- ✅ As a **user**, I can **create a Battle Vest wishlist** so that **I can save favourite products**
- ✅ As a **user**, I can **reset my password** so that **I can regain access to my account**
- ✅ As a **user**, I can **unsubscribe from emails** so that **I can opt out without logging in**
- ✅ As a **user**, I can **sign up for the newsletter** so that **I receive updates and exclusive offers**

#### **Epic 4: Community Engagement**
- ✅ As a **community member**, I can **submit photos to the Vault** so that **I can share my HENDOSHI style**
- ✅ As a **community member**, I can **view featured photos** so that **I can get style inspiration**
- ✅ As a **visitor**, I can **browse the Hall of Fame** so that **I can see legendary community submissions**
- ✅ As a **user**, I can **leave product reviews** so that **I can share my experience with others**
- ✅ As a **user**, I can **upvote/downvote Vault photos** so that **the best content rises to the top**
- ✅ As a **user**, I can **like Vault photos** so that **I can show appreciation for community content**

#### **Epic 5: Admin Management**
- ✅ As an **admin**, I can **create and edit products** so that **I can manage the store inventory**
- ✅ As an **admin**, I can **manage discount codes** so that **I can run promotional campaigns**
- ✅ As an **admin**, I can **moderate Vault submissions** so that **content quality is maintained**
- ✅ As an **admin**, I can **configure seasonal themes** so that **the store has festive animations**
- ✅ As an **admin**, I can **manage customer orders** so that **I can update statuses and resolve issues**
- ✅ As an **admin**, I can **moderate product reviews** so that **only appropriate reviews are published**
- ✅ As an **admin**, I can **manage shipping rates** so that **delivery costs are up to date**
- ✅ As an **admin**, I can **view newsletter subscribers** so that **I can manage my email audience**

### Brand Identity & Mascot

![Pug Skull Mascot](assets/readme/pug-skull-mascot.png)

The **Pug Skull** is the heart and soul of HENDOSHI's identity. The mascot — a skull with unmistakable pug features — appears across the website, error pages, product imagery, and branding materials as a recurring symbol of the brand's personality.

**A tribute to Jasmine 🖤**

Jasmine was a real pug — the beloved companion of HENDOSHI's founder, Danny. She passed away while the site was being created, but her memory, warmth, and quirky spirit live on in every design. The Pug Skull is not just a logo: it is a permanent tribute to Jasmine, the unlikely muse who helped shape the brand's look, feel, and heart.

The skull motif merges the metal/gothic aesthetic (skulls as symbols of mortality, rebellion, and raw energy) with the pug's lovable, wrinkled, expressive face — creating something that is both heavy and tender, dark and playful, serious and weird. That tension *is* HENDOSHI.

**Where the mascot appears:**
- **Every Page Hero Section** — Animated pug skull appears as a subtle floating element or accent in page headers, creating visual continuity across the site
- **Email Templates** — Pug skull watermark and illustrations in transactional emails (order confirmation, shipping updates, promotional newsletters)
- **404 Error Page** — Floating pug skull with a pink glow tells visitors "this page got lost in the void"
- **500 Error Page** — Pug skull investigates the server error with the same calm it once brought to the couch
- **Product Designs** — Skull imagery woven through the HENDOSHI design catalogue as a core design motif
- **Branding Materials** — Logo, banners, promotional assets, social media graphics, and merchandise

> *"Wear Your Weird" — and never forget the ones who made you that way.*

---

### Design Philosophy

**"Dark, Bold, Unapologetic"** - The HENDOSHI aesthetic combines:

1. **Gothic Elegance** - Dark backgrounds, dramatic contrast, neon accent colours
2. **Metal Energy** - Sharp edges, aggressive typography, high-energy animations
3. **Modern Glassmorphism** - Frosted glass UI elements with backdrop blur effects
4. **Accessibility First** - High contrast ratios, clear typography, mobile-optimised layouts

### Color Scheme

**Full light/dark theme toggle** with sun/moon icon in navigation bar.

![Color Palette](assets/readme/color-palette.png)

#### ✨ Dark Mode (Default)

![Dark Mode](assets/readme/dark-mode.png)

The default dark theme embodies the brand's alternative aesthetic with a moody, immersive experience:

| Color | Hex | Usage |
|-------|-----|-------|
| **Neon Pink** | `#FF1493` | Primary CTA buttons, accents, gradients |
| **Electric Yellow** | `#CCFF00` | Secondary accents, highlights, gradients |
| **Charcoal** | `#1A1A1A` | Main background (dark mode) |
| **Off-White** | `#F5F5F5` | Primary text (dark mode), background (light mode) |
| **Gray** | `#333333` | Secondary backgrounds, borders |


#### 🌞 Light Mode 

![Light Mode](assets/readme/light-mode.png)

 The light mode provides a fresh, accessible alternative while maintaining brand identity:

| Element | Color |
|---------|-------|
| **Background** | `#F5F5F5` (Off-White) |
| **Text** | `#1A1A1A` (Charcoal) |
| **Accents** | `#FF1493` (Neon Pink), `#CCFF00` (Electric Yellow) |
| **Borders/Secondary** | `#CCCCCC` (Light Gray) |

**Why Light Mode Matters:**
- ✅ **Accessibility** — WCAG-compliant contrast ratios for better readability
- ✅ **User Choice** — Responsive to system theme preferences and manual selection
- ✅ **Brand Flexibility** — Proves the design system is robust and scalable
- ✅ **Daytime Browsing** — Ideal for shopping in bright environments without eye strain
- ✅ **Professional Appeal** — Shows polish and attention to user comfort

### Typography

- **Display/Headers:** System UI with uppercase, heavy font-weight (900), wide letter-spacing
- **Body Text:** Montserrat, Arial, sans-serif stack for readability
- **Special Effects:** Linear gradient text fills (neon pink → electric yellow) for hero titles and CTAs

### Wireframes

Wireframes were created during the planning phase to define page layout and user flow before development.

**📸 Homepage Wireframe**

![Homepage Wireframe](assets/readme/wireframe-homepage.png)

**📸 Product List Wireframe:**

![Product List Wireframe](assets/readme/wireframe-products.png)

**📸 Product Detail Wireframe:**

![Product Detail Wireframe](assets/readme/wireframe-product-detail.png)

**📸 Cart Wireframe:**

![Cart Wireframe](assets/readme/wireframe-checkout.png)

**📸 Profile Dashboard Wireframe:**

![Profile Dashboard Wireframe](assets/readme/wireframe-profile.png)

**📸 Mobile Navigation Wireframe:**

![Mobile Navigation Wireframe](assets/readme/wireframe-mobile-nav.png)

---

## ✨ Features

### Navigation & Layout

**- Navbar Desktop:**
![Navigation Desktop](assets/readme/feature-navbar-desktop.png)

**- Sidebar Menu Mobile:**
![Navigation Mobile](assets/readme/feature-navbar-mobile.png)

- **Sticky navigation bar** - Remains visible on scroll with glassmorphic styling
- **Discount banner** - Animated scrolling promotional banner at top of page
- **Desktop mega menu** - Multi-column dropdowns with Collections, Audiences, and product types
- **Mobile slide-in menu** - Full-panel navigation with sub-menus
- **Smart search** - Floating search box with instant product lookup
- **Cart badge** - Real-time item count updates on add/remove
- **Battle Vest badge** - Live wishlist count for authenticated users
- **Theme toggle** - Sun/moon icon for light/dark mode, persists across sessions
- **Light/dark mode** - Full site theming with smooth transition

**Footer:**

![Footer](assets/readme/footer.png)

- **Shop column** — Quick links to Sale, New Drops, Collections, and Products pages
- **Customer Care column** — Links to Track Your Order, Contact Us, FAQ, and About Us
- **Legal column** — Privacy Policy, Return Policy, Shipping Policy, Size Guide, Cookie Settings
- **Newsletter signup** — Inline email subscribe form with GDPR consent checkbox (see [Newsletter & Notifications](#14-newsletter--notifications))
- **Social media icons** — Instagram, Facebook, X (Twitter), Pinterest links
- **Payment method badges** — Visa, Mastercard, Amex, Apple Pay, Google Pay icons
- **Copyright line** — "© 2026 HENDOSHI · Wear Your Weird"

---

### Core E-commerce Features

#### 1. Product Catalog

![Product Grid](assets/readme/feature-product-grid.png)

- **Responsive grid** — 6 columns (desktop), 4 columns (tablet), 2 columns (mobile)
- **Glassmorphic product cards** with hover effects and image zoom
- **Quick Add to Cart** — For single-variant products, adds directly with success toast
- **Quick Add modal** — For multi-variant products, opens a size/colour selector overlay
- **Battle Vest (wishlist) heart icon** on every product card
- **Real-time stock indicators** — In Stock / Low Stock / Out of Stock badges
- **Sale badges** with calculated discount percentages
- **Collection filtering** — Filter by Skulls & Death, Weird Animals, Gym Designs, etc.
- **Price range filtering** — Slider-based price range selection
- **Dynamic sorting** — Newest, Price Low-High, Price High-Low, Popularity
- **Pagination** — 12 products per page with previous/next navigation

![Product Filters](assets/readme/feature-product-filters.png)

**Technical Implementation:**
- 11 custom Django models with full CRUD operations
- Lazy-loaded images with WebP format for performance
- AJAX-based filtering without full page reload
- `select_related` and `prefetch_related` for optimised database queries

#### 2. Product Detail Page

![Product Detail 1](assets/readme/feature-product-detail-1.png)
![Product Detail 2](assets/readme/feature-product-detail-2.png)
![Product Detail 3](assets/readme/feature-product-detail-3.png)

- **Image Gallery** — Main image with up to 3 thumbnail gallery images
- **Image Lightbox** — Click any image to view full-size in modal overlay
- **Variant Selection** — Size (XS–5XL), colour, and audience (Men/Women/Unisex/Kids) dropdowns
- **Real-time stock checking** — Shows stock status per variant on selection
- **Quantity selector** — +/− buttons (min 1, max 99)
- **Customer Reviews** — Star ratings, verified purchase badges, helpful vote counts
- **Review Photos** — Up to 3 images per review with lightbox
- **Rating Distribution** — Bar chart showing star breakdown
- **Related Products carousel** — Up to 4 products from the same collection
- **Social Share** — Share buttons for Facebook, Twitter/X, WhatsApp
- **Design Story** — Narrative tab explaining the artwork's inspiration and meaning

![Product Design Story](assets/readme/feature-design-story.png)

#### 3. Shopping Cart & Checkout

**Cart Drawer Features:**

![Cart Drawer](assets/readme/feature-cart-drawer.png)

- **Sliding drawer interface** — Smooth right-side animation, accessible via cart icon
- **Live cart updates** — All totals recalculate in real-time via AJAX
- **Quantity adjustments** — +/− buttons with loading spinners during update
- **Remove items** — One-click removal with instant total recalculation
- **Shipping progress bar** — Visual indicator toward free shipping threshold (€50)
- **Discount code application** — Inline validation with clear error messages
- **Guest-friendly** — Session-based cart for non-logged-in users, merges on login

**Checkout Features:**

![Full Cart](assets/readme/feature-full-cart.png)
- **Stripe Payment Integration** — Secure card processing with SCA (3D Secure) support
![Stripe Payment](assets/readme/stripe-payment.png)
- **Guest Checkout** — Purchase without creating an account
![Guest Checkout](assets/readme/guest-checkout.png)
- **Saved Addresses** — Registered users can select from saved shipping addresses
![Saved Addresses](assets/readme/saved-addresses.png)
- **Shipping Rate Selection** — Choose from available shipping methods with prices
![Shipping Rate](assets/readme/shipping-rate.png)
- **Order Summary Sidebar** — Persistent view of cart items and totals
![Order Summary Sidebar](assets/readme/order-summary-sidebar.png)
- **Email Confirmation** — Branded HTML email with full order details on completion
![Email Confirmation](assets/readme/email-confirmation.png)
- **Order Number** — Unique generated reference (e.g., HEN-20240204-A1B2C3)
![Order Confirmation](assets/readme/feature-order-confirmation.png)


#### 4. User Authentication & Profiles

- **Signup Page** — Sign Up page form.
![Sign Up Page](assets/readme/feature-signup.png)
- **Email Verification** — Confirmation email required before account is activated
![Email Verification](assets/readme/email-verification.png)
- **Password Reset** — Secure token-based email recovery flow
![Password Reset](assets/readme/password-reset.png)
- **Profile Dashboard** — Order history, saved addresses, preferences overview
![Profile Dashboard](assets/readme/feature-profile.png)

- **Multiple Saved Addresses** — Add, edit, delete, and set default shipping addresses
![Edit Saved Addresses](assets/readme/edit-saved-addresses.png)
- **Order History** — Full list of past orders with status and detail view
![Order History](assets/readme/order-history.png)
![Order Details](assets/readme/order-details.png)
- **Invoice Download** — Download PDF invoice for any order
![Invoice Download](assets/readme/invoice-download.png)
- **Notification Preferences** — Granular email type toggles (see [Newsletter & Notifications](#9-newsletter--notifications))
![Notification Preferences](assets/readme/notification-preferences.png)
- **Account Settings** — Change email, update password
![Account Settings](assets/readme/account-settings.png)

---

#### 5. Sale

![Sales Page](assets/readme/sales-page.png)

- **Dedicated Sale page** — Lists all products currently on sale, filtered automatically based on `sale_price`, `sale_start`, and `sale_end` date constraints
- **Sale badge** — "SALE" label shown on product cards and detail pages when a product is on sale
- **Savings displayed** — Original price struck through alongside the discounted price and percentage off
- **Filtering & sorting** — Filter by collection, product type, and audience; sort by price or name
- **AJAX pagination** — Browse sale products without full page reload
- **Footer & navbar link** — Highlighted with a flame emoji (🔥 Sale) in both the footer and navigation for instant visibility

#### 6. New Drops

![New Drops](assets/readme/new-drops.png)

- **Dedicated New Drops page** — Auto-populated with the most recently added active products (last 30 days; expands to 60 days if fewer than 20 results found), capped at 50 items
- **Chronological ordering** — Newest products first by default
- **Filtering** — Filter by collection, product type, and audience
- **Sorting** — Sort by price (asc/desc) or name (asc/desc)
- **Total count** — Shows how many new products are currently available
- **Navbar & footer link** — "New Drops" appears in the navigation dropdown and footer Shop column

#### 7. Collections

![Collections](assets/readme/collections.png)

- **Collections overview page** — Card-based grid showing every active collection with a representative product image and item count
- **Popularity ordering** — Collections sorted by number of active products (most popular first)
- **Click-through to filtered catalog** — Each collection card links directly to the Product Catalog pre-filtered to that collection
- **Empty collections hidden** — Collections with no active products are automatically excluded
- **Navbar integration** — Collections listed in the desktop mega-menu dropdown and mobile sidebar

#### 8. Product Types

![Product Types](assets/readme/product-types.png)

- **Product Types overview page** — Card-based grid showing each product type (e.g. T-Shirts, Hoodies, Accessories) with a representative image and item count
- **Popularity ordering** — Types sorted by number of active products
- **Click-through to filtered catalog** — Each card links to the Product Catalog filtered by that type
- **Audience flag** — Each `ProductType` model has a `requires_audience` flag; types that use it expose Men / Women / Kids / Unisex filtering on the catalog
- **Navbar integration** — Product types listed in the desktop mega-menu and mobile sidebar under "Products"

#### 9. Shop by Audience

![Shop by Audience](assets/readme/shop-by-audience.png)

- **Audience filtering** — Every product has an `audience` field: Men, Women, Kids, or Unisex
- **Navbar audience links** — Desktop mega-menu and mobile sidebar include direct links to the catalog pre-filtered by audience (Men / Women / Kids / Unisex)
- **Works across sections** — Audience filter applies on the main Product Catalog, Sale page, and New Drops page
- **Unisex default** — Products default to Unisex when no specific audience applies

---

### Unique Features

#### 10. Battle Vest (Wishlist)

![Battle Vest Page](assets/readme/feature-battle-vest.png)

**Metal-themed wishlist system:**
- **One-click save** — Heart icon on every product card and detail page
- **Dedicated page** — Grid view of all saved items with total value
- **Total value calculation** — Combined worth of all wishlist items
- **Price drop notifications** — Email alert when a Battle Vest item goes on sale
- **Add to cart from vest** — Inline add-to-cart without re-browsing
- **Persistent across sessions** — Tied to user account, not browser cookies
- **Badge counter** — Real-time live count in the navigation bar

**Technical Implementation:**
- `OneToOne` relationship: User → BattleVest (auto-created via Django signal on registration)
- `ManyToMany` through table: BattleVest → Products via BattleVestItem
- AJAX endpoints for instant add/remove with JSON responses
- Unique constraint: each product can only be added once per vest

#### 11. The Vault (Community Gallery)

![Vault Gallery](assets/readme/feature-vault-gallery.png)

**User-generated content platform built around two areas:**

**Community Gallery (left panel)**
- **Photo Grid** — All approved community photos displayed in a responsive grid
- **Photo Submissions** — Upload images wearing HENDOSHI gear (drag-and-drop or file picker, max 15MB)
- **Caption & Tagging** — Up to 800-character caption with product tagging
- **Like System** — Authenticated users can like any approved photo
- **Voting System** — Authenticated users can upvote/downvote grid photos to influence the featuring algorithm; votes are visible on each card via the hover overlay
- **Pagination** — 12 photos per page

**This Week's Featured Carousel (right sidebar)**
- **Auto-Featured Picks** — The site automatically selects the top-scoring approved photos to feature each week; no admin action required
- **Scoring Algorithm** — Combines likes (×10), vote score (×15), and a recency boost (last 30 days) to rank candidates
- **Weekly Rotation** — Featured photos expire after 7 days; the cycle re-runs automatically whenever fewer than 2 featured photos are active
- **Minimum 2 Shown** — The carousel always shows at least 2 featured photos as long as approved photos exist; if the cycle has not yet run, the top-liked photos are used as a fallback
- **Click to View** — Each carousel card links directly to the full photo detail page; vote and like interactions are only available in the grid

**Moderation**

![Vault Admin Moderation](assets/readme/moderation-queue.png)
- **Moderation Queue** — All submissions are reviewed by an admin before appearing publicly
- **Approval/Rejection Notifications** — Email sent to the submitter on status change
![Approval/Rejection Notifications](assets/readme/approval-email-vault.png)
- **Featured Notification** — When a photo is selected as one of the week's featured picks, the submitter receives a congratulatory email
![Featured Notifications](assets/readme/featured-email-vault.png)

**Hall of Fame**

![Vault Hall of Fame](assets/readme/feature-vault-hof.png)
- Displays every photo that has ever been featured, ordered by most-recently featured first
- Once a photo earns a featured slot it remains in the Hall of Fame permanently, even after its feature window expires
- If no photos have ever been featured yet, the Hall of Fame shows the top-scored approved photos as a fallback so the page is never empty
- Authenticated users can like and upvote/downvote photos directly from the Hall of Fame grid

**Submission Workflow:**

![Vault Submit Form](assets/readme/feature-vault-submit.png)

1. User uploads photo (drag-and-drop or file picker, max 15MB, JPG/PNG only)
2. Adds caption (up to 800 characters) and tags products worn
3. Accepts the Vault Commandments and submits for review
4. Admin approves or rejects (with reason) the photo from the moderation queue
5. User receives an email notification with the outcome
6. Approved photos appear immediately in the public community gallery
7. Each week the algorithm automatically selects the highest-scoring approved photos to feature in the carousel; featured submitters are notified by email

#### 12. Seasonal Themes

![Seasonal Theme Demo](assets/readme/feature-seasonal-theme.png)

**Dynamic site-wide animation system:**
- **12 Pre-built Themes** — Christmas, Valentine's Day, St. Patrick's Day, Halloween, New Year's, Mother's Day, Father's Day, 4th of July, Thanksgiving, Rock 'n' Roll, Celebration, Everyday
- **Particle Animations** — Canvas-based rendering: snowflakes, hearts, confetti, falling leaves, fireworks
- **Message Strips** — Scrolling announcement banners with custom gradient backgrounds and configurable scroll speed
- **Schedule System** — Auto-activate/deactivate based on start and end date settings
- **Customisable Properties** — Animation speed (slow/normal/fast), particle density (light/medium/heavy)
- **Performance Optimised** — Canvas rendering pauses when browser tab is inactive, reduced density on mobile
- **Custom CSS Injection** — Advanced users can add custom CSS rules to any theme

**Admin Controls:**

![Admin Control Themes](assets/readme/admin-control-themes.png)
- Toggle themes on/off instantly
- Set start/end dates for automatic scheduling
- Configure animation speed and density
- Preview theme in isolated window before publishing
- Add custom messages to the announcement strip

#### 13. Product Reviews & Ratings

![Product Reviews](assets/readme/feature-reviews.png)

**Comprehensive review system:**
- **Star Ratings** — 1–5 stars with interactive visual selector
- **Written Reviews** — Text feedback up to 2,000 characters
- **Photo Uploads** — Up to 3 images per review with thumbnail gallery
- **Verified Purchase Badge** — Automatically shown for confirmed buyers
- **Helpful Votes** — Community-driven quality ranking (one vote per user per review)
- **Admin Reply** — Admin can add official responses to reviews
- **Admin Moderation** — Pending → Approved → Published workflow with rejection notes
- **Aggregated Statistics** — Average rating, review count, and per-star distribution chart

#### 14. Email Communications & Notifications

![Newsletter Popup](assets/readme/feature-newsletter-popup.png)

All transactional and marketing emails are sent via **Anymail + Resend**. Every email is a fully branded HTML template with HENDOSHI styling, the pug skull motif, and a one-click unsubscribe link.

**Complete list of emails sent to customers:**

| # | Email | Trigger | Template |
|---|-------|---------|----------|
| 1 | **Email Verification** | New account signup (allauth) | Allauth built-in |
| 2 | **Password Reset** | "Forgot password" request | Allauth built-in |
| 3 | **Newsletter Opt-In Confirmation** | Subscribing to newsletter | `newsletter_confirmation.html` |
| 4 | **Welcome Email** | Confirmed newsletter subscription | `newsletter_welcome.html` |
| 5 | **Order Confirmation** | Successful checkout payment | Checkout signal |
| 6 | **Shipping Notification** | Admin marks order as Shipped | Order status update |
| 7 | **Abandoned Cart Reminder 1** | 24 hours after cart abandoned | `cart_reminder_1.html` |
| 8 | **Abandoned Cart Reminder 2** | 48 hours after cart abandoned | `cart_reminder_2.html` |
| 9 | **Abandoned Cart Reminder 3** | 72 hours after cart abandoned | `cart_reminder_3.html` |
| 10 | **Price Drop Alert** | Battle Vest item goes on sale | `price_drop.html` |
| 11 | **Back in Stock** | Out-of-stock product restocked | `back_in_stock.html` |
| 12 | **Vault Photo Approved** | Admin approves a Vault submission | `photo_approved.html` |
| 13 | **Vault Photo Rejected** | Admin rejects a Vault submission | `photo_rejected.html` |
| 14 | **Vault Photo Featured** | Photo selected for carousel | `photo_featured.html` |

**Email screenshots:**

![Newsletter Opt-In Confirmation](assets/readme/email-newsletter-confirmation.png)
![Welcome Email with Discount Code](assets/readme/welcome-email.png)
![Order Confirmation Email](assets/readme/email-confirmation.png)
![Shipping Notification Email](assets/readme/shipping-notification.png)
![Abandoned Cart Email](assets/readme/abandoned-cart.png)
![Price Drop Alert Email](assets/readme/price-drop.png)
![Back in Stock Email](assets/readme/back-in-stock.png)
![Vault Photo Approved Email](assets/readme/email-vault-approved.png)
![Vault Photo Rejected Email](assets/readme/email-vault-rejected.png)
![Vault Photo Featured Email](assets/readme/email-vault-featured.png)

**Newsletter subscription flow:**

![Newsletter Popup Modal](assets/readme/feature-newsletter-popup.png)
![Subscription Confirmation](assets/readme/subscription-confirm.png)

- **Newsletter Popup** — Glassmorphic modal appears after 1 minute on first visit (shown once per session)
- **Double Opt-In** — Confirmation email required before subscriber is activated (GDPR compliant)
- **Welcome Email** — Sent on confirmation, includes a 10% discount code as a thank-you
- **Abandoned Cart Recovery** — 3-email drip sequence: 24h, 48h, and 72h reminders with cart contents

**Notification Preferences:**

![Notification Preferences](assets/readme/notification-preferences.png)

- Granular per-type toggles (sales, restock, vault status, vault featured, abandoned cart)
- Master on/off switch for all marketing emails
- One-click unsubscribe via token link in every email (no login required)
- GDPR-compliant consent tracking with timestamps
- Preferences managed from the Profile Dashboard

---

### Informational Pages

#### 15. About Page

![About Page](assets/readme/feature-about.png)

- Brand story and HENDOSHI mission
- Animated stat counters (designs, community members, orders)
- Customer testimonials section
- Light/dark mode supported

#### 16. FAQ Page

![FAQ Page](assets/readme/feature-faq.png)

- Accordion-style expandable questions and answers
- Sections covering: Ordering, Shipping, Returns, Sizing, Care Instructions

#### 17. Track Order

![Track Order](assets/readme/feature-track-order.png)

- Look up any order by order number and email address (no login required)
- Shows order status, tracking number, and carrier link
- Available carriers: DHL, DPD, An Post with direct tracking URL links

#### 18. Contact Page

![Contact Form](assets/readme/feature-contact.png)

- Contact form with name, email, subject, and message
- Admin receives email notification on submission
- Sender receives auto-reply confirmation
- Contact information cards (email, response time, location)

#### 19. Size Guide, Shipping & Returns

![Size Guide](assets/readme/feature-size-guide.png)

- **Size Guide** — Detailed measurements table for T-shirts, hoodies, accessories with fit description
- **Shipping Information** — Delivery options, estimated times, international rates, free shipping threshold
- **Returns Policy** — Step-by-step returns process, conditions, refund timeline

#### 20. Custom Error Pages

- **Custom 404 page** — Branded error page with pug skull mascot, "This page got lost in the void…" message, Back to Home and Shop Now CTAs, and an inline search form
![404 Error Page](assets/readme/feature-404-page.png)
- **Custom 500 page** — Server error page with consistent brand styling
![500 Error Page](assets/readme/feature-500-page.png)

#### 21. Cookie Consent Management

![Cookie Consent Banner](assets/readme/feature-cookie-banner.png)

![Cookie Settings Page](assets/readme/feature-cookie-settings.png)

- **Consent Banner** — Appears on first visit with Accept All / Manage options
- **Cookie Settings Page** — Granular toggle controls for each cookie category (Necessary, Analytics, Marketing, Functional)
- **Required cookies** — Cannot be disabled; clearly labelled
- **Persistent consent** — Settings saved to localStorage and respected on subsequent visits
- **GDPR compliant** — No non-essential cookies loaded before consent

---

### AI-Powered Features

#### 22. AI Content Generation (Google Gemini)

![AI Content Generation](assets/readme/feature-ai-generation.png)

Staff can generate content for products using Google Gemini AI via three built-in endpoints:

- **AI Product Description** (`/products/api/generate-product-description/`) — Generates SEO-optimised product descriptions based on product name, collection, and type
- **AI SEO Metadata** (`/products/api/generate-seo-meta/`) — Suggests meta title and description optimised for search engines
- **AI Design Story** (`/products/api/generate-design-story/`) — Creates a compelling narrative explaining the artwork's inspiration and meaning

**Technical Implementation:**
- Google Gemini Flash API via `GEMINI_API_KEY` environment variable
- AJAX endpoints returning JSON for seamless in-form injection
- Staff-only access protected by `@staff_member_required`
- Reduces time to publish new products from hours to minutes

---

### Admin Features

#### 23. Custom Admin Dashboard

![Admin Menu List](assets/readme/feature-admin-products.png)

**Superuser-only management panel (`/admin/` prefix URLs):**

**Product Management:**

![Admin Product List](assets/readme/feature-admin-products-page.png)
- Full CRUD: Create, view, edit, soft-delete (archive) products
- Bulk variant creation — Create up to 100+ variants from a single form by selecting all size/colour/audience combinations
- Product archiving — Hides product from frontend without deleting order history
- Rich text editor (CKEditor 5) for product descriptions and design stories
- Image upload with automatic WebP processing

**Order Management:**

![Admin Order Detail](assets/readme/feature-admin-orders.png)

- Order list with status filters (Pending, Confirmed, Processing, Shipped, Delivered, Cancelled)
- Order detail view with full line items, customer info, shipping address
- Status update with automatic history logging (who changed what, when, with notes)
- Tracking number and carrier input

**Discount Code Manager:**

![Discount Code Manager](assets/readme/discount-code-manager.png)

- Create percentage or fixed-amount discount codes
- Set minimum order value, maximum total uses, max uses per user, expiry date
- Attach promotional message to discount banner display

**Review Moderation:**

![Review Moderation](assets/readme/review-moderation.png)

- View pending reviews with product context
- Approve, reject (with note), or delete reviews
- Add official admin reply to any approved review

**Vault Moderation Queue:**

![Vault Moderation Queue](assets/readme/moderation-queue.png)

- View all pending Vault photo submissions
- Approve (AJAX, no page reload) or reject with reason message
- Feature a photo to appear in the carousel

**Seasonal Theme Configuration:**

![Seasonal Theme](assets/readme/seasonal-theme.png)

- Create, edit, activate, schedule, and preview themes
- Configure animation parameters and message strip content

**Newsletter Subscribers:**

![Newsletter Subscribers](assets/readme/newsletter-subscribers.png)

- View all confirmed subscribers with signup date and consent status

---

### Discount Codes & Promotional Banner

#### 24. Discount Codes & Promotional Banner

**Promotional Banner:**

![Discount Banner](assets/readme/feature-discount-banner.png)

- **Animated scrolling banner** — Fixed at the top of every page (above the navbar), continuously scrolling the active promotional message
- **Admin-controlled** — Message text and an optional call-to-action button (none / "Shop Now" / "Sale") set via the Discount Code Manager in the admin dashboard
- **Linked to discount codes** — When a discount code is active and has a `banner_message` set, that message appears in the banner automatically
- **Persistent visibility** — Shown on all pages so customers never miss an active promotion

**Customer-Facing Discount Code System:**

![Discount Code at Checkout](assets/readme/feature-discount-code-checkout.png)
![Discount Code at Checkout](assets/readme/feature-discount-code-checkout-1.png)

- **Cart drawer input** — Code field inline in the cart drawer; applies discount in real time with AJAX validation and clear error feedback
- **Percentage discounts** — Deduct a % from the order subtotal (e.g. `WELCOME10` → 10% off)
- **Fixed-amount discounts** — Deduct a flat € amount from the order subtotal
- **Minimum order value** — Admin can set a threshold below which the code is invalid
- **Expiry dates** — Codes can be time-limited; expired codes are rejected gracefully
- **Usage limits** — Global max uses and per-user max uses enforced at validation
- **Discount shown in checkout** — Applied saving displayed as a line item in the order summary and order confirmation email
- **Admin management** — Create, edit, deactivate, and monitor usage from the Custom Admin Dashboard

---

### Social Media Presence

#### 25. Social Media Channels

HENDOSHI maintains an active presence across four social media platforms. All links open in a new tab with `rel="noopener noreferrer"` for security. They are accessible from:
- The **footer** (all pages via `base.html`)
![Social Media Links Footer](assets/readme/feature-social-footer.png)
- The **mobile slide-in menu** (social links section at the bottom of the drawer)
![Social Media Links Mobile Menu](assets/readme/feature-social-mobile-menu.png)

| Platform | Handle | Link |
|----------|--------|------|
| **Instagram** | `@hendoshiart` | [![Instagram](https://img.shields.io/badge/Instagram-@hendoshiart-E1306C?style=for-the-badge&logo=instagram&logoColor=white)](https://instagram.com/hendoshiart) |
| **Facebook** | `hendoshiart` | [![Facebook](https://img.shields.io/badge/Facebook-hendoshiart-1877F2?style=for-the-badge&logo=facebook&logoColor=white)](https://www.facebook.com/hendoshiart) |
| **X (Twitter)** | `@hendoshiart` | [![X](https://img.shields.io/badge/X-@hendoshiart-000000?style=for-the-badge&logo=x&logoColor=white)](https://x.com/hendoshiart) |
| **Pinterest** | `hendoshiart` | [![Pinterest](https://img.shields.io/badge/Pinterest-hendoshiart-E60023?style=for-the-badge&logo=pinterest&logoColor=white)](https://ie.pinterest.com/hendoshiart/) |

---

## 🗄️ Database Schema

![ERD Diagram](assets/readme/database-erd.png)

[![Database ERD Diagram](https://img.shields.io/badge/Database-Full_Schema_ERD-CCFF00?style=for-the-badge)](https://dbdiagram.io/d/69c29cb4fb2db18e3bf1d0b4)

The project uses **PostgreSQL** with **33 custom models** across 8 Django applications featuring advanced patterns: auto-created signals, soft deletes, audit trails, image optimization, price/stock history tracking, and complex relationship management.


### Core Models

#### **Products App** (`products/`)
| Model | Purpose |
|-------|---------|
| `Collection` | Product categories (Skulls & Death, Weird Animals, Gym Designs, etc.) |
| `ProductType` | Runtime product types (T-Shirt, Hoodie, Sticker, Accessory) |
| `Product` | Main product entity with pricing, images, sale dates |
| `ProductVariant` | SKU-level inventory with size, colour, stock count |
| `DesignStory` | Narrative content for each product |
| `ProductImage` | Additional gallery images |
| `BattleVest` | Metal-themed wishlist (one per user, auto-created on registration) |
| `BattleVestItem` | Individual products saved in a Battle Vest |
| `ProductReview` | Customer reviews with rating, text, moderation status |
| `ReviewHelpful` | Tracks "helpful" votes per review per user |
| `ReviewImage` | Photo uploads attached to a review (max 3) |

#### **Checkout App** (`checkout/`)
| Model | Purpose |
|-------|---------|
| `Order` | Order header (number, customer, totals, payment & fulfilment status) |
| `OrderItem` | Line items: product, size, colour, quantity, price |
| `DiscountCode` | Promotional codes with type, value, limits, and expiry |
| `ShippingRate` | Available shipping options with price and free-shipping threshold |
| `OrderStatusLog` | Audit trail of every order status change |

#### **Profiles App** (`profiles/`)
| Model | Purpose |
|-------|---------|
| `UserProfile` | Extended user info | Default phone, address fields (OneToOne with Django User) |
| `Address` | Shipping addresses | Full address fields, is_default flag, multiple per user |
| `SavedPaymentMethod` | Card details | Last 4 digits only (masked), card brand, expiry, for display only — never stores raw card data |

#### **Notifications App** (`notifications/`)
| Model | Purpose |
|-------|---------|
| `NotificationPreference` | Per-user email toggle settings | Auto-created on registration, granular control per email type |
| `NewsletterSubscriber` | Newsletter email list | GDPR consent with timestamp, double opt-in token, activation flag |
| `PriceHistory` | Product price tracking | Snapshots historical prices for analytics and drop detection |
| `StockHistory` | Variant stock level changes | Tracks restock events for back-in-stock alerts |
| `PendingNotification` | Email queue | Status (pending/sent/failed), type (order, newsletter, price_drop, etc.), retry counter |
| `SentNotificationLog` | Audit log of all emails sent | Recipient, subject, sent timestamp, email template used |
| `AbandonedCartNotification` | Cart abandonment sequence | Tracks multiple reminder emails (24h, 48h, 72h), sequence number |

**Unique Features:**
- ✅ **Email queue system** — Async notifications with retry logic and error handling
- ✅ **Granular notification control** — Users toggle 5+ email types independently
- ✅ **GDPR compliance** — Double opt-in with confirmation tokens, one-click unsubscribe
- ✅ **Price/stock history** — Tracks temporal data for analytics and alerting
- ✅ **Abandoned cart sequences** — Multi-email recovery campaigns with increasing urgency

#### **Vault App** (`vault/`)
| Model | Purpose |
|-------|---------|
| `VaultPhoto` | Community gallery submissions | Image (auto-compressed), caption (800 chars max), uploader, moderation status (pending/approved/rejected), featured flag, feature count, like count, vote score, tagged products (ManyToMany) |

**Unique Features:**
- ✅ **Moderation workflow** — Pending → approved/rejected/featured transitions
- ✅ **Image compression** — Auto-resized to 1920px max on upload
- ✅ **Voting system** — Upvotes/downvotes with score tracking
- ✅ **Hall of Fame** — Photos with 10+ features get promoted to legendary status
- ✅ **Product tagging** — Link photos to products for cross-promotion

#### **Themes App** (`themes/`)
| Model | Purpose |
|-------|---------|
| `SeasonalTheme` | Animated seasonal configurations | Theme type (Christmas, Halloween, Valentine's, etc.), animation type, message strip text, gradient CSS, custom CSS rules, schedule (start_date, end_date), animation speed and density, is_active flag |

**Unique Features:**
- ✅ **Canvas-based animations** — 12 pre-built particle animation systems (snowflakes, confetti, hearts, leaves, fireworks)
- ✅ **Auto-scheduling** — Themes activate/deactivate based on date range
- ✅ **Performance optimised** — Pauses animations when browser tab inactive, reduced density on mobile
- ✅ **Custom CSS injection** — Advanced users can add bespoke CSS rules to any theme

#### **Cart App** (2 models)
| Model | Purpose |
|-------|---------|
| `Cart` | Shopping session basket | User or session-based, used for guest checkout |
| `CartItem` | Products in cart | Product variant, quantity, price snapshot |

**Unique Features:**
- ✅ **Session persistence** — Guest carts survive page reload, merge on login
- ✅ **Real-time updates** — AJAX endpoints update totals without page refresh
- ✅ **Variant-specific inventory** — Stock checked per size/colour/audience combination

#### **Notifications App** (`notifications/`)
| Model | Purpose |
|-------|---------|
| `NotificationPreference` | Per-user email toggle settings (auto-created on registration) |
| `NewsletterSubscriber` | Newsletter email list with GDPR consent and confirmation token |
| `PriceHistory` | Tracks price changes for products |
| `StockHistory` | Tracks variant stock changes for restock alerts |
| `PendingNotification` | Queue of notifications awaiting dispatch |
| `SentNotificationLog` | Audit log of all sent notifications |
| `AbandonedCartNotification` | Tracks cart abandonment sequences |

#### **Vault App** (`vault/`)
| Model | Purpose |
|-------|---------|
| `VaultPhoto` | Community gallery submissions with moderation, likes, votes, featuring |

#### **Themes App** (`themes/`)
| Model | Purpose |
|-------|---------|
| `SeasonalTheme` | Theme configuration: type, schedule, animation settings, strip messages |

### Key Relationships

```
User (Django Auth)
├── 1:1 → UserProfile (auto-created via signal)
├── 1:1 → BattleVest (auto-created via signal)
│   └── M:M → Product (through BattleVestItem)
├── 1:1 → NotificationPreference (auto-created via signal)
├── 1:M → Order
│   └── 1:M → OrderItem → ProductVariant → Product
├── 1:M → ProductReview
│   └── 1:M → ReviewImage
├── 1:M → VaultPhoto
│   └── M:M → Product (tagged products)
└── 1:M → Address

Collection
└── 1:M → Product
    ├── 1:M → ProductVariant
    ├── 1:M → ProductReview
    └── 1:1 → DesignStory

ProductVariant
├── → StockHistory
└── → PendingNotification (restock)

Product → PriceHistory
```

---

## 🛠️ Technologies Used

### Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.11+ | Primary programming language |
| **Django** | 5.2 | Web framework (MVT architecture) |
| **PostgreSQL** | 14+ | Relational database |
| **Psycopg2** | 2.9 | PostgreSQL adapter |
| **Django AllAuth** | 65.x | Authentication: registration, email verification |
| **Django Unfold** | 0.76 | Modern admin interface UI |
| **django-ckeditor** | 6.7 | Rich text editor for admin product content |
| **django-compressor** | 4.6 | CSS/JS minification and offline compression |
| **django-storages** | 1.14 | Storage backend abstraction layer |
| **python-decouple** | 3.8 | Environment variable management via `.env` |
| **Pillow** | 12.x | Image processing (resize, compress on upload) |
| **Gunicorn** | 23.x | WSGI production server |
| **dj-database-url** | 3.x | Parse `DATABASE_URL` environment variable |
| **whitenoise** | 6.x | Serve static files in production |

### Frontend
| Technology | Version | Purpose |
|-----------|---------|---------|
| **HTML5** | — | Semantic markup |
| **CSS3** | — | Custom styling with CSS variables and glassmorphism |
| **JavaScript (ES6+)** | — | Interactive features, AJAX, canvas animations |
| **Bootstrap** | 5.3 | Responsive grid and UI components |
| **Font Awesome** | 6.4 | Icon library |
| **Google Fonts** | — | Montserrat typeface |

### Payment & Email
| Technology | Purpose |
|-----------|---------|
| **Stripe API** | Payment processing with SCA/3D Secure support |
| **Anymail** | Email backend abstraction layer |
| **Resend** | Transactional email delivery (production) |

### AI & Analytics
| Technology | Purpose |
|-----------|---------|
| **Google Gemini API** | AI-powered content generation: product descriptions, SEO meta tags, design stories |
| **Google Analytics 4 (GA4)** | Traffic analytics, user behaviour tracking, conversion measurement |
| **Google Tag Manager (GTM)** | Tag management for analytics events and marketing pixels |

### Storage & CDN
| Technology | Purpose |
|-----------|---------|
| **Cloudinary** | Cloud storage and CDN for media files (production) |
| **django-cloudinary-storage** | Django integration for Cloudinary |

### Development & Quality Tools
| Tool | Purpose |
|-----|---------|
| **Git** | Version control |
| **GitHub** | Code repository and project management |
| **VS Code** | IDE |
| **djlint** | HTML template linting and formatting |
| **Chrome DevTools** | Debugging and performance profiling |
| **Lighthouse** | Performance, accessibility, SEO auditing |
| **W3C Validator** | HTML validation |
| **Jigsaw (W3C)** | CSS validation |
| **JSHint** | JavaScript linting |
| **Flake8** | Python PEP8 compliance |

### Deployment & Hosting
| Service | Purpose |
|--------|---------|
| **Render.com** | Application hosting (web service) |
| **Render PostgreSQL** | Managed PostgreSQL database hosting |
| **Cloudinary** | Media file storage and CDN |

---

## 🧪 Testing

[![Testing Documentation](https://img.shields.io/badge/Testing-Full_Documentation-9C27B0?style=for-the-badge)](TESTING.md)

### Testing Methodologies

1. **Manual Testing** — User story validation, feature testing, cross-browser compatibility
2. **Automated Testing** — Django unit tests for models, views, forms
3. **Responsive Testing** — Chrome DevTools device emulation, real device testing
4. **Accessibility Testing** — WAVE, Lighthouse, keyboard navigation
5. **Performance Testing** — Lighthouse scores, load time analysis
6. **Security Testing** — OWASP guidelines, SQL injection prevention, XSS protection

### Test Coverage Summary

| Area | Tests | Coverage |
|------|-------|----------|
| Models | 45 tests | 97–100% |
| Views | 260+ tests | 77–94% |
| Forms | 40+ tests | 89–97% |
| Management Commands | 30+ tests | 78–100% |
| Admin Actions | 25+ tests | 88–100% |
| Signals & Context Processors | 15+ tests | 90–95% |
| JavaScript | Manual | N/A |
| **Overall** | **773 tests** | **80%** |

### Browser Compatibility

✅ **Chrome** (v120+)
✅ **Firefox** (v118+)
✅ **Safari** (v17+)
✅ **Edge** (v120+)
✅ **Mobile Safari** (iOS 16+)
✅ **Chrome Mobile** (Android 12+)

### Lighthouse Scores

| Page | Performance | Accessibility | Best Practices | SEO |
|------|-------------|---------------|----------------|-----|
| Homepage | 94 | 98 | 100 | 100 |
| Products | 91 | 97 | 100 | 100 |
| Product Detail | 88 | 96 | 100 | 100 |
| Checkout | 93 | 98 | 100 | 92 |

---

## 🚀 Deployment

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Stripe Account (test keys for development)
- Cloudinary Account (for media storage)
- Resend Account (for email delivery in production)
- Git

### Local Development Setup

1. **Clone the repository:**
```bash
git clone https://github.com/dannykadoshi/Hendoshi_Ecommerce.git
cd Hendoshi_Ecommerce
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create `.env` file** in the project root:
```bash
# Django
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost/hendoshi_db

# Stripe
STRIPE_PUBLIC_KEY=pk_test_xxxxx
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# Email (development — uses Django console backend if not set)
RESEND_API_KEY=re_xxxxxx
DEFAULT_FROM_EMAIL=noreply@hendoshi.com

# Cloudinary (optional in development)
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
```

5. **Run migrations:**
```bash
python manage.py migrate
```

6. **Create superuser:**
```bash
python manage.py createsuperuser
```

7. **Run development server:**
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`

### Production Deployment (Render.com)

1. **Create a Render.com account** and connect your GitHub repository
2. **Create a new Web Service** — Select your repository
3. **Set environment variables** in the Render dashboard:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key (generate a new one) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `hendoshi-ecommerce.onrender.com` |
| `DATABASE_URL` | Connection string from Render PostgreSQL (auto-provided) |
| `STRIPE_PUBLIC_KEY` | Stripe live/test public key |
| `STRIPE_SECRET_KEY` | Stripe live/test secret key |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook endpoint secret |
| `CLOUDINARY_URL` | Cloudinary connection string |
| `RESEND_API_KEY` | Resend email API key |
| `DEFAULT_FROM_EMAIL` | Sender email address |

4. **Configure build command:**
```bash
./build.sh
```

5. **Configure start command:**
```bash
gunicorn hendoshi_store.wsgi:application
```

6. **Deploy** — Render auto-deploys on every push to the main branch

### Static Files Configuration

**Development:** Django's development server serves static files automatically
**Production:** WhiteNoise serves static files; Cloudinary serves media files via CDN

### Database Migrations in Production

```bash
# Run via Render shell or include in build.sh
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

---

## 📈 SEO & Marketing

### Search Engine Optimisation

#### Technical SEO
- ✅ **sitemap.xml** — Django sitemap framework covering products, collections, and static pages
- ✅ **robots.txt** — Configured to allow crawling, disallow admin/checkout
- ✅ **Meta descriptions** — Unique descriptions for all major pages
- ✅ **Semantic HTML** — Proper heading hierarchy (H1→H2→H3), article/section tags
- ✅ **Image alt text** — Descriptive alt attributes on all images
- ✅ **Structured data** — JSON-LD schema for Product, Offer, and AggregateRating
- ✅ **`rel` attributes on external links** — All outbound links include `rel="noopener noreferrer"` for security and SEO; social media links (Instagram, TikTok, Facebook) carry `rel="noopener noreferrer"`; user-generated Vault photo links include `rel="nofollow"` to prevent link equity leakage to unmoderated content

#### `rel` Attributes on External Resources

All links pointing to external resources implement the correct `rel` attributes:

| Link Type | Example | `rel` Value | Reason |
|-----------|---------|-------------|--------|
| Social media links (footer/schema) | `<a href="https://instagram.com/hendoshiart" rel="noopener noreferrer">` | `noopener noreferrer` | Security: prevents window.opener hijacking; SEO: signals external resource |
| CDN/third-party resources | `<link rel="preconnect" href="https://fonts.googleapis.com">` | `preconnect` | Performance: pre-establishes connection |
| Social share buttons | Facebook/Twitter share links | `noopener noreferrer` | Security: external tab isolation |
| Stripe payment link | Stripe documentation | `noopener noreferrer` | Security: external site isolation |
| Carrier tracking links | DHL, DPD, An Post | `noopener noreferrer` | Security: external site isolation |

#### On-Page SEO
- **Title tags** — Format: "Product Name | HENDOSHI - Wear Your Weird"
- **Meta keywords** — Relevant terms (metal apparel, skull t-shirts, alternative fashion)
- **Internal linking** — Cross-linking between products, collections, and Design Stories
- **URL structure** — Clean, descriptive slugs (`/products/skull-crossbones-tee/`)

### Marketing Strategies

#### Web Marketing Evidence

**Facebook Business Page**

![Facebook Business Page](assets/readme/marketing-facebook-page.png)
![Facebook Business Page](assets/readme/marketing-facebook-page-1.png)

**Newsletter Confirmation Email**

![Newsletter Confirmation Email](assets/readme/email-newsletter-confirmation.png)

**robots.txt Screenshot**

![robots.txt Screenshot](assets/readme/seo-robots-txt.png)

**sitemap.xml.txt Screenshot**

![sitemap.xml Screenshot](assets/readme/seo-sitemap-xml.png)

#### Social Media
- **Instagram** (@hendoshiart) — Visual product showcase and community photos, daily posts and Stories
- **Facebook** (HENDOSHI Art) — Product announcements, events, contests, Facebook Ads (future)
- **TikTok** (@hendoshiart) — Product reveals, design process, trend participation

#### Email Marketing
- **Newsletter** — Weekly drop notifications, exclusive offers, Vault highlights
- **Abandoned cart recovery** — 3-email sequence increasing urgency (24h, 48h, 72h)
- **Transactional** — Order confirmation, shipping notification, invoice
- **Triggered alerts** — Price drop (Battle Vest), back-in-stock

#### Content Marketing
- **Design Stories** — Long-form narrative content for each product, SEO-indexed
- **Community Gallery** — User-generated content indexed by Google, drives organic traffic
- **FAQ & Info Pages** — Informational content targeting "metal t-shirt sizing", "how to return" etc.

#### Paid Advertising (Future — Year 2)
- Facebook/Instagram Ads targeting alternative fashion interests
- Google Shopping Ads for product listings
- Influencer partnerships in metal/gothic communities

### GDPR Compliance
- ✅ **Cookie consent** — Banner with Accept All / Manage Settings options
- ✅ **Cookie settings page** — Granular per-category controls
- ✅ **Privacy policy** — Linked in footer, describes all data collected
- ✅ **Double opt-in** — Newsletter requires email confirmation
- ✅ **One-click unsubscribe** — Token-based, no login required
- ✅ **Consent logging** — Timestamp and consent flag stored per subscriber

---

## 🏆 Credits

### Design & Development
**Danny Kadoshi** — Full-stack development, UI/UX design, branding, original artwork

### Code Resources
- **Code Institute** — Django e-commerce walkthrough project structure and learning material
- **Bootstrap Documentation** — Component reference and grid system
- **Django Documentation** — Model relationships, authentication, signals, best practices
- **Stripe Documentation** — Payment integration guides and webhook handling
- **AllAuth Documentation** — Authentication customisation and email configuration
- **Anymail Documentation** — Resend email backend integration
- **GitHub Copilot** — AI-powered code analysis and debugging assistance.

### Design Inspiration
- **Disturbia Clothing** — Alternative fashion e-commerce UX patterns
- **BlackCraft Cult** — Dark aesthetic and community engagement approach
- **Killstar** — Gothic product photography style

### Media & Assets
- **Original Artwork** — All skull, animal, and gym designs created by Danny Kadoshi
- **Font Awesome** — Icon library (free tier)
- **Google Fonts** — Montserrat typeface

### Tools & Libraries
- **Coolors** — Colour palette generation
- **Favicon.io** — Favicon generator
- **TinyPNG** — Image compression
- **Convertio** — WebP image conversion
- **dbdiagram.io** — Entity Relationship Diagram creation
- **Balsamiq** / pen and paper — Wireframe creation
- **Google Gemini** — AI image generation for product mockups and design assets

---

## 🙏 Acknowledgments

### Special Thanks

**Code Institute** — For the comprehensive curriculum, and project assessment framework. This project represents the culmination of the Full Stack Development diploma.

**HENDOSHI Community** — Beta testers who provided feedback on navigation, checkout flow, and mobile responsiveness throughout development.

**Open Source Community** — For maintaining Django, Bootstrap, AllAuth, Stripe libraries, and the countless open-source packages that power this project.


---

## 📧 Contact

**Developer:** Danny Kadoshi

**Email:** admin@hendoshi.com

[![GitHub Profile](https://img.shields.io/badge/GitHub-@dannykadoshi-000000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/dannykadoshi)
[![Live Site](https://img.shields.io/badge/Live_Site-hendoshi--store.onrender.com-ff1493?style=for-the-badge)](https://hendoshi-store.onrender.com)

---

<div align="center">

**Built with 🖤 for Code Institute's Full Stack Development Diploma**

[![GitHub stars](https://img.shields.io/github/stars/dannykadoshi/Hendoshi_Ecommerce?style=social)](https://github.com/dannykadoshi/Hendoshi_Ecommerce/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/dannykadoshi/Hendoshi_Ecommerce?style=social)](https://github.com/dannykadoshi/Hendoshi_Ecommerce/network/members)

**WEAR YOUR WEIRD** 🖤⚡

</div>
