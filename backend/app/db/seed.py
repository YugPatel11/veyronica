"""Database seed script with Faker en_IN data.

EPIC-03-T12: Seed development data with story characters.
Usage: python -m app.db.seed
"""

from __future__ import annotations

import asyncio
import sys
from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import hash_password
from app.db.models.agent import Agent
from app.db.models.connector import Connector
from app.db.models.llm import ModelTier, TokenBudget
from app.db.models.policy import Policy
from app.db.models.user import User, UserRole
from app.db.session import async_session_factory


# ── Dev Users (story characters from an Indian university) ───────────────────

DEV_USERS = [
    {
        "id": "usr_admin_001",
        "email": "admin@nexus.edu",
        "password": "nexus_admin_2026",
        "full_name": "Dr. Ananya Krishnan",
        "roles": ["admin"],
    },
    {
        "id": "usr_faculty_001",
        "email": "faculty@nexus.edu",
        "password": "nexus_faculty_2026",
        "full_name": "Dr. Riya Patel",
        "roles": ["faculty"],
    },
    {
        "id": "usr_faculty_002",
        "email": "rajesh@nexus.edu",
        "password": "nexus_faculty_2026",
        "full_name": "Prof. Rajesh Sharma",
        "roles": ["faculty"],
    },
    {
        "id": "usr_approver_001",
        "email": "approver@nexus.edu",
        "password": "nexus_approver_2026",
        "full_name": "Dr. Meera Iyer",
        "roles": ["approver"],
    },
    {
        "id": "usr_operator_001",
        "email": "operator@nexus.edu",
        "password": "nexus_operator_2026",
        "full_name": "Vikram Desai",
        "roles": ["operator"],
    },
]

# ── Agents ───────────────────────────────────────────────────────────────────

DEV_AGENTS = [
    {
        "id": "agt_master_001",
        "name": "Master Agent",
        "slug": "master",
        "description": "Orchestrates workflow execution, plans tasks, and coordinates specialist agents.",
        "agent_type": "master",
        "default_model_tier": "premium",
    },
    {
        "id": "agt_ingestion_001",
        "name": "Ingestion Agent",
        "slug": "ingestion",
        "description": "Handles file upload, validation, OCR/vision extraction of answers.",
        "agent_type": "ingestion",
        "default_model_tier": "standard",
    },
    {
        "id": "agt_evaluation_001",
        "name": "Evaluation Agent",
        "slug": "evaluation",
        "description": "Marks answers against rubrics with confidence scoring.",
        "agent_type": "evaluation",
        "default_model_tier": "premium",
    },
    {
        "id": "agt_analysis_001",
        "name": "Analysis Agent",
        "slug": "analysis",
        "description": "Generates performance trends, risk scoring, and analytics.",
        "agent_type": "analysis",
        "default_model_tier": "standard",
    },
    {
        "id": "agt_communication_001",
        "name": "Communication Agent",
        "slug": "communication",
        "description": "Drafts parent emails, stakeholder communications.",
        "agent_type": "communication",
        "default_model_tier": "economy",
    },
    {
        "id": "agt_verifier_001",
        "name": "Verifier Agent",
        "slug": "verifier",
        "description": "Performs marks sum checks, range validation, confidence threshold verification.",
        "agent_type": "verifier",
        "default_model_tier": "economy",
    },
    {
        "id": "agt_copilot_001",
        "name": "Copilot Agent",
        "slug": "copilot",
        "description": "Interactive assistant with fixed tool set for admin queries.",
        "agent_type": "copilot",
        "default_model_tier": "standard",
    },
    {
        "id": "agt_security_001",
        "name": "Security Agent",
        "slug": "security",
        "description": "Detects security incidents, gathers context, recommends responses.",
        "agent_type": "security",
        "default_model_tier": "standard",
    },
]

# ── Connectors ───────────────────────────────────────────────────────────────

DEV_CONNECTORS = [
    {
        "id": "conn_erp_001",
        "name": "Campus ERP",
        "slug": "campus-erp",
        "connector_type": "erp",
        "base_url": "http://mock-erp:8001",
        "health_status": "healthy",
        "risk_level": "high",
    },
    {
        "id": "conn_lms_001",
        "name": "Learning Management System",
        "slug": "lms",
        "connector_type": "lms",
        "base_url": "http://mock-lms:8002",
        "health_status": "healthy",
        "risk_level": "medium",
    },
    {
        "id": "conn_crm_001",
        "name": "Student CRM",
        "slug": "student-crm",
        "connector_type": "crm",
        "base_url": "http://mock-crm:8003",
        "health_status": "healthy",
        "risk_level": "medium",
    },
    {
        "id": "conn_email_001",
        "name": "Email (SMTP)",
        "slug": "email-smtp",
        "connector_type": "email",
        "base_url": "http://mailpit:1025",
        "health_status": "healthy",
        "risk_level": "low",
    },
    {
        "id": "conn_storage_001",
        "name": "Object Storage (MinIO)",
        "slug": "object-storage",
        "connector_type": "storage",
        "base_url": "http://minio:9000",
        "health_status": "healthy",
        "risk_level": "low",
    },
]

# ── Model Tiers ──────────────────────────────────────────────────────────────

DEV_MODEL_TIERS = [
    {
        "tier": "economy",
        "model_name": "gpt-4o-mini",
        "provider": "openai",
        "input_cost_per_1k": 0.00015,
        "output_cost_per_1k": 0.0006,
        "max_context_tokens": 128000,
    },
    {
        "tier": "standard",
        "model_name": "gpt-4o",
        "provider": "openai",
        "input_cost_per_1k": 0.0025,
        "output_cost_per_1k": 0.01,
        "max_context_tokens": 128000,
    },
    {
        "tier": "premium",
        "model_name": "gpt-4.1",
        "provider": "openai",
        "input_cost_per_1k": 0.002,
        "output_cost_per_1k": 0.008,
        "max_context_tokens": 1000000,
    },
]


async def seed_database() -> None:
    """Seed development data into the database."""
    async with async_session_factory() as session:
        # Check if already seeded
        result = await session.execute(
            text("SELECT COUNT(*) FROM users")
        )
        count = result.scalar()
        if count and count > 0:
            print("⚠ Database already seeded. Skipping.")
            return

        print("🌱 Seeding development data...")

        # Users + Roles
        for user_data in DEV_USERS:
            user = User(
                id=user_data["id"],
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                full_name=user_data["full_name"],
                is_active=True,
            )
            session.add(user)
            for role in user_data["roles"]:
                session.add(UserRole(user_id=user_data["id"], role=role))
        print(f"  ✓ {len(DEV_USERS)} users created")

        # Agents
        for agent_data in DEV_AGENTS:
            session.add(Agent(**agent_data))
        print(f"  ✓ {len(DEV_AGENTS)} agents registered")

        # Connectors
        for conn_data in DEV_CONNECTORS:
            session.add(Connector(**conn_data))
        print(f"  ✓ {len(DEV_CONNECTORS)} connectors configured")

        # Model Tiers
        for tier_data in DEV_MODEL_TIERS:
            session.add(ModelTier(**tier_data))
        print(f"  ✓ {len(DEV_MODEL_TIERS)} model tiers set up")

        # Global Token Budget
        session.add(TokenBudget(
            scope="global",
            daily_limit=500000,
            monthly_limit=10000000,
            daily_cost_limit_usd=50.0,
            monthly_cost_limit_usd=500.0,
        ))
        print("  ✓ Global token budget configured")

        await session.commit()
        print("✅ Seed complete!")


if __name__ == "__main__":
    asyncio.run(seed_database())
