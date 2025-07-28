import os
import re
import json
import schemas

from typing import Optional
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI




load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


if not GEMINI_API_KEY:
    raise ValueError("API key not present")


try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.1
    )
    print("LLM initialized successfully")
except Exception as e:
    print(f"Failed to initialize LLM: {e}")


def parse_llm_json_output(ll_output_str: str, target_schema: type[schemas.BaseModel]) -> Optional[schemas.BaseModel]:
    if not ll_output_str:
        print("LLM output string is empty.")
        return None

    cleaned_json_str = ll_output_str.strip()
    match = re.search(r"```json\s*([\s\S]+?)\s*```", cleaned_json_str, re.DOTALL)

    if match:
        json_data_str = match.group(1).strip()
        print("Extracted JSON from markdown block.")
    else:
        first_brace = cleaned_json_str.find('{')
        last_brace = cleaned_json_str.rfind('}')

        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            json_data_str = cleaned_json_str[first_brace : last_brace+1]
            print("Extracted JSON using first/last brace method.")
        else:
            json_data_str = cleaned_json_str
            print("No markdown or clear braces found, attempting direct parse.")
    
    try:
        parsed_dict = json.loads(json_data_str)
        validated_data = target_schema.model_validate(parsed_dict) 
        
        print(f"Successfully parsed and validated JSON against {target_schema.__name__}.")
        return validated_data
    except Exception as e:
        print("Error: ", e)
    
    return None


try:
    raw_extraction_schema_json_str = json.dumps(schemas.ResumeExtractedData.model_json_schema(), indent=2)
    raw_analysis_schema_json_str = json.dumps(schemas.LLMAnalysisSchema.model_json_schema(), indent=2)

    LITERAL_EXTRACTION_SCHEMA_JSON_STR = raw_extraction_schema_json_str.replace("{", "{{").replace("}", "}}")
    LITERAL_ANALYSIS_SCHEMA_JSON_STR = raw_analysis_schema_json_str.replace("{", "{{").replace("}", "}}")
except Exception as e:
    print("Error: ", e)
    LITERAL_EXTRACTION_SCHEMA_JSON_STR = "{{ 'error': 'Schema for extraction not available' }}"
    LITERAL_ANALYSIS_SCHEMA_JSON_STR = "{{ 'error': 'Schema for analysis not available' }}"


SYSTEM_EXTRACTION_CONTENT = f"""You are an highly intelligent and meticulous resume parsing assistant.
Your primary function is to extract structured information from the provided resume text.
You MUST output the information STRICTLY in JSON format, precisely adhering to the JSON schema provided below.
- Do NOT include any conversational introductions, apologies, summaries, or any text outside the single JSON object.
- If a specific piece of information or a section (e.g., 'awards') is not found in the resume, either omit that key from the JSON or set its value to `null` if the schema allows for it (usually omitting is better for optional fields/lists).
- Only extract information explicitly present in the resume text. Do not infer or add information not found.
- For dates (e.g., start_date, end_date, graduation_date), strive for consistency. "YYYY-MM-DD" is preferred if day is available, otherwise "YYYY-MM" or "YYYY". If only a year range is given (e.g., "2018-2020"), try to interpret it. "Present" for an end date is acceptable.
- For 'duration_months' in work_experience, calculate it if 'start_date' and 'end_date' (or 'Present') are available. If calculation is ambiguous or dates are missing, omit 'duration_months'.
- Be careful with list fields (e.g., 'responsibilities', 'skills'). Ensure they are correctly formatted as JSON arrays of strings or objects as per the schema.
- Pay close attention to nested objects and their required fields as defined in the schema.
- When extracting descriptions for projects or work experience, ensure all distinct bullet points or key achievements mentioned are captured, maintaining their original meaning.
- Distinguish between formal 'work_experience' (paid or significant, ongoing roles) and 'leadership' roles within clubs or short-term achievements. If a leadership role has substantial responsibilities and duration, it can be considered work experience. One-off hackathon wins or similar should go into 'awards'.
- If the resume contains a distinct section for 'Open Source Contributions' or 'Volunteering', extract details into corresponding fields if available in the schema.
- For 'Relevant Coursework', if listed as a general section, attempt to create a top-level list in the JSON if the schema supports it. If courses are tied to a specific education entry, list them there.

Target JSON Schema:```json
{LITERAL_EXTRACTION_SCHEMA_JSON_STR}
```"""

