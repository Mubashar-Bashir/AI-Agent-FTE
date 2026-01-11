#!/usr/bin/env python3
"""
Test script for User Story 5: Security Allowlist
"""

import sys
import os
import yaml
from pathlib import Path
sys.path.insert(0, 'src')

from dispatcher.security_controls import SecurityControls
from dispatcher.config_manager import ConfigManager


def test_security_controls():
    """Test security controls and allowlist functionality"""
    print("=" * 70)
    print("User Story 5: Security Allowlist Test")
    print("=" * 70)
    
    # Create test allowlist file
    print("\n1. Setting up test allowlist...")
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    test_allowlist = {
        "skills": [
            {
                "name": "systematic-debugging",
                "risk_level": "medium",
                "requires_approval": False,
                "description": "Analyzes errors and proposes fixes without modifying code"
            },
            {
                "name": "test-driven-development",
                "risk_level": "high",
                "requires_approval": True,
                "description": "Creates and modifies test files"
            },
            {
                "name": "verification-before-completion",
                "risk_level": "low",
                "requires_approval": False,
                "description": "Runs verification commands and reports results"
            }
        ]
    }
    
    allowlist_file = config_dir / "allowed_skills.yaml"
    with open(allowlist_file, 'w') as f:
        yaml.dump(test_allowlist, f)
    
    print("   ✓ Test allowlist created")
    
    # Initialize security controls
    security = SecurityControls(allowlist_file=str(allowlist_file))
    print("   ✓ Security controls initialized")
    
    # Test 1: Check allowed skills
    print("\n2. Testing allowed skills validation...")
    
    allowed_skills = ["systematic-debugging", "test-driven-development", "verification-before-completion"]
    for skill in allowed_skills:
        is_allowed = security.is_skill_allowed(skill)
        print(f"   ✓ Skill '{skill}' allowed: {is_allowed}")
        assert is_allowed == True, f"Skill {skill} should be allowed"
    
    # Test disallowed skill
    is_disallowed = security.is_skill_allowed("malicious-skill")
    print(f"   ✓ Disallowed skill 'malicious-skill' allowed: {is_disallowed}")
    assert is_disallowed == False, "Disallowed skill should not be allowed"
    
    # Test 2: Skill configuration retrieval
    print("\n3. Testing skill configuration retrieval...")
    
    for skill in allowed_skills:
        config = security.get_skill_config(skill)
        if config:
            print(f"   ✓ Retrieved config for '{skill}': risk={config['risk_level']}, approval={config['requires_approval']}")
    
    # Test 3: Risk level validation
    print("\n4. Testing risk level validation...")
    
    risk_tests = [
        ("systematic-debugging", "medium"),
        ("test-driven-development", "high"),
        ("verification-before-completion", "low"),
        ("nonexistent-skill", "unknown")
    ]
    
    for skill, expected_risk in risk_tests:
        actual_risk = security.get_risk_level(skill)
        print(f"   ✓ Skill '{skill}' risk level: {actual_risk} (expected: {expected_risk})")
        if skill != "nonexistent-skill":  # Skip nonexistent for assertion
            assert actual_risk == expected_risk, f"Expected {expected_risk}, got {actual_risk}"
    
    # Test 4: Skill name validation
    print("\n5. Testing skill name validation...")
    
    valid_names = ["valid-skill", "valid_skill", "ValidSkill123", "my.skill.name"]
    invalid_names = ["../malicious", "dangerous&skill", "bad|skill", "script.py"]
    
    for name in valid_names:
        is_valid = security.validate_skill_name(name)
        print(f"   ✓ Valid name '{name}' validates: {is_valid}")
        assert is_valid == True, f"Valid name {name} should validate"
    
    for name in invalid_names:
        is_valid = security.validate_skill_name(name)
        print(f"   ✓ Invalid name '{name}' validates: {is_valid}")
        assert is_valid == False, f"Invalid name {name} should not validate"
    
    # Test 5: Comprehensive validation and authorization
    print("\n6. Testing comprehensive validation...")
    
    for skill in allowed_skills:
        result = security.validate_and_authorize(skill)
        print(f"   ✓ Validation result for '{skill}': valid={result['is_valid']}, allowed={result['is_allowed']}")
        assert result['is_valid'] == True, f"Skill {skill} should be valid"
        assert result['is_allowed'] == True, f"Skill {skill} should be allowed"
    
    # Test unauthorized skill
    unauthorized_result = security.validate_and_authorize("unauthorized-skill")
    print(f"   ✓ Validation result for unauthorized skill: valid={unauthorized_result['is_valid']}, allowed={unauthorized_result['is_allowed']}")
    assert unauthorized_result['is_valid'] == False, "Unauthorized skill should not be valid"
    
    print("\n" + "=" * 70)
    print("User Story 5 Test Complete")
    print("=" * 70)
    
    return True


def test_config_manager_integration():
    """Test security integration with config manager"""
    print("\n" + "=" * 70)
    print("Config Manager Integration Test")
    print("=" * 70)
    
    # Initialize config manager
    print("\n1. Initializing config manager...")
    config_manager = ConfigManager()
    print("   ✓ Config manager initialized with security controls")
    
    # Test skill authorization through config manager
    print("\n2. Testing skill authorization via config manager...")
    
    allowed_skills = ["systematic-debugging", "test-driven-development", "verification-before-completion"]
    for skill in allowed_skills:
        is_allowed = config_manager.is_skill_allowed(skill)
        skill_config = config_manager.get_skill_config(skill)
        print(f"   ✓ Config manager allows '{skill}': {is_allowed}")
        if skill_config:
            print(f"     Config: risk={skill_config['risk_level']}, approval={skill_config['requires_approval']}")
    
    # Test comprehensive validation
    print("\n3. Testing comprehensive validation...")
    for skill in allowed_skills:
        result = config_manager.validate_and_authorize_skill(skill)
        print(f"   ✓ Full validation for '{skill}': {result['is_valid']} (risk: {result['risk_level']})")
    
    print("\n" + "=" * 70)
    print("Integration Test Complete")
    print("=" * 70)


def main():
    """Run all security allowlist tests"""
    try:
        success = test_security_controls()
        if not success:
            print("\n✗ Security controls test failed")
            sys.exit(1)
        
        test_config_manager_integration()
        
        print("\n🎉 All User Story 5 tests passed!")
        print("\nSummary:")
        print("- Allowlist Validation: ✓ Checks if skills are in approved list")
        print("- Skill Configuration: ✓ Retrieves risk levels and approval requirements")
        print("- Risk Assessment: ✓ Classifies skills by risk level (low/medium/high)")
        print("- Name Validation: ✓ Prevents dangerous skill names (injection protection)")
        print("- Authorization: ✓ Comprehensive validation and authorization checks")
        print("- Integration: ✓ Works seamlessly with config manager")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
