"""FastAPI 主应用入口"""
from dotenv import load_dotenv
load_dotenv()
import os
import uuid
import shutil
import logging
from typing import Optional, List
from fastapi import FastAPI, File, Form, UploadFile, Depends, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, text

from database import get_db, engine, Base
from models import User, Product
from schemas import (
    UserRegister, UserLogin, UserResponse, TokenResponse,
    PasswordReset, PasswordChange,
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse, AIAnalysisResult,
    ModerationCheckRequest,
    AdminUserCreate, RoleUpdate,
)
from ai_service import analyze_product_images
from image_moderation import moderate_image
from auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, require_login, require_admin
)
from sensitive_filter import check_sensitive
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("flea-market")

app = FastAPI(title="校园跳蚤市场 API", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ==================== 全局异常处理 ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP {exc.status_code} on {request.method} {request.url.path}: {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "服务器内部错误，请稍后重试"})

# ==================== 启动事件 ====================
ADMIN_DEFAULT_PASSWORD = os.getenv("ADMIN_DEFAULT_PASSWORD", "admin@12345")
LEGACY_ADMIN_PASSWORD = "admin123"  # 旧版弱默认口令，启动时自动升级

@app.on_event("startup")
def startup():
    try:
        # 1. 先用 ORM 创建表（如果不存在）
        Base.metadata.create_all(bind=engine)
        # 2. 再用原生 sqlite3 补列（兼容旧数据库）
        import sqlite3
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flea_market.db")
        raw_conn = sqlite3.connect(db_path)
        for col, col_def in [
            ("phone", "VARCHAR(20) DEFAULT ''"),
            ("avatar", "VARCHAR(500) DEFAULT ''"),
        ]:
            try:
                raw_conn.execute(f"ALTER TABLE users ADD COLUMN {col} {col_def}")
                raw_conn.commit()
                logger.info(f"Added {col} column to users table")
            except sqlite3.OperationalError:
                pass  # 列已存在或表刚创建
        raw_conn.close()
        # 3. 确保 admin 账号存在，并升级旧版弱默认口令
        db = next(get_db())
        try:
            admin = db.query(User).filter(User.username == "admin").first()
            if not admin:
                admin = User(username="admin", password_hash=hash_password(ADMIN_DEFAULT_PASSWORD), role="admin", phone="")
                db.add(admin)
                db.commit()
                logger.info(f"Admin account created, default password: {ADMIN_DEFAULT_PASSWORD} (please change it promptly)")
            elif verify_password(LEGACY_ADMIN_PASSWORD, admin.password_hash):
                admin.password_hash = hash_password(ADMIN_DEFAULT_PASSWORD)
                db.commit()
                logger.warning(f"admin was using weak default 'admin123', auto-upgraded to: {ADMIN_DEFAULT_PASSWORD} (please change it promptly)")
        finally:
            db.close()
        # 4. 配置体检：AI Key 未配置时明确提示降级行为
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key or api_key.startswith("sk-your-"):
            logger.warning("OPENAI_API_KEY not configured: AI analysis falls back to mock data, image AI moderation degrades to local-only checks")
        logger.info("Database initialized, admin account ready")
    except Exception as e:
        logger.error(f"Startup failed: {e}")


# ==================== 健康检查 ====================

@app.get("/api/health")
def health():
    """健康检查（供部署脚本/探活使用）"""
    return {"ok": True, "service": "flea-market"}

# ==================== 认证 API ====================

@app.post("/api/auth/register", response_model=TokenResponse)
def register(body: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    try:
        user = User(
            username=body.username,
            password_hash=hash_password(body.password),
            phone=body.phone
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        token = create_access_token({"sub": str(user.id)})
        logger.info(f"User registered: {user.username}, phone={user.phone}")
        return TokenResponse(access_token=token, user=UserResponse.model_validate(user))
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="注册失败，请稍后重试")

@app.post("/api/auth/login", response_model=TokenResponse)
def login(body: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_access_token({"sub": str(user.id)})
    logger.info(f"User logged in: {user.username}")
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))

