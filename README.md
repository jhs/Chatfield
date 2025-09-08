# Chatfield: Conversational Data Collection

🎥 **Watch me develop this live!** Follow along as I build Chatfield in real-time: [YouTube Development Streams](https://www.youtube.com/@JasonSmithBuild/streams)

Transform data collection from rigid forms into natural conversations powered by LLMs.

Chatfield provides implementations in both Python and TypeScript/JavaScript, allowing you to create conversational interfaces for gathering structured data in any application.

## Features

- **Natural Conversations**: Replace traditional forms with engaging dialogues
- **LLM-Powered Validation**: Smart validation and guidance through conversation
- **Type Safety**: Full type support in both Python and TypeScript
- **Rich Transformations**: Convert responses into any data type with casts
- **Framework Integration**: React components, CopilotKit support, and more
- **Flexible APIs**: Multiple API styles to suit different preferences

## Quick Start

### Python Implementation

```python
from chatfield import chatfield, Interviewer

# Create a simple form
contact_form = (chatfield()
    .field("name", "Your full name")
    .field("email", "Your email address")
    .field("message", "How can we help you?")
    .build())

# Run the conversation
interviewer = Interviewer(contact_form)
user_input = None
while not contact_form._done:
    message = interviewer.go(user_input)
    print(message)
    user_input = input("> ")

# Access collected data
print(f"Name: {contact_form.name}")
print(f"Email: {contact_form.email}")
print(f"Message: {contact_form.message}")
```

### TypeScript/JavaScript Implementation

```typescript
import { chatfield, Interviewer } from '@chatfield/core'

// Create a simple form
const contactForm = chatfield()
  .field('name', 'Your full name')
  .field('email', 'Your email address')
  .field('message', 'How can we help you?')
  .build()

// Run the conversation
const interviewer = new Interviewer(contactForm)
let userInput: string | null = null
while (!contactForm._done) {
  const message = await interviewer.go(userInput)
  console.log(message)
  userInput = await getUserInput() // Your input method
}

// Access collected data
console.log(`Name: ${contactForm.name}`)
console.log(`Email: ${contactForm.email}`)
console.log(`Message: ${contactForm.message}`)
```

## Examples: Basic to Advanced

### 1. Simple Contact Form

**Python:**
```python
from chatfield import chatfield, Interviewer

# Basic form with no validation
simple_form = (chatfield()
    .field("name", "Your name")
    .field("email", "Your email")
    .build())
```

**TypeScript:**
```typescript
import { chatfield, Interviewer } from '@chatfield/core'

// Basic form with no validation
const simpleForm = chatfield()
  .field('name', 'Your name')
  .field('email', 'Your email')
  .build()
```

### 2. Adding Validation Rules

**Python:**
```python
# Form with validation requirements
validated_form = (chatfield()
    .field("email", "Your email address")
        .must("be a valid email format")
        .must("not be a temporary email")
    .field("phone", "Phone number")
        .must("include area code")
        .reject("letters or special characters except + and -")
    .field("website", "Your website URL")
        .hint("Include https:// prefix")
        .must("be a valid URL")
    .build())
```

**TypeScript:**
```typescript
// Form with validation requirements
const validatedForm = chatfield()
  .field('email', 'Your email address')
    .must('be a valid email format')
    .must('not be a temporary email')
  .field('phone', 'Phone number')
    .must('include area code')
    .reject('letters or special characters except + and -')
  .field('website', 'Your website URL')
    .hint('Include https:// prefix')
    .must('be a valid URL')
  .build()
```

### 3. Configuring Conversation Roles

**Python:**
```python
# Customize the interviewer and interviewee personas
support_chat = (chatfield()
    .alice()  # Configure interviewer
        .type("Technical Support Agent")
        .trait("Patient and thorough")
        .trait("Ask clarifying questions")
    .bob()    # Configure interviewee
        .type("Customer")
        .trait("May not know technical terms")
    .field("issue", "What problem are you experiencing?")
        .must("be specific about error messages")
    .field("steps_tried", "What have you already tried?")
    .build())
```

**TypeScript:**
```typescript
// Customize the interviewer and interviewee personas
const supportChat = chatfield()
  .alice()  // Configure interviewer
    .type('Technical Support Agent')
    .trait('Patient and thorough')
    .trait('Ask clarifying questions')
  .bob()    // Configure interviewee
    .type('Customer')
    .trait('May not know technical terms')
  .field('issue', 'What problem are you experiencing?')
    .must('be specific about error messages')
  .field('steps_tried', 'What have you already tried?')
  .build()
```

### 4. Type Transformations (Basic)

**Python:**
```python
# Convert responses to specific data types
survey = (chatfield()
    .field("age", "Your age")
        .as_int()  # Converts "twenty-five" → 25
    .field("salary", "Expected salary")
        .as_float()  # Converts "85.5k" → 85500.0
    .field("remote", "Open to remote work?")
        .as_bool()  # Converts "yeah" → True
    .field("skills", "Your top skills")
        .as_list()  # Converts "Python, React, and SQL" → ["Python", "React", "SQL"]
    .build())

# Access transformed values after collection
age_int = survey.age.as_int        # integer
salary = survey.salary.as_float    # float
is_remote = survey.remote.as_bool  # boolean
skill_list = survey.skills.as_list # list
```

**TypeScript:**
```typescript
// Convert responses to specific data types
const survey = chatfield()
  .field('age', 'Your age')
    .asInt()  // Converts "twenty-five" → 25
  .field('salary', 'Expected salary')
    .asFloat()  // Converts "85.5k" → 85500.0
  .field('remote', 'Open to remote work?')
    .asBool()  // Converts "yeah" → true
  .field('skills', 'Your top skills')
    .asList()  // Converts "Python, React, and SQL" → ["Python", "React", "SQL"]
  .build()

// Access transformed values after collection
const ageInt = survey.age.asInt        // number
const salary = survey.salary.asFloat   // number
const isRemote = survey.remote.asBool  // boolean
const skillList = survey.skills.asList // array
```

### 5. Advanced Transformations

**Python:**
```python
# Multiple transformations on the same field
analytics = (chatfield()
    .field("visitors", "Monthly website visitors")
        .as_int()  # Basic number
        .as_lang('es')  # Spanish translation
        .as_lang('fr')  # French translation
        .as_bool('high_traffic', 'True if > 10000')  # Custom boolean
        .as_str('formatted', 'With commas like 1,234')  # Custom format
        .as_percent('growth', 'As percentage of 1M target')  # Percentage
    .build())

# After user says "fifty thousand":
visitors = analytics.visitors                      # "50000"
visitors_int = analytics.visitors.as_int           # 50000
visitors_es = analytics.visitors.as_lang_es        # "cincuenta mil"
visitors_fr = analytics.visitors.as_lang_fr        # "cinquante mille"
is_high = analytics.visitors.as_bool_high_traffic  # True
formatted = analytics.visitors.as_str_formatted    # "50,000"
growth = analytics.visitors.as_percent_growth      # 0.05
```

**TypeScript:**
```typescript
// Multiple transformations on the same field
const analytics = chatfield()
  .field('visitors', 'Monthly website visitors')
    .asInt()  // Basic number
    .asLang('es')  // Spanish translation
    .asLang('fr')  // French translation
    .asBool('highTraffic', 'True if > 10000')  // Custom boolean
    .asStr('formatted', 'With commas like 1,234')  // Custom format
    .asPercent('growth', 'As percentage of 1M target')  // Percentage
  .build()

// After user says "fifty thousand":
const visitors = analytics.visitors                      // "50000"
const visitorsInt = analytics.visitors.asInt             // 50000
const visitorsEs = analytics.visitors.asLangEs           // "cincuenta mil"
const visitorsFr = analytics.visitors.asLangFr           // "cinquante mille"
const isHigh = analytics.visitors.asBoolHighTraffic      // true
const formatted = analytics.visitors.asStrFormatted      // "50,000"
const growth = analytics.visitors.asPercentGrowth        // 0.05
```

### 6. Choice Cardinality (Selection Patterns)

**Python:**
```python
# Control how many options can be selected
preferences = (chatfield()
    # Exactly one choice
    .field("department")
        .as_one('dept', 'Engineering', 'Sales', 'Marketing', 'Support')
    
    # Zero or one choice (optional)
    .field("mentor")
        .as_maybe('person', 'Alice', 'Bob', 'Charlie')
        .desc("Would you like a mentor? (optional)")
    
    # One or more choices (at least one required)
    .field("languages")
        .as_multi('langs', 'Python', 'JavaScript', 'Go', 'Rust', 'Java')
        .desc("Programming languages you know")
    
    # Zero or more choices (completely optional)
    .field("interests")
        .as_any('topics', 'ML', 'Web', 'Mobile', 'DevOps', 'Security')
        .desc("Technical interests (select any that apply)")
    
    .build())

# After collection:
dept = preferences.department.as_one_dept        # "Engineering" (exactly one)
mentor = preferences.mentor.as_maybe_person      # "Alice" or None
langs = preferences.languages.as_multi_langs     # {"Python", "JavaScript"}
interests = preferences.interests.as_any_topics  # {"ML", "Security"} or set()
```

**TypeScript:**
```typescript
// Control how many options can be selected
const preferences = chatfield()
  // Exactly one choice
  .field('department')
    .asOne('dept', 'Engineering', 'Sales', 'Marketing', 'Support')
  
  // Zero or one choice (optional)
  .field('mentor')
    .asMaybe('person', 'Alice', 'Bob', 'Charlie')
    .desc('Would you like a mentor? (optional)')
  
  // One or more choices (at least one required)
  .field('languages')
    .asMulti('langs', 'Python', 'JavaScript', 'Go', 'Rust', 'Java')
    .desc('Programming languages you know')
  
  // Zero or more choices (completely optional)
  .field('interests')
    .asAny('topics', 'ML', 'Web', 'Mobile', 'DevOps', 'Security')
    .desc('Technical interests (select any that apply)')
  
  .build()

// After collection:
const dept = preferences.department.asOneDept        // "Engineering" (exactly one)
const mentor = preferences.mentor.asMaybePerson      // "Alice" or null
const langs = preferences.languages.asMultiLangs     // Set {"Python", "JavaScript"}
const interests = preferences.interests.asAnyTopics  // Set {"ML", "Security"} or Set {}
```

### 7. Special Field Types

**Python:**
```python
# Confidential and conclusion fields
interview = (chatfield()
    # Regular fields collected during conversation
    .field("experience", "Years of experience")
        .as_int()
    
    # Confidential: tracked silently, never mentioned
    .field("shows_leadership")
        .desc("Demonstrates leadership qualities")
        .confidential()
        .as_bool()
    
    # Conclusion: evaluated only after conversation ends
    .field("overall_fit")
        .desc("Overall fit for the role")
        .conclude()
        .as_one('rating', 'poor', 'fair', 'good', 'excellent')
    
    .build())
```

**TypeScript:**
```typescript
// Confidential and conclusion fields
const interview = chatfield()
  // Regular fields collected during conversation
  .field('experience', 'Years of experience')
    .asInt()
  
  // Confidential: tracked silently, never mentioned
  .field('showsLeadership')
    .desc('Demonstrates leadership qualities')
    .confidential()
    .asBool()
  
  // Conclusion: evaluated only after conversation ends
  .field('overallFit')
    .desc('Overall fit for the role')
    .conclude()
    .asOne('rating', 'poor', 'fair', 'good', 'excellent')
  
  .build()
```

### 8. Context and Quote Extraction

**Python:**
```python
# Capture conversation context and exact quotes
research = (chatfield()
    .field("problem", "What problem are you solving?")
        .as_quote()    # Captures exact words
        .as_context()  # Captures conversation context
    
    .field("budget", "What's your budget?")
        .as_int()
        .as_quote()    # "around fifty thousand dollars"
        .as_context()  # Surrounding discussion about constraints
    
    .build())

# After collection:
problem_quote = research.problem.as_quote      # Exact user words
problem_context = research.problem.as_context  # Conversation leading to answer
budget_number = research.budget.as_int         # 50000
budget_quote = research.budget.as_quote        # "around fifty thousand dollars"
```

**TypeScript:**
```typescript
// Capture conversation context and exact quotes
const research = chatfield()
  .field('problem', 'What problem are you solving?')
    .asQuote()    // Captures exact words
    .asContext()  // Captures conversation context
  
  .field('budget', "What's your budget?")
    .asInt()
    .asQuote()    // "around fifty thousand dollars"
    .asContext()  // Surrounding discussion about constraints
  
  .build()

// After collection:
const problemQuote = research.problem.asQuote      // Exact user words
const problemContext = research.problem.asContext  // Conversation leading to answer
const budgetNumber = research.budget.asInt         // 50000
const budgetQuote = research.budget.asQuote        // "around fifty thousand dollars"
```

### 9. Complex Validation with Multiple Rules

**Python:**
```python
# Combine multiple validation strategies
application = (chatfield()
    .field("project_url", "GitHub project URL")
        .must("be a GitHub repository URL")
        .must("be a public repository")
        .reject("private or 404 repos")
        .hint("Format: https://github.com/username/repo")
    
    .field("experience_summary")
        .must("mention specific technologies")
        .must("include years of experience")
        .must("describe at least one project")
        .reject("vague statements like 'various projects'")
        .hint("Be specific about your contributions")
    
    .build())
```

**TypeScript:**
```typescript
// Combine multiple validation strategies
const application = chatfield()
  .field('projectUrl', 'GitHub project URL')
    .must('be a GitHub repository URL')
    .must('be a public repository')
    .reject('private or 404 repos')
    .hint('Format: https://github.com/username/repo')
  
  .field('experienceSummary')
    .must('mention specific technologies')
    .must('include years of experience')
    .must('describe at least one project')
    .reject("vague statements like 'various projects'")
    .hint('Be specific about your contributions')
  
  .build()
```

### 10. Dynamic Traits (Conversation Adaptation)

**Python:**
```python
# Traits that activate based on conversation
adaptive_interview = (chatfield()
    .alice()
        .type("Career Counselor")
    .bob()
        .type("Professional")
        .trait.possible("junior", "less than 3 years experience mentioned")
        .trait.possible("senior", "10+ years or leadership experience")
        .trait.possible("career_changer", "switching industries")
    
    .field("background", "Tell me about your background")
    .field("goals", "What are your career goals?")
    
    .build())

# After conversation, check activated traits:
# interview._chatfield['roles']['bob']['possible_traits']['senior']['active']
```

**TypeScript:**
```typescript
// Traits that activate based on conversation
const adaptiveInterview = chatfield()
  .alice()
    .type('Career Counselor')
  .bob()
    .type('Professional')
    .trait.possible('junior', 'less than 3 years experience mentioned')
    .trait.possible('senior', '10+ years or leadership experience')
    .trait.possible('careerChanger', 'switching industries')
  
  .field('background', 'Tell me about your background')
  .field('goals', 'What are your career goals?')
  
  .build()

// After conversation, check activated traits:
// interview._chatfield.roles.bob.possible_traits.senior.active
```

### 11. Complete Application Example

**Python:**
```python
from chatfield import chatfield, Interviewer

# Full-featured job application
job_application = (chatfield()
    .type("SoftwareEngineerApplication")
    .desc("Senior Software Engineer Position")
    
    # Configure personas
    .alice()
        .type("Hiring Manager")
        .trait("Professional and encouraging")
        .trait("Values specific examples")
    
    .bob()
        .type("Candidate")
        .trait.possible("startup_experience", "mentions startups or small teams")
        .trait.possible("enterprise_experience", "mentions large companies")
    
    # Basic information with validation
    .field("name", "Your full name")
        .must("include first and last name")
    
    .field("email", "Email address")
        .must("be a valid email")
    
    # Experience with transformations
    .field("years_experience", "Years of professional experience")
        .as_int()
        .must("be realistic (0-50 years)")
        .as_bool('senior', 'True if >= 5 years')
        .as_bool('lead', 'True if >= 8 years')
    
    # Skills with multi-selection
    .field("primary_languages")
        .desc("Primary programming languages")
        .as_multi('langs', 'Python', 'JavaScript', 'Go', 'Java', 'C++', 'Rust')
        .must("select at least one")
    
    .field("frameworks")
        .desc("Frameworks you're proficient with")
        .as_any('tools', 'React', 'Django', 'Flask', 'FastAPI', 'Node.js', 'Spring')
    
    # Salary with transformations
    .field("salary_expectation", "Salary expectations")
        .hint("You can give a range")
        .as_int()  # Converts to number
        .as_str('formatted', 'Formatted as $XXX,XXX')
    
    # Availability
    .field("start_date", "When can you start?")
        .must("be specific (e.g., 2 weeks, immediately, specific date)")
    
    # Location preferences
    .field("work_location")
        .desc("Preferred work arrangement")
        .as_one('preference', 'Remote', 'Hybrid', 'Office')
    
    # Confidential assessments (never mentioned in conversation)
    .field("communication_quality")
        .desc("Quality of communication during interview")
        .confidential()
        .as_one('level', 'poor', 'adequate', 'good', 'excellent')
    
    # Final evaluation (assessed after conversation)
    .field("recommendation")
        .desc("Hiring recommendation based on conversation")
        .conclude()
        .as_one('decision', 'reject', 'maybe', 'interview', 'strong_yes')
    
    .build())

# Run the interview
interviewer = Interviewer(job_application)
user_input = None

while not job_application._done:
    message = interviewer.go(user_input)
    if message:
        print(f"Interviewer: {message}")
    if not job_application._done:
        user_input = input("You: ")

# Access all collected data
print(f"Name: {job_application.name}")
print(f"Years: {job_application.years_experience.as_int}")
print(f"Is Senior: {job_application.years_experience.as_bool_senior}")
print(f"Languages: {job_application.primary_languages.as_multi_langs}")
print(f"Salary: {job_application.salary_expectation.as_str_formatted}")
print(f"Recommendation: {job_application.recommendation}")
```

**TypeScript:**
```typescript
import { chatfield, Interviewer } from '@chatfield/core'

// Full-featured job application
const jobApplication = chatfield()
  .type('SoftwareEngineerApplication')
  .desc('Senior Software Engineer Position')
  
  // Configure personas
  .alice()
    .type('Hiring Manager')
    .trait('Professional and encouraging')
    .trait('Values specific examples')
  
  .bob()
    .type('Candidate')
    .trait.possible('startupExperience', 'mentions startups or small teams')
    .trait.possible('enterpriseExperience', 'mentions large companies')
  
  // Basic information with validation
  .field('name', 'Your full name')
    .must('include first and last name')
  
  .field('email', 'Email address')
    .must('be a valid email')
  
  // Experience with transformations
  .field('yearsExperience', 'Years of professional experience')
    .asInt()
    .must('be realistic (0-50 years)')
    .asBool('senior', 'True if >= 5 years')
    .asBool('lead', 'True if >= 8 years')
  
  // Skills with multi-selection
  .field('primaryLanguages')
    .desc('Primary programming languages')
    .asMulti('langs', 'Python', 'JavaScript', 'Go', 'Java', 'C++', 'Rust')
    .must('select at least one')
  
  .field('frameworks')
    .desc('Frameworks you\'re proficient with')
    .asAny('tools', 'React', 'Django', 'Flask', 'FastAPI', 'Node.js', 'Spring')
  
  // Salary with transformations
  .field('salaryExpectation', 'Salary expectations')
    .hint('You can give a range')
    .asInt()  // Converts to number
    .asStr('formatted', 'Formatted as $XXX,XXX')
  
  // Availability
  .field('startDate', 'When can you start?')
    .must('be specific (e.g., 2 weeks, immediately, specific date)')
  
  // Location preferences
  .field('workLocation')
    .desc('Preferred work arrangement')
    .asOne('preference', 'Remote', 'Hybrid', 'Office')
  
  // Confidential assessments (never mentioned in conversation)
  .field('communicationQuality')
    .desc('Quality of communication during interview')
    .confidential()
    .asOne('level', 'poor', 'adequate', 'good', 'excellent')
  
  // Final evaluation (assessed after conversation)
  .field('recommendation')
    .desc('Hiring recommendation based on conversation')
    .conclude()
    .asOne('decision', 'reject', 'maybe', 'interview', 'strong_yes')
  
  .build()

// Run the interview
const interviewer = new Interviewer(jobApplication)
let userInput: string | null = null

while (!jobApplication._done) {
  const message = await interviewer.go(userInput)
  if (message) {
    console.log(`Interviewer: ${message}`)
  }
  if (!jobApplication._done) {
    userInput = await getUserInput() // Your input method
  }
}

// Access all collected data
console.log(`Name: ${jobApplication.name}`)
console.log(`Years: ${jobApplication.yearsExperience.asInt}`)
console.log(`Is Senior: ${jobApplication.yearsExperience.asBoolSenior}`)
console.log(`Languages: ${jobApplication.primaryLanguages.asMultiLangs}`)
console.log(`Salary: ${jobApplication.salaryExpectation.asStrFormatted}`)
console.log(`Recommendation: ${jobApplication.recommendation}`)
```

## Alternative APIs

### Decorator API (Python)
```python
from chatfield import Interview, alice, bob
from chatfield import must, reject, hint
from chatfield import as_int, as_bool, as_lang, as_multi

@alice("Recruiter")
@alice.trait("Professional and friendly")
@bob("Job Applicant")
class JobApplication(Interview):
    """Collecting job application details"""
    
    @must("include first and last name")
    def full_name(): 
        "Your complete name"
    
    @must("be between 0 and 50")
    @as_int
    def years_experience(): 
        "Years of relevant experience"
    
    @as_multi("Python", "JavaScript", "Go", "Rust")
    def languages(): 
        "Programming languages you know"
    
    @as_bool
    def requires_visa(): 
        "Do you require visa sponsorship?"

# Use the decorated class
app = JobApplication()
interviewer = Interviewer(app)
```

### Special Transformations

#### JSON/Dictionary Parsing
```python
# Parse complex structured data
api_form = (chatfield()
    .field("config", "Paste your configuration")
        .as_dict()  # or as_obj() - parses JSON/dict
    .field("metadata", "Additional metadata")
        .as_obj()  # Converts to dictionary
    .build())

# User provides: "timeout: 30, retries: 3, debug: true"
config_dict = api_form.config.as_dict  # {'timeout': 30, 'retries': 3, 'debug': True}
```

#### Set Operations
```python
# Extract unique values as sets
analysis = (chatfield()
    .field("tags", "Relevant tags for this article")
        .as_set()  # Unique values only
        .as_set('keywords', 'Extract main keywords')
        .as_set('entities', 'Named entities mentioned')
    .build())

# User: "machine learning, AI, machine learning, and neural networks"
tags = analysis.tags.as_set           # {'machine learning', 'AI', 'neural networks'}
keywords = analysis.tags.as_set_keywords  # Custom set extraction
```

#### Language Translations
```python
# Multi-language support
international = (chatfield()
    .field("greeting", "Your greeting message")
        .as_lang('es')   # Spanish
        .as_lang('fr')   # French
        .as_lang('de')   # German
        .as_lang('ja')   # Japanese
        .as_lang('zh')   # Chinese
    .build())

# User: "Hello, nice to meet you"
greeting_es = international.greeting.as_lang_es  # "Hola, encantado de conocerte"
greeting_fr = international.greeting.as_lang_fr  # "Bonjour, ravi de vous rencontrer"
```

## Advanced Features

### Conversation Context Preservation
```python
# Access the conversational context and exact quotes
feedback = (chatfield()
    .field("issue", "Describe the problem")
        .as_quote()    # Exact words used
        .as_context()  # Conversation leading to this
    .build())

# After: "Well, I was trying to login yesterday and it kept failing"
issue_quote = feedback.issue.as_quote      # Exact quote
issue_context = feedback.issue.as_context  # Full context
```

### Custom Transformation Prompts
```python
# Define custom transformation logic
custom = (chatfield()
    .field("code", "Paste your code snippet")
        .as_str('minified', 'Remove all whitespace and comments')
        .as_str('documented', 'Add inline documentation')
        .as_bool('has_bugs', 'True if contains obvious bugs')
        .as_list('functions', 'List of function names')
    .build())
```

### Percentage Calculations
```python
# Work with percentages
metrics = (chatfield()
    .field("completion", "Project completion status")
        .as_percent()  # Converts "75%" or "three quarters" to 0.75
    .field("confidence", "Confidence level")
        .as_percent()  # Handles various formats
    .build())

completion = metrics.completion.as_percent  # 0.75 (float between 0.0-1.0)
```

## Project Structure

This repository contains two parallel implementations:

### `/chatfield-py` - Python Implementation
- Decorator-based API with LangGraph orchestration
- Builder pattern as alternative API
- OpenAI integration with extensible LLM support
- Rich validation and transformation system
- Full async support and type hints

### `/chatfield-js` - TypeScript/JavaScript Implementation  
- NPM package `@chatfield/core`
- Primary builder pattern API
- React hooks and components
- CopilotKit integration
- Multiple API styles (builder, decorator, schema)

## Installation

### Python
```bash
cd chatfield-py
pip install .
```

### TypeScript/JavaScript
```bash
cd chatfield-js
npm install
```

## Documentation

- [Python Documentation](./chatfield-py/README.md) - Full API reference and advanced features
- [TypeScript/JavaScript Documentation](./chatfield-js/README.md) - React integration and builder patterns
- [Python Examples](./chatfield-py/examples/) - Working examples with all features
- [TypeScript Examples](./chatfield-js/examples/) - Framework integration examples

## Development

Both implementations share the same core concepts but are tailored to their respective ecosystems:

- **Python**: Uses decorators, LangGraph for orchestration, and async/await patterns
- **TypeScript**: Provides React integration, builder patterns, and full type safety

### Contributing

We welcome contributions to either implementation! Please see the individual project directories for specific development setup instructions.

### Testing

```bash
# Python tests
cd chatfield-py && python -m pytest

# JavaScript tests  
cd chatfield-js && npm test
```

## License

Apache License 2.0 - See [LICENSE](./LICENSE) for details.

## API Keys

Both implementations require an OpenAI API key:

```bash
export OPENAI_API_KEY=your-api-key
```

## Learn More

- **Python Details**: See [chatfield-py/CLAUDE.md](./chatfield-py/CLAUDE.md) for implementation details
- **TypeScript Details**: See [chatfield-js/CLAUDE.md](./chatfield-js/CLAUDE.md) for implementation details

## Status

Both implementations are in active development with feature parity as a goal. The Python implementation currently has more complete decorator support, while the TypeScript implementation offers better framework integrations.