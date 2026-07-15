# SavyCampusDeals — Product Requirements

## Original Problem Statement
India's student verification & discount platform. Verified college students access exclusive offers from restaurants, cafés, brands, gyms, edtech. Indian version of UNiDAYS. Premium Gen-Z aesthetic.

## Stack (approved by user)
- Frontend: React 19 + Tailwind + Framer Motion + TanStack Query + Sonner + lucide-react + qrcode.react
- Backend: FastAPI + MongoDB (motor) + JWT (PyJWT) + bcrypt + qrcode + resend
- Auth: JWT email/password (httpOnly cookie + Bearer token fallback)
- Emails: Resend (onboarding@resend.dev sender)
- Verification: Auto-approve in MVP (real admin review to be added)

## User Personas
- **Student**: Verifies with college ID, browses offers, claims coupons, uses digital student card at partner outlets.
- **Admin**: Seeded account; future: approves verifications, manages offers.
- **Business (future)**: Creates offers, redeems coupons via QR scanner.

## Implemented (Feb 2026)
- Landing page: hero, brand marquee, how-it-works, popular deals, testimonials, FAQ, CTA, footer
- Auth: signup, login, logout, /me, forgot-password (Resend email), reset-password, verify-email-token
- Student verification: upload college ID + selfie → auto-approve → issues SCD-YYYY-XXXXXX number + expiry
- Digital Student Card: 3D-tilt, holographic gradient, animated verified badge, QR code with student payload
- Offers: 12 seeded (Nike, Apple, Spotify, Notion, Zomato, cult.fit, Blue Tokai, Zudio, Coursera, YouTube, BookMyShow, Ray-Ban) across 6 categories, search + category + sort filters
- Offer detail: image, terms, validity, claim CTA (blocks unverified users)
- Claim → generates unique coupon SCD-XXXXXXXX + QR data URI, tracked per user
- My Coupons page with modal QR view
- Saved offers, Dashboard with stats, referral code, quick links
- Cookie auth (samesite=none secure) + Bearer localStorage fallback for cross-origin

## P0 Backlog (deferred to next iteration)
- Business dashboard (create offer, view analytics, QR scanner to redeem coupons)
- Admin dashboard (manual verification review UI, offer/business/user management)
- Real email/OTP flow (email verification link is generated but MVP auto-verifies via upload)
- Referral tracking + rewards points earned events
- Push notifications, offer expiry reminders

## P1
- Gamification (badges, streaks, leaderboards)
- Reviews on offers
- Google Login (Emergent-managed)
- Nearby offers with geolocation
- Coupon redemption endpoint (business scans QR → validates + marks redeemed)

## P2
- Multi-language (Hindi, Tamil, Telugu)
- Campus ambassador program
- Merchant self-serve onboarding

## Testing
- iteration_1.json: 20/20 pass (14 backend, 4 frontend, 100%)
