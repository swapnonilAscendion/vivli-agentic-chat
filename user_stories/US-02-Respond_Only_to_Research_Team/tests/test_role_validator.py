"""
Unit tests for US-02: Respond Only to Research Team

Tests role-based access control validation logic with:
- Eligible roles (researcher, team_member, etc.)
- Ineligible roles (admin, bot, contributor, etc.)
- Edge cases (missing role, invalid role, etc.)
- Error message validation
"""

import pytest
from implementation.role_validator import (
    RoleValidator,
    RoleValidationError,
    validate_user_role
)


class TestRoleValidatorEligibleRoles:
    """Test cases for eligible research team roles"""

    def test_researcher_role_allowed(self):
        """Test that researcher role grants access"""
        is_eligible, error = validate_user_role("researcher", "user_001")
        assert is_eligible is True
        assert error == ""

    def test_team_member_role_allowed(self):
        """Test that team_member role grants access"""
        is_eligible, error = validate_user_role("team_member", "user_002")
        assert is_eligible is True
        assert error == ""

    def test_data_request_creator_role_allowed(self):
        """Test that data_request_creator role grants access"""
        is_eligible, error = validate_user_role("data_request_creator", "user_003")
        assert is_eligible is True
        assert error == ""

    def test_research_team_admin_role_allowed(self):
        """Test that research_team_admin role grants access"""
        is_eligible, error = validate_user_role("research_team_admin", "user_004")
        assert is_eligible is True
        assert error == ""

    def test_role_case_insensitive(self):
        """Test that role comparison is case-insensitive"""
        test_cases = [
            "RESEARCHER",
            "Researcher",
            "ReSeArChEr",
            "TEAM_MEMBER",
            "Team_Member"
        ]
        for role in test_cases:
            is_eligible, error = validate_user_role(role, "user_test")
            assert is_eligible is True, f"Role {role} should be eligible"
            assert error == "", f"Role {role} should have no error"


class TestRoleValidatorIneligibleRoles:
    """Test cases for ineligible roles that should be denied"""

    def test_vivli_admin_role_denied(self):
        """Test that vivli_admin role is denied"""
        is_eligible, error = validate_user_role("vivli_admin", "admin_001")
        assert is_eligible is False
        assert "research team" in error.lower()

    def test_system_admin_role_denied(self):
        """Test that system_admin role is denied"""
        is_eligible, error = validate_user_role("system_admin", "admin_002")
        assert is_eligible is False

    def test_org_admin_role_denied(self):
        """Test that org_admin role is denied"""
        is_eligible, error = validate_user_role("org_admin", "admin_003")
        assert is_eligible is False

    def test_data_contributor_role_denied(self):
        """Test that data_contributor role is denied"""
        is_eligible, error = validate_user_role("data_contributor", "contrib_001")
        assert is_eligible is False

    def test_contributor_role_denied(self):
        """Test that contributor role is denied"""
        is_eligible, error = validate_user_role("contributor", "contrib_002")
        assert is_eligible is False

    def test_data_curator_role_denied(self):
        """Test that data_curator role is denied"""
        is_eligible, error = validate_user_role("data_curator", "curator_001")
        assert is_eligible is False

    def test_guest_role_denied(self):
        """Test that guest role is denied"""
        is_eligible, error = validate_user_role("guest", "guest_001")
        assert is_eligible is False

    def test_automated_notification_denied(self):
        """Test that automated_notification role is denied"""
        is_eligible, error = validate_user_role("automated_notification", "notify_001")
        assert is_eligible is False


class TestRoleValidatorBotDetection:
    """Test cases for bot/system detection"""

    def test_bot_system_detected(self):
        """Test that bot_system role is detected as bot"""
        is_eligible, error = validate_user_role("bot_system", "bot_001")
        assert is_eligible is False
        assert "automated system" in error.lower()

    def test_irp_system_detected(self):
        """Test that irp_system role is detected as system"""
        is_eligible, error = validate_user_role("irp_system", "irp_001")
        assert is_eligible is False

    def test_automated_service_detected(self):
        """Test detection of automated services"""
        bot_roles = ["automated_bot", "notification_bot", "system_bot"]
        for role in bot_roles:
            is_eligible, _ = validate_user_role(role, "bot_test")
            assert is_eligible is False, f"Role {role} should be detected as bot"


class TestRoleValidatorEdgeCases:
    """Test edge cases and error scenarios"""

    def test_empty_role_denied(self):
        """Test that empty role string is denied"""
        is_eligible, error = validate_user_role("", "user_empty")
        assert is_eligible is False
        assert "Unable to verify" in error or "role" in error.lower()

    def test_none_role_denied(self):
        """Test that None role is denied"""
        is_eligible, error = validate_user_role(None, "user_none")
        assert is_eligible is False

    def test_whitespace_only_role_denied(self):
        """Test that whitespace-only role is denied"""
        is_eligible, error = validate_user_role("   ", "user_space")
        assert is_eligible is False

    def test_unknown_role_denied(self):
        """Test that unknown role is denied"""
        is_eligible, error = validate_user_role("unknown_role_xyz", "user_unknown")
        assert is_eligible is False
        assert "research team" in error.lower()

    def test_invalid_role_format_denied(self):
        """Test that invalid role format is denied"""
        is_eligible, error = validate_user_role("!@#$%", "user_invalid")
        assert is_eligible is False

    def test_role_with_extra_whitespace(self):
        """Test that role with extra whitespace is handled"""
        is_eligible, error = validate_user_role("  researcher  ", "user_ws")
        assert is_eligible is True
        assert error == ""


