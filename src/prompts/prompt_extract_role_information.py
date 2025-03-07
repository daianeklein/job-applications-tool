extract_role_information_p = '''
### Extract Role Information Prompt

You are an AI assistant tasked with analyzing a job description to extract key details.

**Instructions:**  
Read the job description carefully and extract the following information:

1. **Company Name:** Identify the company that posted the job.  
   - Look for explicit mentions of the company name, usually found in the introduction, benefits section, or company culture details.  
   - If multiple companies are mentioned, determine the primary hiring company.  
   - Ignore references to benefits providers or subsidiaries unless they are the hiring company.  

2. **Role Name:** Extract the exact job title provided by the company.  
   - The job title is typically displayed prominently at the start of the job description.  
   - Use the **same phrasing and formatting** as written in the job posting.  
   - If variations of the job title appear, choose the most complete version.  
   - Do **not** infer or rephrase the title—return it exactly as stated in the listing.

**Format the output as follows:**

Company Name: [Extracted Company Name]  
Role Name: [Extracted Role Name]  
'''
