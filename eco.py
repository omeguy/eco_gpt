import pdfplumber
import re
import pandas as pd

class StudySession:
    def __init__(self, module_number, session_number):
        self.module_number = module_number
        self.session_number = session_number
        self.intro = ""
        self.learning_outcomes = ""
        self.content = ""
        self.summary = "" 
        self.assessment_questions = "" 

def extract_sessions_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        current_module_number = 0
        current_session_number = 0
        current_session = None
        study_sessions = []

        for page in pdf.pages:
            text = page.extract_text()
            module_match = re.search(r"Module (\d+)", text)
            if module_match:
                current_module_number = int(module_match.group(1))

            session_match = re.search(r"Study session (\d+)", text)
            if session_match:
                current_session_number = int(session_match.group(1))
                if current_session is not None:
                    study_sessions.append(current_session)
                current_session = StudySession(current_module_number, current_session_number)

            if current_session is not None:
                intro_match = re.search(r"Introduction(.*?)(?=Learning Outcomes for)", text, re.DOTALL | re.IGNORECASE)

                if intro_match:
                    current_session.intro = intro_match.group(1).strip()

                outcomes_match = re.search(r"Learning Outcomes for(.*?)(?=\d+\.\d)", text, re.DOTALL)
                if outcomes_match:
                    current_session.learning_outcomes = outcomes_match.group(1).strip()

                # revised content match pattern to exclude summary and questions
                content_match = re.search(r"(\d+\.\d.*?)(?=Summary of module|Self-Assessment Questions for|$)", text, re.DOTALL)
                if content_match:
                    current_session.content += content_match.group(1).strip()

                # new match patterns for summary and self-assessment questions
                summary_match = re.search(r"Summary of module(.*?)(?=Self-Assessment Questions for|$)", text, re.DOTALL)
                if summary_match:
                    current_session.summary += summary_match.group(1).strip()

                questions_match = re.search(r"Self-Assessment Questions for(.*?)(?=Solution to MCQs|$)", text, re.DOTALL)
                if questions_match:
                    current_session.assessment_questions += questions_match.group(1).strip()

        if current_session is not None:
            study_sessions.append(current_session)

    return study_sessions

sessions = extract_sessions_from_pdf('pdf/gst301.pdf')

data = []
for session in sessions:
    data.append([
        session.module_number,
        session.session_number,
        session.intro,
        session.learning_outcomes,
        session.content,
        session.summary,
        session.assessment_questions,
    ])

# Define the column names for your table

column_names = ["Module Number", "Session Number", "Introduction", "Learning Outcomes", "Content", "Summary", "Self-Assessment Questions"]

# Create a DataFrame from your data
df = pd.DataFrame(data, columns=column_names)

# Now you can save this DataFrame to a csv file
df.to_csv("sessions.csv", index=False)
