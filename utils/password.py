import re
from typing import Optional

class InvalidPasswordFormatError(Exception):
    """비밀번호 형식이 유효하지 않을 때 발생하는 예외"""
    pass

def is_valid_password(password: str) -> bool:
    """
    비밀번호 유효성 검사 함수
    
    조건:
    - 최소 8자, 최대 32자
    - 최소 1개의 대문자 포함
    - 최소 1개의 소문자 포함
    - 최소 1개의 숫자 포함
    - 최소 1개의 특수문자 포함
    
    Args:
        password: 검사할 비밀번호
        
    Returns:
        bool: 비밀번호가 유효하면 True, 아니면 False
    """
    if not password or len(password) < 8 or len(password) > 32:
        return False
        
    # 대문자 검사
    if not re.search(r"[A-Z]", password):
        return False
        
    # 소문자 검사
    if not re.search(r"[a-z]", password):
        return False
        
    # 숫자 검사
    if not re.search(r"[0-9]", password):
        return False
        
    # 특수문자 검사
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
        
    return True