@app.get("/api/auth/me", response_model=UserResponse)
def me(user: User = Depends(require_login)):
    return user

# ==================== 找回密码 ====================

@app.post("/api/auth/reset-password")
def reset_password(body: PasswordReset, db: Session = Depends(get_db)):
    """通过用户名 + 手机号验证身份后重置密码"""
    user = db.query(User).filter(User.username == body.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    # 归一化手机号：去除所有非数字字符后比较
    stored_phone = re.sub(r'\D', '', user.phone or '')
    input_phone = re.sub(r'\D', '', body.phone)
    if not stored_phone or stored_phone != input_phone:
        raise HTTPException(status_code=400, detail="手机号不匹配，请核实后重试")
    try:
        user.password_hash = hash_password(body.new_password)
        db.commit()
        logger.info(f"Password reset for user: {user.username}")
        return {"ok": True, "message": "密码重置成功，请使用新密码登录"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="重置失败，请稍后重试")

# ==================== 修改密码（需登录） ====================

@app.post("/api/auth/change-password")
def change_password(
    body: PasswordChange,
    user: User = Depends(require_login),
    db: Session = Depends(get_db)
):
    """已登录状态下，通过旧密码验证后修改密码"""
    if not verify_password(body.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="旧密码不正确")
    try:
        user.password_hash = hash_password(body.new_password)
        db.commit()
        logger.info(f"Password changed for user: {user.username}")
        return {"ok": True, "message": "密码修改成功"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="修改失败，请稍后重试")

# ==================== 头像上传 ====================

@app.post("/api/auth/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(require_login),
    db: Session = Depends(get_db)
):
    """上传用户头像"""
    validate_image(file)
    try:
        filename = f"avatar_{user.id}_{uuid.uuid4().hex[:8]}{os.path.splitext(file.filename or 'img.jpg')[1].lower()}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        await moderate_uploaded_image(filepath)
        avatar_url = f"/uploads/{filename}"
        user.avatar = avatar_url
        db.commit()
        db.refresh(user)
        logger.info(f"Avatar updated: user={user.username}")
        return {"avatar": avatar_url, "message": "头像上传成功"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Avatar upload failed: {e}")
        raise HTTPException(status_code=500, detail="头像上传失败，请稍后重试")
# ==================== 文件校验工具 ====================

def validate_image(file: UploadFile):
    """校验上传文件是否为合法图片"""
    ext = os.path.splitext(file.filename or "img.jpg")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的图片格式: {ext}，仅支持 {', '.join(ALLOWED_EXTENSIONS)}")
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"图片大小不能超过 {MAX_FILE_SIZE // 1024 // 1024}MB")
    return ext

def _safe_remove(filepath: str):
    try:
        os.remove(filepath)
    except OSError:
        pass

async def moderate_uploaded_image(filepath: str):
    """对已保存的图片执行审核（魔数校验 + 违规内容审核），
    违规时删除文件并抛出 HTTPException 拦截"""
    try:
        flagged, reason = await moderate_image(filepath)
    except ValueError as e:
        _safe_remove(filepath)
        raise HTTPException(status_code=400, detail=f"图片校验失败：{e}")
    if flagged:
        _safe_remove(filepath)
        # reason 可能为空（模型偶发未给原因）：给用户可理解的兜底文案
        detail = f"图片审核未通过：{reason}" if reason else "图片审核未通过：图片包含疑似违规内容，请更换图片后重试"
        raise HTTPException(status_code=400, detail=detail)

# ==================== 文本敏感词拦截 ====================

def _check_text_blocked(text: str) -> list[str]:
    """检查文本敏感词，命中则抛出 HTTPException 拦截"""
    flagged, words = check_sensitive(text)
    if flagged:
        raise HTTPException(
            status_code=400,
            detail=f"内容包含违规敏感词，已被拦截：{'、'.join(words[:5])}，请修改后重试"
        )
    return words

# ==================== AI 分析接口 ====================

@app.post("/api/ai/analyze", response_model=AIAnalysisResult)
async def ai_analyze(
    files: List[UploadFile] = File(..., max_count=3),
    note: Optional[str] = Form(None)
):
    if len(files) < 1 or len(files) > 3:
        raise HTTPException(status_code=400, detail="请上传 1-3 张图片")

    temp_paths = []
    try:
        for f in files:
            ext = validate_image(f)
            filename = f"temp_{uuid.uuid4().hex}{ext}"
            filepath = os.path.join(UPLOAD_DIR, filename)
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(f.file, buffer)
            temp_paths.append(filepath)
            # 违规图片拦截（违规文件会被删除并抛 400）
            await moderate_uploaded_image(filepath)

        result = await analyze_product_images(temp_paths, note or "")
        return AIAnalysisResult(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI 分析失败: {str(e)}")
    finally:
        # 清理临时文件
        for p in temp_paths:
            try:
                os.remove(p)
            except OSError:
                pass

# ==================== 商品 CRUD ====================

@app.post("/api/products", response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    user: User = Depends(require_login),
    db: Session = Depends(get_db)
):
    # 敏感词拦截：覆盖标题/文案/补充说明/联系方式/标签
    full_text = " ".join(filter(None, [
        product.title, product.ai_copy, product.user_note, product.contact,
        " ".join(product.ai_tags or []),
    ]))
    _check_text_blocked(full_text)

    try:
        db_product = Product(
            user_id=user.id,
            is_flagged=0,
            **product.model_dump()
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        logger.info(f"Product created: id={db_product.id}, user={user.username}")
        return db_product
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="发布失败，请稍后重试")

@app.get("/api/products", response_model=ProductListResponse)
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    category: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Product).filter(Product.status == "active", Product.is_flagged == 0)
    if category:
        query = query.filter(Product.category == category)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(or_(Product.title.like(like), Product.ai_copy.like(like)))
    total = query.count()
    products = query.order_by(Product.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return ProductListResponse(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total, page=page, page_size=page_size
    )

@app.get("/api/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product

@app.put("/api/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    update: ProductUpdate,
    user: User = Depends(require_login),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    if product.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="无权修改此商品")
    update_data = update.model_dump(exclude_unset=True)
    # 被标记违规的商品，卖家不能私自重新上架（需管理员放行）
    if product.is_flagged == 1 and update_data.get("status") == "active" and user.role != "admin":
        raise HTTPException(status_code=403, detail="该商品已被标记违规，无法重新上架，请联系管理员")
    # 敏感词拦截：仅当文本字段被修改时检查（纯状态变更如下架/已售不受影响）
    text_fields = {"title", "ai_copy", "contact", "ai_tags"}
    if text_fields & set(update_data.keys()):
        merged_text = " ".join(filter(None, [
            update_data.get("title", product.title),
            update_data.get("ai_copy", product.ai_copy),
            update_data.get("contact", product.contact),
            " ".join(update_data.get("ai_tags", product.ai_tags) or []),
        ]))
        _check_text_blocked(merged_text)
    try:
        for key, val in update_data.items():
            setattr(product, key, val)
        db.commit()
        db.refresh(product)
        logger.info(f"Product updated: id={product_id}, user={user.username}")
        return product
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="更新失败，请稍后重试")

@app.delete("/api/products/{product_id}")
def delete_product(
    product_id: int,
    user: User = Depends(require_login),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    if product.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="无权删除此商品")
    try:
        image_urls = list(product.images or [])
        db.delete(product)
        db.commit()
        # 同步清理商品图片文件，避免残留（清理失败不影响删除结果）
        for url in image_urls:
            if isinstance(url, str) and url.startswith("/uploads/"):
                _safe_remove(os.path.join(UPLOAD_DIR, os.path.basename(url)))
        logger.info(f"Product deleted: id={product_id}, user={user.username}")
        return {"ok": True}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="删除失败，请稍后重试")

# ==================== 个人中心 ====================

@app.get("/api/my/products", response_model=ProductListResponse)
def my_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    status: Optional[str] = Query(None),
    user: User = Depends(require_login),
    db: Session = Depends(get_db)
):
    query = db.query(Product).filter(Product.user_id == user.id)
    if status:
        query = query.filter(Product.status == status)
    total = query.count()
    products = query.order_by(Product.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return ProductListResponse(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total, page=page, page_size=page_size
    )

# ==================== 管理员 API ====================

@app.get("/api/admin/flagged", response_model=ProductListResponse)
def admin_flagged(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Product).filter(Product.is_flagged == 1)
    total = query.count()
    products = query.order_by(Product.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return ProductListResponse(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total, page=page, page_size=page_size
    )

@app.get("/api/admin/all", response_model=ProductListResponse)
def admin_all_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    status: Optional[str] = Query(None),
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    if status:
        query = query.filter(Product.status == status)
    total = query.count()
    products = query.order_by(Product.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return ProductListResponse(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total, page=page, page_size=page_size
    )

@app.post("/api/admin/products/{product_id}/offline")
def admin_offline(product_id: int, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    try:
        product.status = "offline"
        db.commit()
        logger.info(f"Admin offline: product={product_id}, admin={user.username}")
        return {"ok": True, "message": "已下架"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")

@app.delete("/api/admin/products/{product_id}")
def admin_delete(product_id: int, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    try:
        db.delete(product)
        db.commit()
        logger.info(f"Admin delete: product={product_id}, admin={user.username}")
        return {"ok": True, "message": "已删除"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="删除失败，请稍后重试")

@app.post("/api/admin/products/{product_id}/flag")
def admin_flag(product_id: int, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    try:
        product.is_flagged = 1
        product.status = "offline"
        db.commit()
        logger.info(f"Admin flag: product={product_id}, admin={user.username}")
        return {"ok": True, "message": "已标记违规并下架"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")

@app.post("/api/admin/products/{product_id}/unflag")
def admin_unflag(product_id: int, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    try:
        product.is_flagged = 0
        restored = False
        if product.status == "offline":
            product.status = "active"
            restored = True
        db.commit()
        logger.info(f"Admin unflag: product={product_id}, admin={user.username}, restored={restored}")
        return {"ok": True, "message": "已取消标记并恢复上架" if restored else "已取消标记"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")

# ==================== 管理员：用户管理 ====================

@app.get("/api/admin/users")
def admin_list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    query = db.query(User)
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    items = []
    for u in users:
        items.append({
            "id": u.id,
            "username": u.username,
            "phone": u.phone or "",
            "role": u.role,
            "created_at": u.created_at,
            "product_count": db.query(Product).filter(Product.user_id == u.id).count(),
        })
    return {"items": items, "total": total, "page": page, "page_size": page_size}

@app.post("/api/admin/users")
def admin_create_user(body: AdminUserCreate, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    try:
        new_user = User(
            username=body.username,
            password_hash=hash_password(body.password),
            phone=body.phone or "",
            role=body.role,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"Admin created account: {new_user.username} role={new_user.role} by {user.username}")
        return {"ok": True, "user_id": new_user.id, "username": new_user.username, "role": new_user.role}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="创建失败，请稍后重试")

@app.put("/api/admin/users/{user_id}/role")
def admin_set_role(user_id: int, body: RoleUpdate, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")
    if target.id == user.id and body.role != "admin":
        raise HTTPException(status_code=400, detail="不能降级自己")
    if target.role == "admin" and body.role == "user":
        admin_count = db.query(User).filter(User.role == "admin").count()
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="不能降级最后一名管理员")
    try:
        old_role = target.role
        target.role = body.role
        db.commit()
        logger.info(f"Admin set role: {target.username} {old_role}->{body.role} by {user.username}")
        return {"ok": True, "message": "已设为管理员" if body.role == "admin" else "已设为普通用户"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="操作失败，请稍后重试")

@app.delete("/api/admin/users/{user_id}")
def admin_delete_user(user_id: int, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")
    if target.id == user.id:
        raise HTTPException(status_code=400, detail="不能删除自己的账号")
    if target.role == "admin":
        admin_count = db.query(User).filter(User.role == "admin").count()
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="不能删除最后一名管理员")
    try:
        products = db.query(Product).filter(Product.user_id == target.id).all()
        image_urls = []
        for p in products:
            image_urls.extend([u for u in (p.images or []) if isinstance(u, str)])
            db.delete(p)
        db.delete(target)
        db.commit()
        for url in image_urls:
            if url.startswith("/uploads/"):
                _safe_remove(os.path.join(UPLOAD_DIR, os.path.basename(url)))
        logger.info(f"Admin deleted account: {target.username} (with {len(products)} products) by {user.username}")
        return {"ok": True, "message": f"账号已删除（含其名下 {len(products)} 件商品）"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="删除失败，请稍后重试")

# ==================== 图片上传 ====================

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    ext = validate_image(file)
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    try:
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        _safe_remove(filepath)
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail="文件上传失败，请稍后重试")
    # 违规图片拦截（违规文件会被删除并抛 400）
    await moderate_uploaded_image(filepath)
    logger.info(f"Image uploaded: {filename}")
    return {"url": f"/uploads/{filename}"}

# ==================== 文本违规预检 ====================

@app.post("/api/moderation/check")
def moderation_check(
    body: ModerationCheckRequest,
    user: User = Depends(require_login)
):
    """发布前文本敏感词预检，供前端即时反馈"""
    flagged, words = check_sensitive(body.text)
    return {"flagged": flagged, "words": words}

# ==================== 前端静态托管（可选） ====================
# 若 frontend/dist 存在（已执行过 pnpm build），后端直接托管前端页面，
# 浏览器访问 http://localhost:8000 即可，无需单独启动前端开发服务器
DIST_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dist"))
if os.path.isdir(DIST_DIR):
    _assets_dir = os.path.join(DIST_DIR, "assets")
    if os.path.isdir(_assets_dir):
        app.mount("/assets", StaticFiles(directory=_assets_dir), name="assets")

    # 缓存策略：index.html 禁止缓存（每次校验最新版），
    # 带内容哈希的静态资源可长期缓存。避免浏览器拿到旧版前端导致“修复不生效”。
    _NO_CACHE = {"Cache-Control": "no-cache, must-revalidate"}
    _IMMUTABLE = {"Cache-Control": "public, max-age=31536000, immutable"}

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        """SPA 路由兜底：静态文件存在则返回文件，否则返回 index.html"""
        if not full_path:
            return FileResponse(os.path.join(DIST_DIR, "index.html"), headers=_NO_CACHE)
        # 未注册的 /api 路径返回 404，避免把 SPA 页面当成接口响应（200 HTML）
        if full_path == "api" or full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="接口不存在")
        # 规范化后必须仍位于前端构建目录内，防止 ../ 路径穿越读取任意文件
        candidate = os.path.normpath(os.path.join(DIST_DIR, full_path))
        if not candidate.startswith(DIST_DIR + os.sep):
            raise HTTPException(status_code=404, detail="资源不存在")
        if os.path.isfile(candidate):
            headers = _IMMUTABLE if full_path.replace("\\", "/").startswith("assets/") else None
            return FileResponse(candidate, headers=headers)
        return FileResponse(os.path.join(DIST_DIR, "index.html"), headers=_NO_CACHE)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)









