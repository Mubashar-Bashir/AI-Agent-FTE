"""
Regex pattern validator with ReDoS prevention
"""

import re
from typing import Tuple

from .exceptions import InvalidPatternError


class RegexValidator:
    """
    Validates regex patterns to prevent ReDoS (Regular Expression Denial of Service) attacks
    """
    
    # Maximum pattern length
    MAX_PATTERN_LENGTH = 200
    
    # Maximum nesting depth for groups
    MAX_NESTING_DEPTH = 5
    
    # Maximum number of capture groups
    MAX_CAPTURE_GROUPS = 10
    
    # Dangerous pattern constructs
    DANGEROUS_PATTERNS = [
        (r'\([^)]*[+*]\)[+*]', "Nested quantifiers (e.g., (a+)+ or (a*)*)"),
        (r'\([^)]*\|[^)]*\|[^)]*\|[^)]*\|[^)]*\|', "Excessive alternation"),
        (r'\(\?[=!<].*[+*]', "Lookahead/lookbehind with quantifiers"),
    ]
    
    @classmethod
    def validate(cls, pattern: str) -> Tuple[bool, str]:
        """
        Validate a regex pattern for safety
        
        Args:
            pattern: The regex pattern to validate
            
        Returns:
            Tuple of (is_valid, error_message)
            
        Raises:
            InvalidPatternError: If pattern is dangerous
        """
        # Check length
        if len(pattern) > cls.MAX_PATTERN_LENGTH:
            raise InvalidPatternError(
                f"Pattern too long: {len(pattern)} chars (max: {cls.MAX_PATTERN_LENGTH})"
            )
        
        # Check for dangerous constructs
        for dangerous_pattern, description in cls.DANGEROUS_PATTERNS:
            if re.search(dangerous_pattern, pattern):
                raise InvalidPatternError(
                    f"Dangerous pattern detected: {description}"
                )
        
        # Check nesting depth
        nesting_depth = cls._check_nesting_depth(pattern)
        if nesting_depth > cls.MAX_NESTING_DEPTH:
            raise InvalidPatternError(
                f"Pattern nesting too deep: {nesting_depth} (max: {cls.MAX_NESTING_DEPTH})"
            )
        
        # Check capture group count
        capture_count = pattern.count('(') - pattern.count('(?:')
        if capture_count > cls.MAX_CAPTURE_GROUPS:
            raise InvalidPatternError(
                f"Too many capture groups: {capture_count} (max: {cls.MAX_CAPTURE_GROUPS})"
            )
        
        # Try to compile the pattern
        try:
            re.compile(pattern)
        except re.error as e:
            raise InvalidPatternError(f"Invalid regex pattern: {e}")
        
        return True, "Pattern is valid"
    
    @staticmethod
    def _check_nesting_depth(pattern: str) -> int:
        """
        Check the maximum nesting depth of groups in the pattern
        
        Args:
            pattern: The regex pattern to check
            
        Returns:
            Maximum nesting depth
        """
        max_depth = 0
        current_depth = 0
        
        i = 0
        while i < len(pattern):
            if pattern[i] == '(':
                # Check if it's an escape
                if i > 0 and pattern[i-1] == '\\':
                    i += 1
                    continue
                    
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif pattern[i] == ')':
                # Check if it's an escape
                if i > 0 and pattern[i-1] == '\\':
                    i += 1
                    continue
                    
                current_depth = max(0, current_depth - 1)
            
            i += 1
        
        return max_depth
