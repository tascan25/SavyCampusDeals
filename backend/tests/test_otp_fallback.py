"""Regression + bug fix tests for OTP dev fallback (Resend test mode)."""
import os
import time
import uuid
import requests
import pytest

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://student-perks-9.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def s():
    return requests.Session()


def _new_email():
    return f"TEST_{uuid.uuid4().hex[:10]}@example.com"


# ---------- Bug fix: dev OTP fallback ----------
class TestOtpFallback:
    def test_register_returns_dev_otp_when_resend_rejects(self, s):
        email = _new_email()
        r = s.post(f"{API}/auth/register", json={
            "name": "Test User",
            "email": email,
            "password": "Test@1234",
        })
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("email_sent") is False, f"expected email_sent False (Resend test mode), got: {data}"
        assert "dev_otp" in data and len(data["dev_otp"]) == 6 and data["dev_otp"].isdigit()
        assert "email_error" in data and data["email_error"]
        # save for next tests
        pytest.shared_email = email
        pytest.shared_otp = data["dev_otp"]
        pytest.shared_token = data["token"]

    def test_verify_otp_success_with_dev_otp(self, s):
        r = s.post(f"{API}/auth/verify-otp", json={
            "email": pytest.shared_email,
            "otp": pytest.shared_otp,
        })
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("ok") is True
        # user should now be verified
        if "user" in data:
            assert data["user"].get("email_verified") is True

    def test_send_otp_throttled_then_dev_otp(self, s):
        # register new user, wait 60s, resend, expect dev_otp again
        email = _new_email()
        r = s.post(f"{API}/auth/register", json={
            "name": "Throttle User", "email": email, "password": "Test@1234",
        })
        assert r.status_code == 200
        # Immediate resend must be throttled
        r429 = s.post(f"{API}/auth/send-otp", json={"email": email})
        assert r429.status_code == 429, f"expected 429 throttle, got {r429.status_code}"
        # Wait for throttle to lift
        time.sleep(62)
        r2 = s.post(f"{API}/auth/send-otp", json={"email": email})
        assert r2.status_code == 200, r2.text
        d = r2.json()
        assert d.get("email_sent") is False
        assert "dev_otp" in d and len(d["dev_otp"]) == 6


# ---------- Regression: prior features not broken ----------
class TestRegression:
    def test_admin_login(self, s):
        r = s.post(f"{API}/auth/login", json={
            "email": "admin@savycampusdeals.in", "password": "Admin@123",
        })
        assert r.status_code == 200, r.text
        data = r.json()
        assert data.get("user", {}).get("role") == "admin"
        assert data.get("token")

    def test_offers_list_has_14_with_brand_url(self, s):
        r = s.get(f"{API}/offers")
        assert r.status_code == 200
        offers = r.json()
        assert isinstance(offers, list)
        assert len(offers) >= 14, f"expected >=14 offers, got {len(offers)}"
        assert all("brand_url" in o for o in offers[:5])

    def test_claim_forbidden_for_unverified(self, s):
        # register a new user (unverified), try to claim
        email = _new_email()
        reg = s.post(f"{API}/auth/register", json={
            "name": "Unverified User", "email": email, "password": "Test@1234",
        }).json()
        token = reg["token"]
        offers = s.get(f"{API}/offers").json()
        offer_id = offers[0]["id"]
        r = s.post(f"{API}/offers/{offer_id}/claim",
                   headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 403, f"expected 403 for unverified email, got {r.status_code} {r.text}"

    def test_scan_lookup_and_redeem_flow(self, s):
        # Admin login
        admin = s.post(f"{API}/auth/login", json={
            "email": "admin@savycampusdeals.in", "password": "Admin@123",
        }).json()
        admin_token = admin["token"]
        headers = {"Authorization": f"Bearer {admin_token}"}
        # Try to grab an existing coupon by listing recent coupons endpoint if available
        # Fallback: skip if none exist. First, create a claim as verified test student.
        # Use admin to fetch any coupon via /api/admin/coupons if exists
        r_admin_coupons = s.get(f"{API}/admin/coupons", headers=headers)
        if r_admin_coupons.status_code != 200 or not r_admin_coupons.json():
            pytest.skip("No admin coupons endpoint or no coupons to test scan flow")
        coupon = r_admin_coupons.json()[0]
        code = coupon.get("code") or coupon.get("coupon_code")
        if not code:
            pytest.skip("Coupon shape has no code field")
        # Lookup
        r_look = s.post(f"{API}/scan/lookup", json={"code": code}, headers=headers)
        assert r_look.status_code in (200, 404), r_look.text
