from sqlalchemy import Column, ForeignKey, Integer, String, Table, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from database.base import Base
from sqlalchemy.orm import relationship
from database import uuid_pk, str_64, str_128



# role_permissions = Table(
#     'role_permissions', Base.metadata,
#     Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
#     Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
# )

# class Roles(Base):
#     __tablename__ = 'roles'
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     role_name: Mapped[str] = mapped_column(String, nullable=False)

#     permissions: Mapped[list['Permissions']] = relationship(
#         "Permissions", secondary=role_permissions, back_populates="roles"
#     )

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid_pk]
    name: Mapped[str_64]
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    password: Mapped[str_128]
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    
    # role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'), nullable=False)
    # role: Mapped['Roles'] = relationship("Roles", back_populates="users")

# class Permissions(Base):
#     __tablename__ = 'permissions'
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     permission_name: Mapped[str] = mapped_column(String, nullable=False)

#     roles: Mapped[list['Roles']] = relationship(
#         "Roles", secondary=role_permissions, back_populates="permissions"
#     )

#     def add_permission(self, permission):
#         if permission not in self.permissions:
#             self.permissions.append(permission)

#     def remove_permission(self, permission):
#         if permission in self.permissions:
#             self.permissions.remove(permission)
