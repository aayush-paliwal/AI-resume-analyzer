import crud
import schemas
import llm_service
import resume_parser

from db import get_db
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status


router = APIRouter(
    prefix="/resumes",
    tags=["users"]
)


@router.post("/upload", response_model=schemas.ResumeReadSchema, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename:
       raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file uploaded")

    contents = await file.read()

    try:
        raw_text = resume_parser.extract_text_from_resume(file.filename, contents)

        if not raw_text or len(raw_text.strip()) < 30:
            print(f"Could not extract sufficient text from resume: {file.filename}.")
            crud.create_resume_entry(db, file_name=file.filename, raw_text=raw_text or "Extraction failed or empty", extracted_data=None, llm_analysis_data=None)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not extract sufficient text.")
    except ValueError as e:
        print(f"Unsupported file type or encoding for {file.filename}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print(f"Unexpected error during text extraction for {file.filename}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing resume file during text extraction.")

    extracted_data: Optional[schemas.ResumeExtractedData] = await llm_service.extract_structured_data_from_text(raw_text)
    
    if not extracted_data:
        print(f"LLM failed to extract structured data for {file.filename}.")
        crud.create_resume_entry(db, file_name=file.filename, raw_text=raw_text, extracted_data=None, llm_analysis_data=None)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="LLM failed to extract structured data. Raw text has been saved.")


    llm_analysis = await llm_service.analyze_resume_with_llm(extracted_data)
    if not llm_analysis:
        print(f"LLM analysis failed for {file.filename}")



    db_resume = crud.create_resume_entry(
        db=db, 
        file_name=file.filename,
        raw_text=raw_text,
        extracted_data=extracted_data,
        llm_analysis_data=llm_analysis
    )

    if not db_resume:
        print(f"Failed to save processed resume data to database for {file.filename}.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save processed resume data to database.")
            
    print(f"Resume {file.filename} processed and saved successfully.")
    return schemas.ResumeReadSchema.model_validate(db_resume)



@router.get("/", response_model=List[schemas.ResumeListDetailSchema])
def list_resumes(
    skip: int = 0, limit: int = 20, 
    db:Session = Depends(get_db)
):
    resumes_db = crud.get_all_resumes(db, skip=skip, limit=limit)
    if resumes_db is None: 
        return []
        
    results = []
    for r_db in resumes_db:
        name = r_db.contact_info.get("name") if isinstance(r_db.contact_info, dict) else None
        email = r_db.contact_info.get("email") if isinstance(r_db.contact_info, dict) else None
        results.append(schemas.ResumeListDetailSchema(
            id=r_db.id,
            file_name=r_db.file_name,
            uploaded_at=r_db.uploaded_at,
            name=name,
            email=email,
        ))

    return results


@router.get("/{resume_id}", response_model=schemas.ResumeReadSchema)
def get_resume(
    resume_id: int, 
    db:Session = Depends(get_db)
):
    db_resume = crud.get_resume_by_id(db, resume_id=resume_id)
    
    if db_resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    
    # Use model_validate for SQLAlchemy ORM instance to Pydantic model conversion
    return schemas.ResumeReadSchema.model_validate(db_resume)
