export interface Resume {
    id: number;
    file_name: string;
    name: string | null;
    email: string | null;
    uploaded_at: string;
}

export interface ResumeInfo {
    id: number;
    file_name: string;
    summary: string | null;
    raw_text: string;
    uploaded_at: string;

    contact_info: {
        name: string | null;
        email: string | null;
        address: string | null;
        phone: string | null;
        linkedin: string | null;
        github: string | null;
        portfolio_url: string | null;
    };
    skills: {
        technical: Array<{ name: string; proficiency: string | null }>;
        soft: string[];
        languages: string[];
        tools: Array<{ name: string; proficiency: string | null }>;
    };
    work_experience: Array<{
        company: string;
        role: string;
        location: string | null;
        start_date: string | null;
        end_date: string | null;
        duration_months: number | null;
        responsibilities: string[];
        achievements: string[];
    }>;
    projects: Array<{
        name: string;
        description: string;
        technologies_used: string[];
        link: string | null;
        repo_link: string | null;
    }>;
    certifications: Array<{
        name: string;
        issuer: string;
        issue_date: string | null;
        expiration_date: string | null;
        credential_id: string | null;
        credential_url: string | null;
    }>;
    education: Array<{
        institution: string;
        degree: string;
        major: string;
        start_date: string | null;
        end_date: string | null;
        gpa: string | null;
        location: string | null;
        relevant_coursework: string[];
    }>;
    awards: Array<{
        name: string;
        issuer: string | null;
        date: string | null;
        description: string | null;
    }>;
    llm_analysis: {
        resume_rating: number;
        overall_feedback: string;
        strength_areas: string[];
        improvement_areas: string[];
        upskill_suggestions: Array<{
            skill: string;
            reason: string;
            resources: string[];
        }>;
        suggested_keywords_for_ats: string[];
        potential_roles: string[];
    }
}