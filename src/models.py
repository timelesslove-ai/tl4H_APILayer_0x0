"""
Shared database models used across multiple modules.
Defines BaseModel, TimeStampedModel, and common relationship tables.
"""

"""
Global database models used across multiple modules in the Memory Keeper application.
Defines base models, database tables, and relationships between entities.
"""

from datetime import date, datetime
from enum import Enum, auto
from typing import (Any, Dict, Generic, List, Literal, Optional, Set, TypeVar,
                    Union)
from uuid import UUID, uuid4

from pydantic import BaseModel as PydanticBaseModel
from pydantic import EmailStr, Field, root_validator, validator
from pydantic.generics import GenericModel
from sqlalchemy import JSON, Boolean, Column, DateTime
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy import Float, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as SQLUUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import (DeclarativeBase, Mapped, backref, mapped_column,
                            relationship)
from sqlalchemy.sql import expression


# Base SQLAlchemy class
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    pass


# Common SQLAlchemy model mixins
class TimestampMixin:
    """Adds created_at and updated_at timestamps to models"""
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class UUIDMixin:
    """Adds UUID primary key to models"""
    id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )


# Association tables for many-to-many relationships
memory_tag_association = Table(
    "memory_tag",
    Base.metadata,
    Column("memory_id", SQLUUID(as_uuid=True), ForeignKey("memories.id"), primary_key=True),
    Column("tag_id", SQLUUID(as_uuid=True), ForeignKey("tags.id"), primary_key=True)
)

memory_child_association = Table(
    "memory_child",
    Base.metadata,
    Column("memory_id", SQLUUID(as_uuid=True), ForeignKey("memories.id"), primary_key=True),
    Column("child_id", SQLUUID(as_uuid=True), ForeignKey("children.id"), primary_key=True)
)

