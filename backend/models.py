from db import Base

from sqlalchemy import Column, Integer, String, JSON, Text, func, DateTime


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)

    file_name = Column(String, index=True)
    raw_text = Column(Text, nullable=True)

    skills = Column(JSON, nullable=True)
    awards = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    projects = Column(JSON, nullable=True)
    education = Column(JSON, nullable=True)
    contact_info = Column(JSON, nullable=True)
    certifications = Column(JSON, nullable=True)
    work_experience = Column(JSON, nullable=True)

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())  # auto-timestamp

    llm_analysis = Column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<Resume(id={self.id}, filename={self.file_name})>"