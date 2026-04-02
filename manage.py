#!/usr/bin/env python3
"""
manage.py — CLI for administrative tasks in BehaveDrift API.
Provides subcommands to provision tenants, generate API keys, reset passwords, etc.
"""

import asyncio
import argparse
import sys
import secrets
import bcrypt

from app.database import AsyncSessionLocal, engine
from app.models.tenant import Tenant
from sqlalchemy import select


def hash_secret(secret: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(secret.encode("utf-8"), salt).decode("utf-8")


async def create_tenant(name: str):
    """Creates a new tenant and generates an API key."""
    async with AsyncSessionLocal() as db:
        tenant_id = f"ten_test{secrets.token_hex(4)}"  # Demo ID generation

        # Generate API key
        raw_key = f"sk_{secrets.token_urlsafe(32)}"
        hashed_key = hash_secret(raw_key)

        tenant = Tenant(
            id=tenant_id, name=name, api_key_hash=hashed_key, is_active=True
        )
        db.add(tenant)
        await db.commit()

        print("\n" + "=" * 50)
        print("Tenant Created Successfully!")
        print(f"Name: {name}")
        print(f"Tenant ID: {tenant_id}")
        print(f"API Key: {raw_key}")
        print("Keep the API Key safe, it will not be shown again.")
        print("=" * 50 + "\n")


async def reset_api_key(tenant_id: str):
    """Resets the API key for an existing tenant."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = result.scalar_one_or_none()
        if not tenant:
            print(f"Error: Tenant '{tenant_id}' not found.")
            sys.exit(1)

        raw_key = f"sk_{secrets.token_urlsafe(32)}"
        tenant.api_key_hash = hash_secret(raw_key)

        await db.commit()

        print("\n" + "=" * 50)
        print("API Key Reset Successfully!")
        print(f"Tenant ID: {tenant_id}")
        print(f"Name: {tenant.name}")
        print(f"New API Key: {raw_key}")
        print("=" * 50 + "\n")


async def list_tenants():
    """Lists all registered tenants."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Tenant))
        tenants = result.scalars().all()

        print(f"\nTotal Tenants: {len(tenants)}")
        print(f"{'ID':<20} | {'Name':<30} | {'Active'}")
        print("-" * 65)
        for t in tenants:
            active = "Yes" if t.is_active else "No"
            print(f"{t.id:<20} | {t.name:<30} | {active}")
        print()


def main():
    parser = argparse.ArgumentParser(description="BehaveDrift Management CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # create-tenant
    parser_create = subparsers.add_parser(
        "create-tenant", help="Create a new tenant with an API key"
    )
    parser_create.add_argument("name", type=str, help="Name of the tenant organization")

    # reset-key
    parser_reset = subparsers.add_parser(
        "reset-key", help="Reset the API key for an existing tenant"
    )
    parser_reset.add_argument("tenant_id", type=str, help="The ID of the tenant")

    # list-tenants
    subparsers.add_parser("list-tenants", help="List all registered tenants")

    args = parser.parse_args()

    try:
        if args.command == "create-tenant":
            asyncio.run(create_tenant(args.name))
        elif args.command == "reset-key":
            asyncio.run(reset_api_key(args.tenant_id))
        elif args.command == "list-tenants":
            asyncio.run(list_tenants())
    finally:
        asyncio.run(engine.dispose())


if __name__ == "__main__":
    main()
