from openai import OpenAI

llm_judge = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

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

def evaluate_correctness(question: str, ground_truth: str, answer: str):
    prompt = f"""You are an expert evaluator. Evaluate the student's answer against the reference answer.
Question: {question}
Reference Answer: {ground_truth}
Student Answer: {answer}

Is the student's answer correct and factually consistent with the reference answer? Ignore phrasing, sentence fragments, and citation formats. Focus ONLY on whether the key facts match.
Respond with ONLY "1" if correct, or "0" if incorrect."""
    
    try:
        response = llm_judge.chat.completions.create(
            model="llama3.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            seed=42
        )
        result = response.choices[0].message.content.strip()
        if "1" in result:
            reasoning_prompt = f"""You are an expert evaluator. Evaluate the student's answer against the reference answer.
Question: {question}
Reference Answer: {ground_truth}
Student Answer: {answer}

You marked this student answer as CORRECT (1). Please explain your reasoning. Focus on why the facts match despite the text being different."""
            
            resp = llm_judge.chat.completions.create(
                model="llama3.1",
                messages=[{"role": "user", "content": reasoning_prompt}],
                temperature=0.0,
                seed=42
            )
            print(f"\n[PASSED CORRUPTED ANSWER]")
            print(f"Reference: {ground_truth}")
            print(f"Corrupted: {answer}")
            print(f"Reasoning:\n{resp.choices[0].message.content.strip()}")
            
    except Exception as e:
        print(f"Error: {e}")

print("Running llama3.1 on corrupted answers to find false positives...")
for q, gt, a in corrupted:
    evaluate_correctness(q, gt, a)
