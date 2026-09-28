import json
import uuid

# We will generate a fictional handbook for "Apex Innovations".
# It will have 60 paragraphs, each containing a specific fact we can query.

facts = [
    ("The company was founded in 2010 by CEO Alice Smith.", "When was Apex Innovations founded and by whom?", "Apex Innovations was founded in 2010 by CEO Alice Smith."),
    ("Our headquarters is located at 123 Innovation Drive, Silicon Valley, CA.", "Where is the headquarters of Apex Innovations located?", "The headquarters is located at 123 Innovation Drive, Silicon Valley, CA."),
    ("We specialize in AI-driven enterprise solutions for the healthcare industry.", "What industry does Apex Innovations specialize in?", "Apex Innovations specializes in AI-driven enterprise solutions for the healthcare industry."),
    ("The flagship product, HealthAI, was launched in 2015.", "What is the flagship product of Apex Innovations and when was it launched?", "The flagship product is HealthAI, launched in 2015."),
    ("All employees receive 20 days of paid time off per year.", "How many days of paid time off do employees receive per year?", "Employees receive 20 days of paid time off per year."),
    ("The standard working hours are from 9 AM to 5 PM, Monday through Friday.", "What are the standard working hours at Apex Innovations?", "The standard working hours are from 9 AM to 5 PM, Monday through Friday."),
    ("Remote work is permitted for up to 2 days a week for all full-time staff.", "How many days a week are employees allowed to work remotely?", "Employees are allowed to work remotely for up to 2 days a week."),
    ("The company offers a 401(k) match up to 5% of the employee's salary.", "What is the company's 401(k) match policy?", "The company offers a 401(k) match up to 5% of the employee's salary."),
    ("Annual performance reviews are conducted every November.", "When are annual performance reviews conducted?", "Annual performance reviews are conducted every November."),
    ("The core values of Apex Innovations are Integrity, Innovation, and Inclusion.", "What are the core values of Apex Innovations?", "The core values are Integrity, Innovation, and Inclusion."),
    ("Employees can expense up to $500 per year for professional development courses.", "What is the annual allowance for professional development courses?", "Employees can expense up to $500 per year for professional development courses."),
    ("The company provides full health, dental, and vision insurance coverage.", "What types of insurance coverage does the company provide?", "The company provides full health, dental, and vision insurance coverage."),
    ("Maternity leave policy includes 12 weeks of fully paid leave.", "How many weeks of fully paid leave are included in the maternity leave policy?", "The maternity leave policy includes 12 weeks of fully paid leave."),
    ("Paternity leave policy includes 4 weeks of fully paid leave.", "What is the paternity leave policy at Apex Innovations?", "The paternity leave policy includes 4 weeks of fully paid leave."),
    ("Our primary data center is located in Ashburn, Virginia.", "Where is the primary data center located?", "The primary data center is located in Ashburn, Virginia."),
    ("The company uses AWS for cloud hosting and services.", "Which cloud provider does Apex Innovations use?", "The company uses AWS for cloud hosting and services."),
    ("The company's all-hands meetings are held on the first Monday of every month.", "When are the company's all-hands meetings held?", "All-hands meetings are held on the first Monday of every month."),
    ("Apex Innovations acquired MedTech Solutions in 2018.", "Which company did Apex Innovations acquire in 2018?", "Apex Innovations acquired MedTech Solutions in 2018."),
    ("The CTO of Apex Innovations is Bob Jones, who joined in 2012.", "Who is the CTO of Apex Innovations and when did he join?", "The CTO is Bob Jones, who joined in 2012."),
    ("The annual company retreat takes place every summer in Lake Tahoe.", "Where does the annual company retreat take place?", "The annual company retreat takes place in Lake Tahoe every summer."),
    ("Employees must submit expense reports by the 5th of the following month.", "When is the deadline to submit expense reports?", "Expense reports must be submitted by the 5th of the following month."),
    ("The employee referral bonus is $2000 for successful hires.", "What is the employee referral bonus for successful hires?", "The employee referral bonus is $2000 for successful hires."),
    ("The company provides a monthly stipend of $50 for home internet.", "How much is the monthly stipend for home internet?", "The company provides a monthly stipend of $50 for home internet."),
    ("Our customer support team operates 24/7 in three global shifts.", "What are the operating hours of the customer support team?", "The customer support team operates 24/7 in three global shifts."),
    ("The company dress code is business casual.", "What is the company dress code?", "The company dress code is business casual."),
    ("We use Slack as our primary internal communication tool.", "What is the primary internal communication tool used?", "Slack is the primary internal communication tool used."),
    ("The company intranet is named 'ApexHub'.", "What is the name of the company intranet?", "The company intranet is named 'ApexHub'."),
    ("Our main competitor in the market is HealthTech Dynamics.", "Who is the main competitor of Apex Innovations?", "The main competitor is HealthTech Dynamics."),
    ("Apex Innovations surpassed $100 million in ARR in 2021.", "When did Apex Innovations surpass $100 million in ARR?", "Apex Innovations surpassed $100 million in ARR in 2021."),
    ("The Board of Directors consists of 7 members.", "How many members are on the Board of Directors?", "The Board of Directors consists of 7 members."),
    ("Employees are eligible for a sabbatical after 5 years of continuous service.", "When are employees eligible for a sabbatical?", "Employees are eligible for a sabbatical after 5 years of continuous service."),
    ("The company offers free lunch on Fridays for in-office employees.", "What day is free lunch offered for in-office employees?", "Free lunch is offered on Fridays for in-office employees."),
    ("The engineering team follows a two-week sprint cycle.", "How long is the sprint cycle for the engineering team?", "The engineering team follows a two-week sprint cycle."),
    ("Our chief security officer is Sarah Lee.", "Who is the chief security officer?", "The chief security officer is Sarah Lee."),
    ("All employees must complete annual security awareness training in January.", "When must employees complete the annual security awareness training?", "Annual security awareness training must be completed in January."),
    ("The company's carbon neutral goal is set to be achieved by 2030.", "By what year does the company aim to be carbon neutral?", "The company aims to be carbon neutral by 2030."),
    ("Employee stock options vest over a four-year period with a one-year cliff.", "What is the vesting schedule for employee stock options?", "Employee stock options vest over a four-year period with a one-year cliff."),
    ("The marketing department is the largest team with 150 members.", "Which department is the largest and how many members does it have?", "The marketing department is the largest with 150 members."),
    ("We have regional offices in London, Tokyo, and Sydney.", "Where are the regional offices located?", "The regional offices are located in London, Tokyo, and Sydney."),
    ("The company mascot is a robot named 'Sparky'.", "What is the name of the company mascot?", "The company mascot is a robot named 'Sparky'."),
    ("The standard laptop provided to engineers is a 16-inch MacBook Pro.", "What is the standard laptop provided to engineers?", "The standard laptop provided to engineers is a 16-inch MacBook Pro."),
    ("The Q3 planning session is typically held in July.", "When is the Q3 planning session typically held?", "The Q3 planning session is typically held in July."),
    ("Our mobile application was released on iOS and Android in 2017.", "When was the mobile application released and on what platforms?", "The mobile application was released on iOS and Android in 2017."),
    ("Employees can take up to 3 days of paid volunteer leave per year.", "How many days of paid volunteer leave are employees allowed to take?", "Employees can take up to 3 days of paid volunteer leave per year."),
    ("The company's primary color code is #1A5276 (dark blue).", "What is the company's primary color code?", "The company's primary color code is #1A5276 (dark blue)."),
    ("We use Jira for project management and issue tracking.", "What tool is used for project management and issue tracking?", "Jira is used for project management and issue tracking."),
    ("The annual holiday party is held in the second week of December.", "When is the annual holiday party held?", "The annual holiday party is held in the second week of December."),
    ("The company has won the 'Best Place to Work' award for three consecutive years.", "How many times has the company won the 'Best Place to Work' award?", "The company has won the 'Best Place to Work' award for three consecutive years."),
    ("Our data privacy policy is GDPR compliant.", "Is the company's data privacy policy GDPR compliant?", "Yes, the data privacy policy is GDPR compliant."),
    ("The VP of Sales is Michael Chang.", "Who is the VP of Sales?", "The VP of Sales is Michael Chang."),
    ("There is an onsite gym available at the headquarters.", "Is there an onsite gym at the headquarters?", "Yes, there is an onsite gym available at the headquarters."),
    ("The company matched $500,000 in employee charitable donations last year.", "How much did the company match in employee charitable donations last year?", "The company matched $500,000 in employee charitable donations last year."),
    ("Our customer retention rate was 95% in the last fiscal year.", "What was the customer retention rate in the last fiscal year?", "The customer retention rate was 95% in the last fiscal year."),
    ("The IT support desk can be reached at extension 4357 (HELP).", "What extension can be used to reach the IT support desk?", "The IT support desk can be reached at extension 4357 (HELP)."),
    ("The company uses a bi-weekly payroll schedule.", "What is the payroll schedule at Apex Innovations?", "The company uses a bi-weekly payroll schedule."),
    ("Employees receive a $1000 bonus on their 5-year work anniversary.", "What bonus do employees receive on their 5-year work anniversary?", "Employees receive a $1000 bonus on their 5-year work anniversary."),
    ("The company started an internal mentorship program in 2020.", "When was the internal mentorship program started?", "The internal mentorship program was started in 2020."),
    ("We sponsor an annual hackathon named 'ApexHack'.", "What is the name of the annual hackathon sponsored by the company?", "The annual hackathon is named 'ApexHack'."),
    ("The CEO hosts a weekly AMA session on Friday afternoons.", "When does the CEO host the weekly AMA session?", "The CEO hosts a weekly AMA session on Friday afternoons."),
    ("The company implemented a four-day work week trial for the summer.", "What new work schedule trial was implemented for the summer?", "A four-day work week trial was implemented for the summer.")
]

paragraphs = [{"id": str(uuid.uuid4()), "content": fact[0]} for fact in facts]
eval_data = []

for i, fact in enumerate(facts):
    eval_data.append({
        "question": fact[1],
        "reference_answer": fact[2],
        "source_chunk_id": paragraphs[i]["id"]
    })

with open("seed_data.jsonl", "w") as f:
    for p in paragraphs:
        f.write(json.dumps(p) + "\\n")

with open("eval_questions.jsonl", "w") as f:
    for e in eval_data:
        f.write(json.dumps(e) + "\\n")

print("Generated seed_data.jsonl and eval_questions.jsonl")
