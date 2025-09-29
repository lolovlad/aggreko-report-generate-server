from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    ForeignKey,
    Boolean,
    Float,
    Date
)

from sqlalchemy.dialects.postgresql import JSONB, UUID
from uuid import uuid4
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional

base = declarative_base()


class DeleteMixin(object):
    is_delite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True, server_default="False")


class SystemVariablesMixin(object):
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    system_name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(128), nullable=True)


class TypeUser(base, SystemVariablesMixin):
    __tablename__ = "type_user"


class Profession(base, SystemVariablesMixin):
    __tablename__ = "profession"


class User(base, DeleteMixin):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), unique=True, default=uuid4)

    name: Mapped[str] = mapped_column(nullable=True)
    surname: Mapped[str] = mapped_column(nullable=True)
    patronymic: Mapped[str] = mapped_column(nullable=True)

    email: Mapped[str] = mapped_column(nullable=True, unique=True)
    password_hash: Mapped[str] = mapped_column(nullable=True)
    id_type: Mapped[int] = mapped_column(ForeignKey("type_user.id"))
    id_profession: Mapped[int] = mapped_column(ForeignKey("profession.id"))
    type: Mapped[TypeUser] = relationship(lazy="joined")
    profession: Mapped[Profession] = relationship(lazy="joined")

    painting: Mapped[str] = mapped_column(nullable=True, default="")

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, val: str):
        self.password_hash = generate_password_hash(val)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class TypeBlueprint(base, SystemVariablesMixin, DeleteMixin):
    __tablename__ = "type_blueprint"


class TypeEquipmentBlueprint(base, SystemVariablesMixin, DeleteMixin):
    __tablename__ = "type_equipment_blueprint"


class Blueprint(base, DeleteMixin):
    __tablename__ = "blueprint"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), unique=True, default=uuid4)

    name: Mapped[str] = mapped_column(nullable=False, default="template")
    id_plant: Mapped[int] = mapped_column(ForeignKey("type_equipment_blueprint.id"), nullable=False, default=1)
    id_type: Mapped[int] = mapped_column(ForeignKey("type_blueprint.id"), nullable=False, default=1)

    path_template_docx_file: Mapped[str] = mapped_column(nullable=False)
    path_map_data_json_file: Mapped[str] = mapped_column(nullable=False)
    path_form_xlsx_file: Mapped[str] = mapped_column(nullable=False)

    type: Mapped[TypeBlueprint] = relationship(lazy="joined")
    plant: Mapped[TypeEquipmentBlueprint] = relationship(lazy="joined")

    last_datetime_edit: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                         nullable=False,
                                                         onupdate=func.now(),
                                                         server_default=func.now())


class TypeEquipment(base, SystemVariablesMixin, DeleteMixin):
    __tablename__ = "type_equipment"
    code: Mapped[str] = mapped_column(unique=True, nullable=False)


class Equipment(base, DeleteMixin):
    __tablename__ = "equipment"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    uuid: Mapped[str] = mapped_column(UUID(as_uuid=True), unique=True, default=uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    code: Mapped[str] = mapped_column(nullable=True)
    id_type: Mapped[int] = mapped_column(ForeignKey("type_equipment.id"))
    type: Mapped[TypeEquipment] = relationship(lazy="joined")
    description: Mapped[str] = mapped_column(Text, nullable=True)
    characteristics: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)


class StateClaim(base, SystemVariablesMixin):
    __tablename__ = "state_claim"


class Claim(base, DeleteMixin):
    __tablename__ = "claim"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    uuid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), unique=True, default=uuid4)

    name: Mapped[str] = mapped_column(nullable=True, default="template", server_default="template")
    datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    id_state_claim: Mapped[int] = mapped_column(ForeignKey("state_claim.id"))
    state_claim: Mapped[StateClaim] = relationship(lazy="joined")

    id_user: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User] = relationship(lazy="joined")

    id_blueprint: Mapped[int] = mapped_column(ForeignKey("blueprint.id"))
    blueprint: Mapped[Blueprint] = relationship(lazy="joined")

    id_equipment: Mapped[int] = mapped_column(ForeignKey("equipment.id"), nullable=True)
    equipment: Mapped[Equipment] = relationship(lazy="joined")

    main_document: Mapped[str] = mapped_column(nullable=True)

    edit_document: Mapped[str] = mapped_column(nullable=True)
    comment: Mapped[str] = mapped_column(Text, nullable=True, default="Нет")

    blueprint_xlsx_file: Mapped[str] = mapped_column(nullable=True)
    blueprint_json_file: Mapped[Optional[dict]] = mapped_column(MutableDict.as_mutable(JSONB), nullable=True)

    last_datetime_edit: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                         nullable=False,
                                                         onupdate=func.now(),
                                                         server_default=func.now())


class TypeDevice(base, SystemVariablesMixin):
    __tablename__ = "type_device"


class Device(base):
    __tablename__ = "device"
    id:  Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    id_type:  Mapped[int] = mapped_column(ForeignKey("type_device.id"))
    type: Mapped[TypeDevice] = relationship(lazy="joined")
    error: Mapped[str] = mapped_column(nullable=False)
    code: Mapped[str] = mapped_column(nullable=False, unique=True)
    date_check_last: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    date_check_next: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)