HUMAN_EXTRACTION_TEMPLATE = """Resume Text to Process:
```text
{resume_text}
```

Your Extracted JSON Output:"""

SYSTEM_ANALYSIS_CONTENT = f"""You are an expert AI career coach and resume reviewer with a keen eye for detail and actionable advice.


Your task is to analyze the provided structured resume data (which was previously extracted from a resume).
Based on this data, provide a comprehensive analysis.
You MUST output your analysis STRICTLY in JSON format, adhering to the JSON schema provided below.

Do NOT include any conversational introductions, apologies, summaries, or any text outside the single JSON object.

'resume_rating': Provide a rating from 1.0 to 10.0 (float). Be critical but fair.

'overall_feedback': A concise (1-3 insightful sentences) summary of the resume's effectiveness.

'strength_areas': List 2-4 key strengths evident from the resume data.

'improvement_areas': List 3-5 specific, actionable areas where the resume could be improved. Focus on content, clarity, impact, and structure. Be concrete.

'upskill_suggestions': Suggest 2-4 relevant skills for the candidate to learn or enhance, tailored to their apparent field/experience. For each, provide a brief 'reason' and optionally a list of 'resources' (e.g., "Online course on Advanced Python", "Official documentation for React").

'suggested_keywords_for_ats': List 3-5 keywords relevant to the candidate's profile that could improve ATS (Applicant Tracking System) performance.

'potential_roles': Suggest 1-3 job roles that seem like a good fit based on the resume.

Target JSON Schema:
```json
{LITERAL_ANALYSIS_SCHEMA_JSON_STR}
```"""

HUMAN_ANALYSIS_TEMPLATE = """Structured Resume Data (in JSON format) for Analysis:
```json
{structured_resume_data_json_str}
```

Your Analysis JSON Output:"""


extraction_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_EXTRACTION_CONTENT),
        ("human", HUMAN_EXTRACTION_TEMPLATE)
    ]
)

analysis_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_ANALYSIS_CONTENT),
        ("human", HUMAN_ANALYSIS_TEMPLATE)
    ]
)

if llm:
    extraction_chain = extraction_prompt | llm
    analysis_chain = analysis_prompt | llm


async def extract_structured_data_from_text(resume_text: str) -> Optional[schemas.ResumeExtractedData]:
    if not resume_text or not resume_text.strip():
        print("Resume text is empty or whitespace only; cannot extract data.")
        return None

    try:
        llm_response_str = await extraction_chain.ainvoke({
            "resume_text": resume_text
        })


        if not llm_response_str:
            print("LLM returned an empty string for extraction.")


        extracted_data = parse_llm_json_output(llm_response_str.content, schemas.ResumeExtractedData)

        return extracted_data
    
    except Exception as e:
        print(f"Unexpected error during LLM data extraction: {e}")
    
    return None


async def analyze_resume_with_llm(extracted_data: schemas.ResumeExtractedData) -> Optional[schemas.LLMAnalysisSchema]:
    if not analysis_chain:
        print("LLM analysis service (chain) is not available. Cannot process request.")
        return None
    if not extracted_data:
        print("Extracted resume data is None or empty; cannot perform analysis.")
        return None
    
    try:
        structured_resume_data_json_str = extracted_data.model_dump_json(indent=2)

        llm_response_str = await analysis_chain.ainvoke({
            "structured_resume_data_json_str": structured_resume_data_json_str
        })


        if not llm_response_str:
            print("LLM returned an empty string for analysis.")
            return None

        analysis_data = parse_llm_json_output(llm_response_str.content, schemas.LLMAnalysisSchema)


        if analysis_data:
            print("Successfully generated and validated LLM analysis of resume data.")
        else:
            print("Failed to parse or validate LLM analysis output against schema.")
        return analysis_data
    
    except Exception as e:
        print(f"Unexpected error during LLM resume analysis: {e}")
    
    return None