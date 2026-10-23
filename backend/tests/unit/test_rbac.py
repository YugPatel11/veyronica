"""Unit tests for RBAC permission checks."""

from __future__ import annotations

from app.core.rbac import Permission, get_permissions_for_roles


class TestRolePermissions:
    """Tests for the role → permission matrix."""

    def test_admin_has_all_permissions(self) -> None:
        perms = get_permissions_for_roles(["admin"])
        assert perms == set(Permission)

    def test_faculty_has_limited_permissions(self) -> None:
        perms = get_permissions_for_roles(["faculty"])
        assert Permission.WORKFLOWS_RUN in perms
        assert Permission.COPILOT_USE in perms
        assert Permission.USERS_MANAGE not in perms
        assert Permission.SETTINGS_MANAGE not in perms

    def test_approver_can_decide_approvals(self) -> None:
        perms = get_permissions_for_roles(["approver"])
        assert Permission.APPROVALS_DECIDE in perms
        assert Permission.WORKFLOWS_RUN not in perms

    def test_operator_can_verify_audit(self) -> None:
        perms = get_permissions_for_roles(["operator"])
        assert Permission.AUDIT_VERIFY in perms
        assert Permission.SECURITY_MANAGE in perms
        assert Permission.APPROVALS_DECIDE not in perms

    def test_multiple_roles_union_permissions(self) -> None:
        perms = get_permissions_for_roles(["faculty", "approver"])
        assert Permission.WORKFLOWS_RUN in perms  # from faculty
        assert Permission.APPROVALS_DECIDE in perms  # from approver

    def test_unknown_role_grants_no_permissions(self) -> None:
        perms = get_permissions_for_roles(["nonexistent_role"])
        assert len(perms) == 0

    def test_empty_roles_grants_no_permissions(self) -> None:
        perms = get_permissions_for_roles([])
        assert len(perms) == 0