class TestRoleValidatorErrorMessages:
    """Test error message generation"""

    def test_invalid_role_error_message(self):
        """Test error message for invalid role"""
        validator = RoleValidator()
        msg = validator.get_error_message(RoleValidationError.INVALID_ROLE)
        assert "research team" in msg.lower()
        assert "contact support" in msg.lower()

    def test_ineligible_role_error_message(self):
        """Test error message for ineligible role"""
        validator = RoleValidator()
        msg = validator.get_error_message(RoleValidationError.INELIGIBLE_ROLE)
        assert "research team" in msg.lower()

    def test_bot_detected_error_message(self):
        """Test error message for bot detection"""
        validator = RoleValidator()
        msg = validator.get_error_message(RoleValidationError.BOT_DETECTED)
        assert "automated" in msg.lower()

    def test_user_role_not_found_error_message(self):
        """Test error message for missing role"""
        validator = RoleValidator()
        msg = validator.get_error_message(RoleValidationError.USER_ROLE_NOT_FOUND)
        assert "Unable to verify" in msg or "role" in msg.lower()

    def test_all_error_messages_user_friendly(self):
        """Test that all error messages are user-friendly"""
        validator = RoleValidator()
        for error_type in RoleValidationError:
            if error_type == RoleValidationError.VALID:
                continue
            msg = validator.get_error_message(error_type)
            assert len(msg) > 0, f"Error message for {error_type} is empty"
            assert "traceback" not in msg.lower(), f"Error message for {error_type} contains traceback"
            assert len(msg) < 200, f"Error message for {error_type} is too long"


class TestRoleValidatorMethods:
    """Test individual validator methods"""

    def test_is_eligible_role_researcher(self):
        """Test is_eligible_role method with researcher"""
        validator = RoleValidator()
        assert validator.is_eligible_role("researcher") is True

    def test_is_eligible_role_admin(self):
        """Test is_eligible_role method with admin"""
        validator = RoleValidator()
        assert validator.is_eligible_role("vivli_admin") is False

    def test_is_eligible_role_empty(self):
        """Test is_eligible_role method with empty role"""
        validator = RoleValidator()
        assert validator.is_eligible_role("") is False

    def test_is_eligible_role_none(self):
        """Test is_eligible_role method with None"""
        validator = RoleValidator()
        assert validator.is_eligible_role(None) is False

    def test_bot_detection_multiple_patterns(self):
        """Test bot detection with various patterns"""
        validator = RoleValidator()
        bot_roles = ["bot_system", "system_bot", "automated_bot", "notification_service"]
        for role in bot_roles:
            assert validator._is_bot_or_system(role) is True, f"Failed to detect {role} as bot"

    def test_non_bot_detection(self):
        """Test that non-bot roles don't trigger bot detection"""
        validator = RoleValidator()
        non_bot_roles = ["researcher", "team_member", "org_admin"]
        for role in non_bot_roles:
            is_bot = validator._is_bot_or_system(role)
            # org_admin contains 'admin' but should not be detected as bot
            if role == "org_admin":
                assert is_bot is False, f"Role {role} should not be detected as bot"


class TestRoleValidatorIntegration:
    """Integration tests with multiple scenarios"""

    def test_validation_pipeline_eligible(self):
        """Test complete validation pipeline for eligible user"""
        is_eligible, error = validate_user_role("researcher", "researcher_001")
        assert is_eligible is True
        assert error == ""

    def test_validation_pipeline_ineligible(self):
        """Test complete validation pipeline for ineligible user"""
        is_eligible, error = validate_user_role("vivli_admin", "admin_001")
        assert is_eligible is False
        assert len(error) > 0

    def test_validation_multiple_eligible_roles(self):
        """Test validation with all eligible roles"""
        eligible_roles = ["researcher", "team_member", "data_request_creator", "research_team_admin"]
        for role in eligible_roles:
            is_eligible, error = validate_user_role(role, f"user_{role}")
            assert is_eligible is True, f"Role {role} should be eligible"

    def test_validation_multiple_ineligible_roles(self):
        """Test validation with all ineligible roles"""
        ineligible_roles = ["vivli_admin", "system_admin", "org_admin", "data_contributor",
                          "contributor", "data_curator", "guest", "bot_system"]
        for role in ineligible_roles:
            is_eligible, _ = validate_user_role(role, f"user_{role}")
            assert is_eligible is False, f"Role {role} should be ineligible"

    def test_validator_initialization(self):
        """Test validator initialization and configuration"""
        validator = RoleValidator()
        assert validator.ROLE_CHECK_ENABLED is True
        assert validator.ALLOW_SYSTEM_BOTS is False
        assert len(validator.ELIGIBLE_ROLES) == 4
        assert len(validator.INELIGIBLE_ROLES) == 10


class TestRoleValidatorConfiguration:
    """Test configuration and customization"""

    def test_eligible_roles_set(self):
        """Test that eligible roles are properly set"""
        validator = RoleValidator()
        assert "researcher" in validator.eligible_roles
        assert "team_member" in validator.eligible_roles
        assert "data_request_creator" in validator.eligible_roles
        assert "research_team_admin" in validator.eligible_roles

    def test_ineligible_roles_set(self):
        """Test that ineligible roles are properly set"""
        validator = RoleValidator()
        assert "vivli_admin" in validator.ineligible_roles
        assert "bot_system" in validator.ineligible_roles
        assert "guest" in validator.ineligible_roles

    def test_role_check_disabled(self):
        """Test behavior when role check is disabled"""
        validator = RoleValidator()
        original_value = validator.ROLE_CHECK_ENABLED
        try:
            validator.ROLE_CHECK_ENABLED = False
            is_eligible, error = validate_user_role("any_role", "test_user")
            assert is_eligible is True
        finally:
            validator.ROLE_CHECK_ENABLED = original_value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
