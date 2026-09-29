import json
from openai import OpenAI
import time

llm_judge = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

# 20 corrupted answers (wrong dates, numbers, names, unverified claims)
corrupted = [
    ("When was Apex Innovations founded and by whom?", "Apex Innovations was founded in 2010 by CEO Alice Smith.", "Apex Innovations was founded in 2012 by CEO Alice Smith."),
    ("Where is the headquarters of Apex Innovations located?", "The headquarters is located at 123 Innovation Drive, Silicon Valley, CA.", "The headquarters is located at 456 Innovation Drive, Silicon Valley, CA."),
    ("How many days of paid time off do employees receive per year?", "Employees receive 20 days of paid time off per year.", "Employees receive 15 days of paid time off per year."),
    ("What are the standard working hours at Apex Innovations?", "The standard working hours are from 9 AM to 5 PM, Monday through Friday.", "The standard working hours are from 8 AM to 4 PM, Monday through Friday."),
    ("How many days a week are employees allowed to work remotely?", "Employees are allowed to work remotely for up to 2 days a week.", "Employees can work remotely up to 3 days a week."),
    ("What is the company's 401(k) match policy?", "The company offers a 401(k) match up to 5% of the employee's salary.", "The company offers a 10% 401(k) match."),
    ("When are annual performance reviews conducted?", "Annual performance reviews are conducted every November.", "They are conducted in December."),
    ("What is the annual allowance for professional development courses?", "Employees can expense up to $500 per year for professional development courses.", "Employees get $1000 per year for courses."),
    ("How many weeks of fully paid leave are included in the maternity leave policy?", "The maternity leave policy includes 12 weeks of fully paid leave.", "The maternity leave policy includes 16 weeks of fully paid leave."),
    ("What is the paternity leave policy at Apex Innovations?", "The paternity leave policy includes 4 weeks of fully paid leave.", "The paternity leave policy includes 2 weeks of fully paid leave."),
    ("Where is the primary data center located?", "The primary data center is located in Ashburn, Virginia.", "The primary data center is located in Seattle, Washington."),
    ("Which cloud provider does Apex Innovations use?", "The company uses AWS for cloud hosting and services.", "The company uses Google Cloud Platform."),
    ("When are the company's all-hands meetings held?", "All-hands meetings are held on the first Monday of every month.", "All-hands meetings are held every Friday."),
    ("Which company did Apex Innovations acquire in 2018?", "Apex Innovations acquired MedTech Solutions in 2018.", "Apex Innovations acquired HealthTech Dynamics in 2018."),
    ("Who is the CTO of Apex Innovations and when did he join?", "The CTO is Bob Jones, who joined in 2012.", "The CTO is Sarah Lee, who joined in 2012."),
    ("Where does the annual company retreat take place?", "The annual company retreat takes place in Lake Tahoe every summer.", "The retreat takes place in Aspen every winter."),
    ("What is the employee referral bonus for successful hires?", "The employee referral bonus is $2000 for successful hires.", "The referral bonus is $1000."),
    ("How much is the monthly stipend for home internet?", "The company provides a monthly stipend of $50 for home internet.", "The stipend is $100 per month."),
    ("What are the operating hours of the customer support team?", "The customer support team operates 24/7 in three global shifts.", "Customer support is available 9 AM to 5 PM."),
    ("What is the company dress code?", "The company dress code is business casual.", "The company requires formal business attire.")
]

# 10 correct-but-reworded answers
reworded = [
    ("When was Apex Innovations founded and by whom?", "Apex Innovations was founded in 2010 by CEO Alice Smith.", "CEO Alice Smith started Apex Innovations in the year 2010."),
    ("Where is the headquarters of Apex Innovations located?", "The headquarters is located at 123 Innovation Drive, Silicon Valley, CA.", "You can find their main office in Silicon Valley, CA at 123 Innovation Dr."),
    ("How many days of paid time off do employees receive per year?", "Employees receive 20 days of paid time off per year.", "Staff are granted 20 days of PTO annually."),
    ("What are the standard working hours at Apex Innovations?", "The standard working hours are from 9 AM to 5 PM, Monday through Friday.", "Employees typically work Monday-Friday, 9 to 5."),
    ("How many days a week are employees allowed to work remotely?", "Employees are allowed to work remotely for up to 2 days a week.", "You can work from home a maximum of twice a week."),
    ("What is the company's 401(k) match policy?", "The company offers a 401(k) match up to 5% of the employee's salary.", "They will match your 401(k) contributions up to a limit of 5% of your pay."),
    ("When are annual performance reviews conducted?", "Annual performance reviews are conducted every November.", "Performance evaluations happen yearly during the month of November."),
    ("What is the annual allowance for professional development courses?", "Employees can expense up to $500 per year for professional development courses.", "There is a $500 yearly budget available for employees to spend on professional growth."),
    ("How many weeks of fully paid leave are included in the maternity leave policy?", "The maternity leave policy includes 12 weeks of fully paid leave.", "Mothers get 12 weeks off with full pay."),
    ("What is the paternity leave policy at Apex Innovations?", "The paternity leave policy includes 4 weeks of fully paid leave.", "Fathers receive 4 weeks of paid paternity leave.")
]

def evaluate_correctness(model_name: str, question: str, ground_truth: str, answer: str) -> int:
    prompt = f"""You are an expert evaluator. Evaluate the student's answer against the reference answer.
Question: {question}
Reference Answer: {ground_truth}
Student Answer: {answer}

Is the student's answer correct and factually consistent with the reference answer? Ignore phrasing, sentence fragments, and citation formats. Focus ONLY on whether the key facts match.
Respond with ONLY "1" if correct, or "0" if incorrect."""
    
    try:
        response = llm_judge.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            seed=42
        )
        result = response.choices[0].message.content.strip()
        if "1" in result:
            return 1
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 0

for model in ["llama3.1", "qwen2.5:7b"]:
    print(f"--- Testing {model} ---")
    c_scores = sum(evaluate_correctness(model, q, gt, a) for q, gt, a in corrupted)
    r_scores = sum(evaluate_correctness(model, q, gt, a) for q, gt, a in reworded)
    
    print(f"Corrupted marked WRONG: {20 - c_scores}/20")
    print(f"Reworded marked CORRECT: {r_scores}/10")
    print()
