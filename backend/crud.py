import models
import schemas

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError


async def get_resume_by_id(db: AsyncSession, resume_id: int) -> Optional[models.Resume]:
    try:
        result = await db.execute(
            select(models.Resume).where(models.Resume.id == resume_id)
        )
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        print(f"Error fetching resume by ID {resume_id}: {e}")
        return None


async def get_all_resumes(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Resume]:
    try:
        result = await db.execute(
            select(models.Resume)
            .order_by(models.Resume.uploaded_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    except SQLAlchemyError as e:
        print(f"Error fetching all resumes: {e}")
        return []


async def create_resume_entry(
    db: AsyncSession,
    file_name: str,
    raw_text: str,
    extracted_data: Optional[schemas.ResumeExtractedData],
    llm_analysis_data: Optional[schemas.LLMAnalysisSchema]
) -> Optional[models.Resume]:
    try:
        db_resume = models.Resume(
            file_name=file_name,
            raw_text=raw_text,
            contact_info=extracted_data.contact_info.model_dump(exclude_none=True)
                if extracted_data and extracted_data.contact_info else None,
            summary=extracted_data.summary if extracted_data else None,
            work_experience=[
                exp.model_dump(exclude_none=True) for exp in extracted_data.work_experience
            ] if extracted_data and extracted_data.work_experience else [],
            education=[
                edu.model_dump(exclude_none=True) for edu in extracted_data.education
            ] if extracted_data and extracted_data.education else [],
            skills=extracted_data.skills.model_dump(exclude_none=True)
                if extracted_data and extracted_data.skills else None,
            projects=[
                proj.model_dump(exclude_none=True) for proj in extracted_data.projects
            ] if extracted_data and extracted_data.projects else [],
            certifications=[
                cert.model_dump(exclude_none=True) for cert in extracted_data.certifications
            ] if extracted_data and extracted_data.certifications else [],
            awards=[
                award.model_dump(exclude_none=True) for award in extracted_data.awards
            ] if extracted_data and extracted_data.awards else [],
            llm_analysis=llm_analysis_data.model_dump(exclude_none=True)
                if llm_analysis_data else None
        )

        db.add(db_resume)
        await db.commit()
        await db.refresh(db_resume)
        return db_resume

    except Exception as e:
        await db.rollback()
        import traceback
        print(f"Error creating resume entry for {file_name}: {e}")
        traceback.print_exc()
        return None
