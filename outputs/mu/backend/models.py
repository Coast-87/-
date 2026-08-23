"""SQLAlchemy 数据模型"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    password_hash = Column(String(200), nullable=False, comment="密码哈希")
    phone = Column(String(20), nullable=True, default="", comment="手机号")
    avatar = Column(String(500), nullable=True, default="", comment="头像URL")
    role = Column(String(20), default="user", comment="角色: user / admin")
    created_at = Column(DateTime, default=datetime.utcnow, comment="注册时间")

    products = relationship("Product", back_populates="owner")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="发布者ID")
    title = Column(String(200), nullable=False, comment="商品标题")
    category = Column(String(50), nullable=False, comment="商品分类")
    condition = Column(String(50), nullable=False, comment="成色等级")
    ai_price_min = Column(Float, nullable=True, comment="AI推荐最低价")
    ai_price_max = Column(Float, nullable=True, comment="AI推荐最高价")
    ai_tags = Column(JSON, nullable=True, comment="AI评估标签列表")
    ai_copy = Column(Text, nullable=True, comment="AI生成的营销文案")
    images = Column(JSON, nullable=True, comment="图片路径列表")
    user_note = Column(Text, nullable=True, comment="用户补充说明")
    contact = Column(String(200), nullable=True, comment="卖家联系方式")
    status = Column(String(20), default="active", comment="商品状态: active/sold/offline")
    is_flagged = Column(Integer, default=0, comment="是否被管理员标记违规: 0正常/1违规")
    created_at = Column(DateTime, default=datetime.utcnow, comment="发布时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    owner = relationship("User", back_populates="products")
