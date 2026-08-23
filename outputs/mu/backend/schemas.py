"""Pydantic 请求/响应模型"""
import re
from pydantic import AliasChoices, BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

# ==================== 认证 ====================

class UserRegister(BaseModel):
    username: str = Field(..., min_length=2, max_length=20)
    password: str = Field(..., min_length=8, max_length=100)
    phone: str = Field(..., min_length=11, max_length=11)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9]+$', v):
            raise ValueError("用户名只能包含中文、英文、数字")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("密码至少需要8位")
        # 至少包含两种字符类型
        has_letter = bool(re.search(r'[a-zA-Z]', v))
        has_digit = bool(re.search(r'\d', v))
        has_special = bool(re.search(r'[!@#$%^&*(),.?\"":{}|<>_\-+=\[\]\\;\/]', v))
        if not (has_letter and has_digit) and not (has_letter and has_special) and not (has_digit and has_special):
            raise ValueError("密码需包含字母+数字、或字母+符号、或数字+符号的组合")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError("请输入正确的11位中国大陆手机号")
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class PasswordReset(BaseModel):
    """找回密码：用户名 + 手机号验证 → 设置新密码"""
    username: str = Field(..., min_length=2, max_length=20)
    phone: str = Field(..., min_length=11, max_length=11)
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("密码至少需要8位")
        has_letter = bool(re.search(r'[a-zA-Z]', v))
        has_digit = bool(re.search(r'\d', v))
        has_special = bool(re.search(r'[!@#$%^&*(),.?\"":{}|<>_\-+=\[\]\\;\/]', v))
        if not (has_letter and has_digit) and not (has_letter and has_special) and not (has_digit and has_special):
            raise ValueError("密码需包含字母+数字、或字母+符号、或数字+符号的组合")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError("请输入正确的11位中国大陆手机号")
        return v

class PasswordChange(BaseModel):
    """修改密码：旧密码验证 → 设置新密码"""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("密码至少需要8位")
        has_letter = bool(re.search(r'[a-zA-Z]', v))
        has_digit = bool(re.search(r'\d', v))
        has_special = bool(re.search(r'[!@#$%^&*(),.?\"":{}|<>_\-+=\[\]\\;\/]', v))
        if not (has_letter and has_digit) and not (has_letter and has_special) and not (has_digit and has_special):
            raise ValueError("密码需包含字母+数字、或字母+符号、或数字+符号的组合")
        return v

class UserResponse(BaseModel):
    id: int
    username: str
    phone: Optional[str] = None
    avatar: Optional[str] = None
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ==================== 商品 ====================

class ProductCreate(BaseModel):
    title: str = Field(..., max_length=200)
    category: str = Field(..., max_length=50)
    condition: str = Field(..., max_length=50)
    ai_price_min: Optional[float] = None
    ai_price_max: Optional[float] = None
    ai_tags: Optional[List[str]] = None
    ai_copy: Optional[str] = None
    images: Optional[List[str]] = None
    user_note: Optional[str] = None
    contact: Optional[str] = None

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    condition: Optional[str] = None
    ai_price_min: Optional[float] = None
    ai_price_max: Optional[float] = None
    ai_tags: Optional[List[str]] = None
    ai_copy: Optional[str] = None
    contact: Optional[str] = None
    status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            raise ValueError("商品状态不能为空")
        if v not in ("active", "sold", "offline"):
            raise ValueError("商品状态只能是 active(在售)/sold(已售)/offline(已下架)")
        return v

class ProductResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    title: str
    category: str
    condition: str
    ai_price_min: Optional[float] = None
    ai_price_max: Optional[float] = None
    ai_tags: Optional[List[str]] = None
    ai_copy: Optional[str] = None
    images: Optional[List[str]] = None
    user_note: Optional[str] = None
    contact: Optional[str] = None
    status: str
    is_flagged: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AIAnalysisResult(BaseModel):
    title: str
    category: str
    condition: str
    price_min: float
    price_max: float
    tags: List[str]
    copy_text: str = Field(..., validation_alias=AliasChoices("copy_text", "copy"), serialization_alias="copy")

class ModerationCheckRequest(BaseModel):
    """文本违规预检请求"""
    text: str = Field(..., min_length=1, max_length=2000)

class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int



class AdminUserCreate(BaseModel):
    """管理员创建账号（可指定角色，用户名/密码规则与普通注册一致）"""
    username: str = Field(..., min_length=2, max_length=20)
    password: str = Field(..., min_length=8, max_length=100)
    phone: Optional[str] = ""
    role: str = Field("admin", pattern="^(admin|user)$")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9]+$', v):
            raise ValueError("用户名只能包含中文、英文、数字")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        has_letter = bool(re.search(r'[a-zA-Z]', v))
        has_digit = bool(re.search(r'\d', v))
        has_special = bool(re.search(r'[!@#$%^&*(),.?\"":{}|<>_\-+=\[\]\\;\/]', v))
        if not (has_letter and has_digit) and not (has_letter and has_special) and not (has_digit and has_special):
            raise ValueError("密码需包含字母+数字、或字母+符号、或数字+符号的组合")
        return v


class RoleUpdate(BaseModel):
    role: str = Field(..., pattern="^(admin|user)$")
