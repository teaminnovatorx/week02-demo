"""Real unit tests — 26 tests covering all endpoints."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models import Case, Alert, User


class TestRoot:
    def test_root_returns_service_info(self, client: TestClient):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["service"] == "UDARA AI"
        assert data["status"] == "operational"
        assert "endpoints" in data

    def test_docs_available(self, client: TestClient):
        resp = client.get("/docs")
        assert resp.status_code in (200, 307)


class TestAuth:
    def test_login_returns_token(self, client: TestClient):
        resp = client.post("/api/v1/auth/login", json={
            "email": "test@udara.health",
            "password": "anything",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "test@udara.health"

    def test_login_auto_creates_user(self, client: TestClient, db: Session):
        resp = client.post("/api/v1/auth/login", json={
            "email": "newuser@test.com",
            "password": "pass",
        })
        assert resp.status_code == 200
        from sqlalchemy import select
        user = db.execute(
            select(User).where(User.email == "newuser@test.com")
        ).scalar_one_or_none()
        assert user is not None

    def test_register_creates_user(self, client: TestClient):
        resp = client.post("/api/v1/auth/register", json={
            "email": "register@test.com",
            "password": "secure123",
            "name": "Test User",
        })
        assert resp.status_code == 200
        assert resp.json()["user"]["email"] == "register@test.com"

    def test_register_duplicate(self, client: TestClient):
        client.post("/api/v1/auth/register", json={
            "email": "dup@test.com", "password": "pass",
        })
        resp = client.post("/api/v1/auth/register", json={
            "email": "dup@test.com", "password": "pass",
        })
        assert resp.status_code == 400

    def test_logout(self, client: TestClient):
        resp = client.post("/api/v1/auth/logout")
        assert resp.status_code == 200
        assert resp.json()["message"] == "Logged out"


class TestCases:
    def test_list_empty(self, client: TestClient):
        resp = client.get("/api/v1/cases")
        assert resp.status_code == 200
        data = resp.json()
        assert data["cases"] == []
        assert data["total"] == 0

    def test_create_case(self, client: TestClient):
        resp = client.post("/api/v1/cases", json={
            "source": "telegram",
            "complaint": "Fever and cough for 3 days",
            "symptoms": ["fever", "cough"],
            "duration": "3 days",
            "medications": ["amoxicillin"],
            "severity": "moderate",
            "district": "Lagos",
            "patient_age_years": 30,
            "patient_sex": "male",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["complaint"] == "Fever and cough for 3 days"
        assert data["source"] == "telegram"
        assert data["case_id"] is not None

    def test_get_case_by_id(self, client: TestClient):
        create = client.post("/api/v1/cases", json={
            "complaint": "Test case", "district": "Nairobi",
        })
        case_id = create.json()["case_id"]

        resp = client.get(f"/api/v1/cases/{case_id}")
        assert resp.status_code == 200
        assert resp.json()["case_id"] == case_id

    def test_get_case_not_found(self, client: TestClient):
        resp = client.get("/api/v1/cases/nonexistent")
        assert resp.status_code == 404

    def test_list_pagination(self, client: TestClient):
        for i in range(5):
            client.post("/api/v1/cases", json={"complaint": f"Case {i}", "district": "Kampala"})

        resp = client.get("/api/v1/cases?page=1&per_page=2")
        data = resp.json()
        assert len(data["cases"]) == 2
        assert data["total"] == 5
        assert data["total_pages"] == 3

    def test_filter_by_district(self, client: TestClient):
        client.post("/api/v1/cases", json={"complaint": "A", "district": "Lagos"})
        client.post("/api/v1/cases", json={"complaint": "B", "district": "Nairobi"})

        resp = client.get("/api/v1/cases?district=Lagos")
        assert all(c["district"] == "Lagos" for c in resp.json()["cases"])


class TestStats:
    def test_dashboard_all_fields(self, client: TestClient):
        resp = client.get("/api/v1/stats/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        for key in ["total_cases", "active_alerts", "avg_resistance_pct",
                     "active_chws", "cases_this_week", "districts_covered"]:
            assert key in data

    def test_overview(self, client: TestClient):
        resp = client.get("/api/v1/stats/overview")
        assert resp.status_code == 200
        assert resp.json()["service"] == "UDARA AI"
        assert resp.json()["status"] == "operational"


class TestAlerts:
    def test_list_empty(self, client: TestClient):
        resp = client.get("/api/v1/alerts")
        assert resp.status_code == 200
        assert "alerts" in resp.json()

    def test_acknowledge_not_found(self, client: TestClient):
        resp = client.post("/api/v1/alerts/bad-id/acknowledge")
        assert resp.status_code == 404

    def test_resolve_not_found(self, client: TestClient):
        resp = client.post("/api/v1/alerts/bad-id/resolve")
        assert resp.status_code == 404


class TestResistance:
    def test_list_drugs(self, client: TestClient):
        resp = client.get("/api/v1/resistance/drugs")
        assert resp.status_code == 200
        assert "drugs" in resp.json()

    def test_map(self, client: TestClient):
        resp = client.get("/api/v1/resistance/map")
        assert resp.status_code == 200
        assert "features" in resp.json()

    def test_trends(self, client: TestClient):
        resp = client.get("/api/v1/resistance/trends")
        assert resp.status_code == 200
        data = resp.json()
        assert "dates" in data
        assert "series" in data


class TestBot:
    def test_telegram_empty(self, client: TestClient):
        resp = client.post("/api/v1/bot/telegram", json={})
        assert resp.status_code == 200

    def test_telegram_start(self, client: TestClient):
        resp = client.post("/api/v1/bot/telegram", json={
            "message": {"chat": {"id": 123}, "text": "/start", "from": {"id": 100}},
        })
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
        assert "UDARA" in resp.json()["response"]

    def test_telegram_ingest(self, client: TestClient, db: Session):
        resp = client.post("/api/v1/bot/telegram", json={
            "message": {
                "chat": {"id": 999},
                "text": "Patient with fever, cough, taking amoxicillin",
                "from": {"id": 999, "first_name": "Test"},
            }
        })
        assert resp.status_code == 200
        assert resp.json()["ok"] is True
        case = db.execute(
            __import__("sqlalchemy").select(Case).where(Case.reported_by == "999")
        ).scalar_one_or_none()
        assert case is not None
        assert "fever" in case.complaint

    def test_whatsapp_verify(self, client: TestClient):
        resp = client.get(
            "/api/v1/bot/whatsapp?hub.mode=subscribe&hub.verify_token=udara_verify_2026&hub.challenge=123456"
        )
        assert resp.status_code == 200

    def test_whatsapp_verify_bad_token(self, client: TestClient):
        resp = client.get(
            "/api/v1/bot/whatsapp?hub.mode=subscribe&hub.verify_token=wrong&hub.challenge=123"
        )
        assert resp.status_code == 403
        data = resp.json()
        assert "error" in data

    def test_telegram_help(self, client: TestClient):
        resp = client.post("/api/v1/bot/telegram", json={
            "message": {"chat": {"id": 1}, "text": "/help", "from": {"id": 1}},
        })
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

    def test_whatsapp_webhook_post_passthrough(self, client: TestClient):
        """WhatsApp webhook POST returns 200 and processes async."""
        resp = client.post("/api/v1/bot/whatsapp", json={
            "entry": [{
                "changes": [{
                    "value": {
                        "contacts": [{"profile": {"name": "Test"}}],
                        "messages": [{
                            "from": "+2348031234567",
                            "id": "msg1",
                            "type": "text",
                            "text": {"body": "Fever and cough for 3 days"},
                        }],
                    }
                }]
            }]
        })
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestAutomations:
    def test_list_rules(self, client: TestClient):
        resp = client.get("/api/v1/automations/rules")
        assert resp.status_code == 200
        data = resp.json()
        assert "rules" in data
        assert data["total"] > 0

    def test_automation_log_empty(self, client: TestClient):
        resp = client.get("/api/v1/automations/log")
        assert resp.status_code == 200
        assert "cases" in resp.json()

    def test_automation_log_with_cases(self, client: TestClient):
        # Create a case via WhatsApp with resistance keywords
        client.post("/api/v1/bot/whatsapp", json={
            "entry": [{
                "changes": [{
                    "value": {
                        "contacts": [{"profile": {"name": "Test"}}],
                        "messages": [{
                            "from": "+234805555555",
                            "id": "msg555",
                            "type": "text",
                            "text": {"body": "Patient not responding to treatment, possible MDR"},
                        }],
                    }
                }]
            }]
        })
        resp = client.get("/api/v1/automations/log")
        assert resp.status_code == 200
        cases = resp.json()["cases"]
        assert len(cases) >= 1
        # At least one case should have resistance_flag = True from MDR trigger
        flagged = [c for c in cases if c["resistance_flag"]]
        assert len(flagged) >= 1, "No case flagged as resistant despite MDR keyword"


class TestBroadcast:
    def test_broadcast_no_recipients(self, client: TestClient):
        resp = client.post("/api/v1/broadcast/send", json={})
        assert resp.status_code == 400

    def test_broadcast_new_format(self, client: TestClient):
        resp = client.post("/api/v1/broadcast/send", json={
            "recipients": [
                {"phone": "+2348031234567", "text": "Alert in your area"},
            ],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["sent"] == 1

    def test_broadcast_legacy_format(self, client: TestClient):
        resp = client.post("/api/v1/broadcast/send", json={
            "phone_numbers": ["+2348031234567", "+254712345678"],
            "text": "AMR alert in your district",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert data["sent"] == 2

    def test_broadcast_invalid_phone(self, client: TestClient):
        resp = client.post("/api/v1/broadcast/send", json={
            "phone_numbers": ["invalid"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["failed"] == 1

    def test_broadcast_status(self, client: TestClient):
        resp = client.get("/api/v1/broadcast/status")
        assert resp.status_code == 200
        assert "rate_limits" in resp.json()