user_family_association = Table(
    "user_family",
    Base.metadata,
    Column("user_id", SQLUUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("family_id", SQLUUID(as_uuid=True), ForeignKey("families.id"), primary_key=True),
    Column("role", SQLAEnum("owner", "co_parent", "family_member", "guest"), nullable=False)
)


# Enum definitions
class VisibilityRuleType(str, Enum):
    """Types of visibility rules for age gating memories"""
    ABSOLUTE_AGE = "absolute_age"
    MILESTONE = "milestone"
    PARENT_TRIGGERED = "parent_triggered"
    COMBO = "combo"


class MediaType(str, Enum):
    """Supported media types for memory content"""
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    DOCUMENT = "document"


class MilestoneCategory(str, Enum):
    """Categories for developmental milestones"""
    PHYSICAL = "physical"
    COGNITIVE = "cognitive"
    SOCIAL = "social"
    EMOTIONAL = "emotional"
    LANGUAGE = "language"
    EDUCATIONAL = "educational"
    CUSTOM = "custom"


class UserRole(str, Enum):
    """User roles within a family"""
    OWNER = "owner"
    CO_PARENT = "co_parent"
    FAMILY_MEMBER = "family_member"
    GUEST = "guest"


# SQLAlchemy Models
class User(Base, UUIDMixin, TimestampMixin):
    """User model representing a registered account"""
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    preferences: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    owned_families: Mapped[List["Family"]] = relationship(
        "Family", back_populates="owner", foreign_keys="Family.owner_id"
    )
    families: Mapped[List["Family"]] = relationship(
        "Family", secondary=user_family_association, back_populates="members"
    )
    created_memories: Mapped[List["Memory"]] = relationship(
        "Memory", back_populates="creator", foreign_keys="Memory.creator_id"
    )
    authored_comments: Mapped[List["Comment"]] = relationship(
        "Comment", back_populates="author"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="user"
    )


class Family(Base, UUIDMixin, TimestampMixin):
    """Family model representing a group of related users and children"""
    __tablename__ = "families"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    owner_id: Mapped[UUID] = mapped_column(SQLUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    owner: Mapped[User] = relationship(
        "User", back_populates="owned_families", foreign_keys=[owner_id]
    )
    members: Mapped[List[User]] = relationship(
        "User", secondary=user_family_association, back_populates="families"
    )
    children: Mapped[List["Child"]] = relationship(
        "Child", back_populates="family"
    )


class Child(Base, UUIDMixin, TimestampMixin):
    """Child model for whom memories are being stored"""
    __tablename__ = "children"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_date: Mapped[date] = mapped_column(DateTime, nullable=False)
    gender: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    family_id: Mapped[UUID] = mapped_column(SQLUUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    
    # Relationships
    family: Mapped[Family] = relationship("Family", back_populates="children")
    memories: Mapped[List["Memory"]] = relationship(
        "Memory", secondary=memory_child_association, back_populates="children"
    )
    milestones: Mapped[List["Milestone"]] = relationship(
        "Milestone", back_populates="child"
    )


class VisibilityRule(Base, UUIDMixin, TimestampMixin):
    """Rules that determine when content becomes visible based on child's age"""
    __tablename__ = "visibility_rules"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    rule_type: Mapped[VisibilityRuleType] = mapped_column(
        SQLAEnum(VisibilityRuleType), nullable=False
    )
    # For absolute age: {"years": 5, "months": 6, "days": 0}
    # For milestone: {"milestone_type": "first_day_school"}
    # For combo: {"operator": "AND", "rules": [rule_id1, rule_id2]}
    rule_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    memories: Mapped[List["Memory"]] = relationship(
        "Memory", back_populates="visibility_rule"
    )


class Memory(Base, UUIDMixin, TimestampMixin):
    """Core memory model containing metadata and relationships"""
    __tablename__ = "memories"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    date_occurred: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    creator_id: Mapped[UUID] = mapped_column(SQLUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    visibility_rule_id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True), ForeignKey("visibility_rules.id"), nullable=False
    )
    is_milestone: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    milestone_category: Mapped[Optional[MilestoneCategory]] = mapped_column(
        SQLAEnum(MilestoneCategory), nullable=True
    )
    location: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    custom_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    creator: Mapped[User] = relationship(
        "User", back_populates="created_memories", foreign_keys=[creator_id]
    )
    visibility_rule: Mapped[VisibilityRule] = relationship(
        "VisibilityRule", back_populates="memories"
    )
    children: Mapped[List[Child]] = relationship(
        "Child", secondary=memory_child_association, back_populates="memories"
    )
    media_items: Mapped[List["MediaItem"]] = relationship(
        "MediaItem", back_populates="memory"
    )
    comments: Mapped[List["Comment"]] = relationship(
        "Comment", back_populates="memory"
    )
    tags: Mapped[List["Tag"]] = relationship(
        "Tag", secondary=memory_tag_association, back_populates="memories"
    )
    related_memories: Mapped[List["MemoryConnection"]] = relationship(
        "MemoryConnection", 
        foreign_keys="[MemoryConnection.source_memory_id]",
        back_populates="source_memory"
    )


class MediaItem(Base, UUIDMixin, TimestampMixin):
    """Media content associated with a memory"""
    __tablename__ = "media_items"

    memory_id: Mapped[UUID] = mapped_column(SQLUUID(as_uuid=True), ForeignKey("memories.id"), nullable=False)
    media_type: Mapped[MediaType] = mapped_column(SQLAEnum(MediaType), nullable=False)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # For audio/video
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # For images/video
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # For images/video
    transcription: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # For audio/video
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    memory: Mapped[Memory] = relationship("Memory", back_populates="media_items")
    thumbnails: Mapped[List["MediaThumbnail"]] = relationship(
        "MediaThumbnail", back_populates="media_item"
    )


class MediaThumbnail(Base, UUIDMixin, TimestampMixin):
    """Thumbnails and previews for media items"""
    __tablename__ = "media_thumbnails"

    media_item_id: Mapped[UUID] = mapped_column(SQLUUID(as_uuid=True), ForeignKey("media_items.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    thumbnail_type: Mapped[str] = mapped_column(String(50), nullable=False)  # small, medium, large
    
    # Relationships
    media_item: Mapped[MediaItem] = relationship("MediaItem", back_populates="thumbnails")


class Tag(Base, UUIDMixin, TimestampMixin):
    """Tags for categorizing memories"""
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    
    # Relationships
    memories: Mapped[List[Memory]] = relationship(
        "Memory", secondary=memory_tag_association, back_populates="tags"
    )


class Comment(Base, UUIDMixin, TimestampMixin):
    """User comments on memories"""
    __tablename__ = "comments"

    memory_id: Mapped[UUID] = mapped_column(SQLUUID(as_uuid=True), ForeignKey("memories.id"), nullable=False)
    author_id: Mapped[UUID] = mapped_column(SQLUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    parent_id: Mapped[Optional[UUID]] = mapped_column(SQLUUID(as_uuid=True), ForeignKey("comments.id"), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Relationships
    memory: Mapped[Memory] = relationship("Memory", back_populates="comments")
    author: Mapped[User] = relationship("User", back_populates="authored_comments")
    parent: Mapped[Optional["Comment"]] = relationship(
        "Comment", back_populates="replies", remote_side=[id]
    )
    replies: Mapped[List["Comment"]] = relationship(
        "Comment", back_populates="parent"
    )


class Milestone(Base, UUIDMixin, TimestampMixin):
    """Developmental milestones for children"""
    __tablename__ = "milestones"

    child_id: Mapped[UUID] = mapped_column(SQLUUID(as_uuid=True), ForeignKey("children.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    date_achieved: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    category: Mapped[MilestoneCategory] = mapped_column(SQLAEnum(MilestoneCategory), nullable=False)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    custom_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    related_memory_id: Mapped[Optional[UUID]] = mapped_column(SQLUUID(as_uuid=True), ForeignKey("memories.id"), nullable=True)
    
    # Relationships
    child: Mapped[Child] = relationship("Child", back_populates="milestones")
    related_memory: Mapped[Optional[Memory]] = relationship(
        "Memory", foreign_keys=[related_memory_id]
    )


class MemoryConnection(Base, UUIDMixin, TimestampMixin):
    """Connections between related memories"""
    __tablename__ = "memory_connections"

    source_memory_id: Mapped[UUID] = mapped_column(SQLUUID(as_uuid=True), ForeignKey("memories.id"), nullable=False)
    target_memory_id: Mapped[UUID] = mapped_column(SQLUUID(as_uuid=True), ForeignKey("memories.id"), nullable=False)
    connection_type: Mapped[str] = mapped_column(String(100), nullable=False)
    connection_strength: Mapped[float] = mapped_column(Float, nullable=False)
    is_auto_detected: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    source_memory: Mapped[Memory] = relationship(
        "Memory", foreign_keys=[source_memory_id], back_populates="related_memories"
    )
    target_memory: Mapped[Memory] = relationship(
        "Memory", foreign_keys=[target_memory_id]
    )


class Notification(Base, UUIDMixin, TimestampMixin):
    """User notifications for various system events"""
    __tablename__ = "notifications"

    user_id: Mapped[UUID] = mapped_column(SQLUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    notification_type: Mapped[str] = mapped_column(String(100), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    link: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    related_object_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    related_object_id: Mapped[Optional[UUID]] = mapped_column(SQLUUID(as_uuid=True), nullable=True)
    
    # Relationships
    user: Mapped[User] = relationship("User", back_populates="notifications")


# Pydantic models for API input/output
T = TypeVar('T')

class BaseSchema(PydanticBaseModel):
    """Base Pydantic schema with common configurations"""
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class PaginatedResponse(GenericModel, Generic[T]):
    """Generic pagination wrapper for list responses"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool


class ApiResponse(GenericModel, Generic[T]):
    """Standard API response envelope"""
    success: bool = True
    data: Optional[T] = None
    error: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None


# API schemas would be defined in their respective module schemas.py files
# but here are a few examples for illustration:

class UserCreate(BaseSchema):
    """Schema for user creation"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str
    last_name: str
    
    @validator('password')
    def password_strength(cls, v):
        # Simple validation - would be more complex in real implementation
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v


class UserRead(BaseSchema):
    """Schema for user data response"""
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class MemoryCreate(BaseSchema):
    """Schema for memory creation"""
    title: str
    description: Optional[str] = None
    date_occurred: datetime
    child_ids: List[UUID]
    visibility_rule_id: UUID
    is_milestone: bool = False
    milestone_category: Optional[MilestoneCategory] = None
    location: Optional[Dict[str, Any]] = None
    custom_metadata: Optional[Dict[str, Any]] = None
    tags: List[str] = []


class VisibilityRuleCreate(BaseSchema):
    """Schema for visibility rule creation"""
    name: str
    rule_type: VisibilityRuleType
    rule_data: Dict[str, Any]
    description: Optional[str] = None
    
    @root_validator
    def validate_rule_data(cls, values):
        rule_type = values.get('rule_type')
        rule_data = values.get('rule_data')
        
        if rule_type == VisibilityRuleType.ABSOLUTE_AGE:
            required_fields = ['years', 'months', 'days']
            if not all(field in rule_data for field in required_fields):
                raise ValueError(f"Absolute age rule must contain {', '.join(required_fields)}")
        
        elif rule_type == VisibilityRuleType.MILESTONE:
            if 'milestone_type' not in rule_data:
                raise ValueError("Milestone rule must contain 'milestone_type'")
        
        elif rule_type == VisibilityRuleType.COMBO:
            if 'operator' not in rule_data or 'rules' not in rule_data:
                raise ValueError("Combo rule must contain 'operator' and 'rules'")
            
            valid_operators = ['AND', 'OR']
            if rule_data['operator'] not in valid_operators:
                raise ValueError(f"Operator must be one of {', '.join(valid_operators)}")
            
            if not isinstance(rule_data['rules'], list) or len(rule_data['rules']) < 2:
                raise ValueError("Rules must be a list with at least 2 items")
        
        return values