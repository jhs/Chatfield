# Chatfield: Conversational Data Collection AI Agent

🎥 **[Watch me develop this live](https://www.youtube.com/@JasonSmithBuild/streams)**.

Chatfield is a library to collect information using conversation rather than forms.

- Chatfield supports **Python** and **TypeScript** as well as JavaScript
- Chatfield supports **Server** and **Browser** operation
- Chatfield works in **any User Interface** because it computes what to say, now how to present

```typescript
import { chatfield } from 'chatfield' // Or Python: from chatfield import chatfield

const trip = chatfield()              // Identical API in Python and TypeScript/JavaScript
    .field('destination')
        .desc('Where would you like to go?')
    .field('budget')
        .desc('What is your budget?')
    .build()
```

With Chatfield, your application can easily do:

- **Natural Conversation**: You tell Chatfield the user input. Chatfield tells you what to say in response.
- **LLM-Powered Validation**: Write rules in natural language describing valid or invalid field values.
- **LLM-powered Data Transformation**: "Cast" user input into any additional representation you want:
    - **Convert to data**: `"5k"` becomes `5000`. `"Yes"` becomes `true`. `"50/50"` becomes `0.5`
    - **Convert to object**: `"I am Sam age 20"` becomes `{"name":"Sam", "age":20}`
    - **Translate language**: `"Hello"` becomes `"Bonjour"`
    - **Classify** user input into categories you choose

Chatfield works in any framework. Internally, Chatfield is built on [LangGraph](https://www.langchain.com/langgraph) and [LangChain](https://www.langchain.com/), supporting all LLMs which LangChain supports.

## Quick Start

### Running the Travel Planner

Using the simple travel form defined above, here's how to run a conversation:

**Python:**
```python
from chatfield import chatfield, Interviewer

# Define the travel planner (from above)
trip = (chatfield()
    .field("destination")
        .desc("Where would you like to go?")
    .field("budget")
        .desc("What is your budget?")
    .build())

# Run the conversation
interviewer = Interviewer(trip)
user_input = None
while not trip._done:
    message = interviewer.go(user_input)
    print(message)
    user_input = input("> ")

# Access collected data
print(f"Destination: {trip.destination}")
print(f"Budget: {trip.budget}")
```

**TypeScript:**
```typescript
import { chatfield, Interviewer } from 'chatfield'

// Define the travel planner (from above)
const trip = chatfield()
  .field('destination')
    .desc('Where would you like to go?')
  .field('budget')
    .desc('What is your budget?')
  .build()

// Run the conversation
const interviewer = new Interviewer(trip)
let userInput: string | null = null
while (!trip._done) {
  const message = await interviewer.go(userInput)
  console.log(message)
  userInput = await getUserInput() // Your input method
}

// Access collected data
console.log(`Destination: ${trip.destination}`)
console.log(`Budget: ${trip.budget}`)
```

## Core Concepts

Chatfield transforms traditional form fields into conversational topics. The AI interviewer guides users through data collection naturally, validating responses and transforming them into structured data.

### Field Definition

Fields are the basic building blocks. Each field represents a piece of data to collect:

**Python:**
```python
trip = (chatfield()
    .field("destination")
        .desc("Where would you like to go?")
    .field("travel_style")
        .desc("What's your travel style?")
    .field("group_size")
        .desc("How many people are traveling?")
    .build())
```

**TypeScript:**
```typescript
const trip = chatfield()
  .field('destination')
    .desc('Where would you like to go?')
  .field('travelStyle')
    .desc('What\'s your travel style?')
  .field('groupSize')
    .desc('How many people are traveling?')
  .build()
```

### Interview Metadata

Provide context about your interview:

**Python:**
```python
vacation_planner = (chatfield()
    .type("Vacation Planning")
    .desc("Plan your perfect vacation")
    .field("destination")
        .desc("Where would you like to go?")
    .field("duration")
        .desc("How many days?")
    .field("interests")
        .desc("What are you interested in?")
    .build())
```

**TypeScript:**
```typescript
const vacationPlanner = chatfield()
  .type('Vacation Planning')
  .desc('Plan your perfect vacation')
  .field('destination')
    .desc('Where would you like to go?')
  .field('duration')
    .desc('How many days?')
  .field('interests')
    .desc('What are you interested in?')
  .build()
```

## Adding Validation

The basic travel planner above can be enhanced with validation rules:

**Python:**
```python
trip = (chatfield()
    .field("destination")
        .desc("Where would you like to go?")
        .must("be a real place")
        .reject("generic answers like 'anywhere'")
    .field("budget")
        .desc("What is your budget?")
        .must("include a specific amount")
        .hint("Per person or total is fine")
    .build())
```

**TypeScript:**
```typescript
const trip = chatfield()
  .field('destination')
    .desc('Where would you like to go?')
    .must('be a real place')
    .reject("generic answers like 'anywhere'")
  .field('budget')
    .desc('What is your budget?')
    .must('include a specific amount')
    .hint('Per person or total is fine')
  .build()
```

## Validation Rules

Ensure data quality with validation rules that guide the conversation:

### Must, Reject, and Hint

For more complex validation scenarios:

**Python:**
```python
advanced_trip = (chatfield()
    .field("dates")
        .desc("Travel dates")
        .must("be at least 7 days in the future")
        .must("not exceed 30 days duration")
        .reject("peak holiday periods if avoiding crowds")
        .hint("Consider shoulder season for better rates")

    .field("budget")
        .desc("Total trip budget")
        .must("be realistic for destination")
        .must("include all travelers")
        .reject("vague amounts like 'whatever it takes'")
        .hint("Include flights, hotels, food, and activities")

    .build())
```

**TypeScript:**
```typescript
const advancedTrip = chatfield()
  .field('dates')
    .desc('Travel dates')
    .must('be at least 7 days in the future')
    .must('not exceed 30 days duration')
    .reject('peak holiday periods if avoiding crowds')
    .hint('Consider shoulder season for better rates')

  .field('budget')
    .desc('Total trip budget')
    .must('be realistic for destination')
    .must('include all travelers')
    .reject("vague amounts like 'whatever it takes'")
    .hint('Include flights, hotels, food, and activities')

  .build()
```

## Type Transformations

The basic budget field can be enhanced to convert text into structured data:

**Python:**
```python
trip = (chatfield()
    .field("destination")
        .desc("Where would you like to go?")
    .field("budget")
        .desc("What is your budget?")
        .as_float()  # "2.5k" → 2500.0
    .build())
```

**TypeScript:**
```typescript
const trip = chatfield()
  .field('destination')
    .desc('Where would you like to go?')
  .field('budget')
    .desc('What is your budget?')
    .as_float()  // "2.5k" → 2500.0
  .build()
```

### Basic Transformations

More transformation examples:

**Python:**
```python
booking = (chatfield()
    .field("group_size")
        .desc("How many travelers?")
        .as_int()  # "family of four" → 4

    .field("trip_budget")
        .desc("Trip budget per person")
        .as_float()  # "2.5k" → 2500.0

    .field("all_inclusive")
        .desc("Want all-inclusive package?")
        .as_bool()  # "yes please" → True

    .field("destinations")
        .desc("Countries to visit")
        .as_list()  # "France, Italy, Greece" → ["France", "Italy", "Greece"]

    .field("flexibility")
        .desc("How flexible are your dates?")
        .as_percent()  # "very flexible" → 0.85

    .build())

# Access transformed values
travelers = booking.group_size.as_int       # integer
budget = booking.trip_budget.as_float       # float
inclusive = booking.all_inclusive.as_bool   # boolean
countries = booking.destinations.as_list    # list
flex = booking.flexibility.as_percent       # float
```

**TypeScript:**
```typescript
const booking = chatfield()
  .field('groupSize')
    .desc('How many travelers?')
    .as_int()  // "family of four" → 4

  .field('tripBudget')
    .desc('Trip budget per person')
    .as_float()  // "2.5k" → 2500.0

  .field('allInclusive')
    .desc('Want all-inclusive package?')
    .as_bool()  // "yes please" → true

  .field('destinations')
    .desc('Countries to visit')
    .as_list()  // "France, Italy, Greece" → ["France", "Italy", "Greece"]

  .field('flexibility')
    .desc('How flexible are your dates?')
    .as_percent()  // "very flexible" → 0.85

  .build()

// Access transformed values
const travelers = booking.groupSize.as_int      // number
const budget = booking.tripBudget.as_float      // number
const inclusive = booking.allInclusive.as_bool  // boolean
const countries = booking.destinations.as_list  // array
const flex = booking.flexibility.as_percent     // number
```

### Advanced Transformations

Multiple transformations on the same field:

**Python:**
```python
international_trip = (chatfield()
    .field("budget")
        .desc("Your travel budget")
        .as_float()
        .as_lang('es')  # Spanish translation
        .as_lang('jp')  # Japanese translation
        .as_bool('luxury', 'True if > 5000 per person')
        .as_str('formatted', 'With currency symbol like $5,000')
        .as_percent('of_annual', 'As percentage of $50k annual travel budget')

    .build())

# After user says "three thousand dollars":
budget = international_trip.budget                    # "3000"
budget_float = international_trip.budget.as_float     # 3000.0
budget_es = international_trip.budget.as_lang_es      # "tres mil dólares"
budget_jp = international_trip.budget.as_lang_jp      # "三千ドル"
is_luxury = international_trip.budget.as_bool_luxury  # False
formatted = international_trip.budget.as_str_formatted # "$3,000"
of_annual = international_trip.budget.as_percent_of_annual # 0.06
```

**TypeScript:**
```typescript
const internationalTrip = chatfield()
  .field('budget')
    .desc('Your travel budget')
    .as_float()
    .as_lang('es')  // Spanish translation
    .as_lang('jp')  // Japanese translation
    .as_bool('luxury', 'True if > 5000 per person')
    .as_str('formatted', 'With currency symbol like $5,000')
    .as_percent('ofAnnual', 'As percentage of $50k annual travel budget')

  .build()

// After user says "three thousand dollars":
const budget = internationalTrip.budget                     // "3000"
const budgetFloat = internationalTrip.budget.as_float       // 3000.0
const budgetEs = internationalTrip.budget.as_lang_es        // "tres mil dólares"
const budgetJp = internationalTrip.budget.as_lang_jp        // "三千ドル"
const isLuxury = internationalTrip.budget.as_bool_luxury    // false
const formatted = internationalTrip.budget.as_str_formatted // "$3,000"
const ofAnnual = internationalTrip.budget.as_percent_ofAnnual // 0.06
```

### Language Translations

**Python:**
```python
multilingual_booking = (chatfield()
    .field("special_request")
        .desc("Any special requests for your trip?")
        .as_lang('es')   # Spanish
        .as_lang('fr')   # French
        .as_lang('de')   # German
        .as_lang('ja')   # Japanese
        .as_lang('zh')   # Chinese
    .build())

# User: "I need a quiet room away from the elevator"
request_es = multilingual_booking.special_request.as_lang_es  # "Necesito una habitación tranquila lejos del ascensor"
request_fr = multilingual_booking.special_request.as_lang_fr  # "J'ai besoin d'une chambre calme loin de l'ascenseur"
request_de = multilingual_booking.special_request.as_lang_de  # "Ich brauche ein ruhiges Zimmer weit vom Aufzug"
request_ja = multilingual_booking.special_request.as_lang_ja  # "エレベーターから離れた静かな部屋が必要です"
request_zh = multilingual_booking.special_request.as_lang_zh  # "我需要一个远离电梯的安静房间"
```

**TypeScript:**
```typescript
const multilingualBooking = chatfield()
  .field('specialRequest')
    .desc('Any special requests for your trip?')
    .as_lang('es')   // Spanish
    .as_lang('fr')   // French
    .as_lang('de')   // German
    .as_lang('ja')   // Japanese
    .as_lang('zh')   // Chinese
  .build()

// User: "I need a quiet room away from the elevator"
const requestEs = multilingualBooking.specialRequest.as_lang_es  // "Necesito una habitación tranquila lejos del ascensor"
const requestFr = multilingualBooking.specialRequest.as_lang_fr  // "J'ai besoin d'une chambre calme loin de l'ascenseur"
const requestDe = multilingualBooking.specialRequest.as_lang_de  // "Ich brauche ein ruhiges Zimmer weit vom Aufzug"
const requestJa = multilingualBooking.specialRequest.as_lang_ja  // "エレベーターから離れた静かな部屋が必要です"
const requestZh = multilingualBooking.specialRequest.as_lang_zh  // "我需要一个远离电梯的安静房间"
```

### JSON and Dictionary Parsing

**Python:**
```python
api_form = (chatfield()
    .field("config")
        .desc("Paste your configuration")
        .as_dict()  # Parses JSON/dict

    .field("metadata")
        .desc("Additional metadata")
        .as_obj()  # Alternative name for dict

    .build())

# User: "timeout: 30, retries: 3, debug: true"
config = api_form.config.as_dict  # {'timeout': 30, 'retries': 3, 'debug': True}
```

**TypeScript:**
```typescript
const apiForm = chatfield()
  .field('config')
    .desc('Paste your configuration')
    .as_dict()  // Parses JSON/dict

  .field('metadata')
    .desc('Additional metadata')
    .as_obj()  // Alternative name for dict

  .build()

// User: "timeout: 30, retries: 3, debug: true"
const config = apiForm.config.as_dict  // {timeout: 30, retries: 3, debug: true}
```

### Set Operations

**Python:**
```python
analysis = (chatfield()
    .field("tags")
        .desc("Relevant tags")
        .as_set()  # Unique values only
        .as_set('keywords', 'Extract main keywords')
        .as_set('entities', 'Named entities')

    .build())

# User: "machine learning, AI, machine learning, neural networks"
tags = analysis.tags.as_set              # {'machine learning', 'AI', 'neural networks'}
keywords = analysis.tags.as_set_keywords # Custom set extraction
entities = analysis.tags.as_set_entities # Named entities from text
```

**TypeScript:**
```typescript
const analysis = chatfield()
  .field('tags')
    .desc('Relevant tags')
    .as_set()  // Unique values only
    .as_set('keywords', 'Extract main keywords')
    .as_set('entities', 'Named entities')

  .build()

// User: "machine learning, AI, machine learning, neural networks"
const tags = analysis.tags.as_set              // Set {'machine learning', 'AI', 'neural networks'}
const keywords = analysis.tags.as_set_keywords // Custom set extraction
const entities = analysis.tags.as_set_entities // Named entities from text
```

## Choice Cardinality

Control how many options can be selected from a list:

**Python:**
```python
preferences = (chatfield()
    # Exactly one choice required
    .field("department")
        .desc("Your department")
        .as_one('dept', 'Engineering', 'Sales', 'Marketing', 'Support')

    # Zero or one choice (optional)
    .field("mentor")
        .desc("Would you like a mentor?")
        .as_maybe('person', 'Alice', 'Bob', 'Charlie')

    # One or more choices (at least one required)
    .field("languages")
        .desc("Programming languages you know")
        .as_multi('langs', 'Python', 'JavaScript', 'Go', 'Rust', 'Java')

    # Zero or more choices (completely optional)
    .field("interests")
        .desc("Technical interests")
        .as_any('topics', 'ML', 'Web', 'Mobile', 'DevOps', 'Security')

    .build())

# After collection:
dept = preferences.department.as_one_dept        # "Engineering"
mentor = preferences.mentor.as_maybe_person      # "Alice" or None
langs = preferences.languages.as_multi_langs     # {"Python", "JavaScript"}
interests = preferences.interests.as_any_topics  # {"ML", "Security"} or set()
```

**TypeScript:**
```typescript
const preferences = chatfield()
  // Exactly one choice required
  .field('department')
    .desc('Your department')
    .as_one('dept', 'Engineering', 'Sales', 'Marketing', 'Support')

  // Zero or one choice (optional)
  .field('mentor')
    .desc('Would you like a mentor?')
    .as_maybe('person', 'Alice', 'Bob', 'Charlie')

  // One or more choices (at least one required)
  .field('languages')
    .desc('Programming languages you know')
    .as_multi('langs', 'Python', 'JavaScript', 'Go', 'Rust', 'Java')

  // Zero or more choices (completely optional)
  .field('interests')
    .desc('Technical interests')
    .as_any('topics', 'ML', 'Web', 'Mobile', 'DevOps', 'Security')

  .build()

// After collection:
const dept = preferences.department.as_one_dept        // "Engineering"
const mentor = preferences.mentor.as_maybe_person      // "Alice" or null
const langs = preferences.languages.as_multi_langs     // Set {"Python", "JavaScript"}
const interests = preferences.interests.as_any_topics  // Set {"ML", "Security"} or Set {}
```

## Persona Customization

Define conversational roles and traits to shape the interaction:

### Basic Personas

**Python:**
```python
tech_interview = (chatfield()
    .alice()  # Configure interviewer
        .type("Senior Technical Interviewer")
        .trait("Direct and technical")
        .trait("Focuses on architecture")

    .bob()  # Configure interviewee
        .type("Software Architect")
        .trait("10+ years experience")
        .trait("Prefers detailed discussions")

    .field("stack")
        .desc("Proposed technology stack")
        .must("specific technology choices")

    .field("scale")
        .desc("Expected scale requirements")
        .must("quantifiable metrics")

    .build())
```

**TypeScript:**
```typescript
const techInterview = chatfield()
  .alice()  // Configure interviewer
    .type('Senior Technical Interviewer')
    .trait('Direct and technical')
    .trait('Focuses on architecture')

  .bob()  // Configure interviewee
    .type('Software Architect')
    .trait('10+ years experience')
    .trait('Prefers detailed discussions')

  .field('stack')
    .desc('Proposed technology stack')
    .must('specific technology choices')

  .field('scale')
    .desc('Expected scale requirements')
    .must('quantifiable metrics')

  .build()
```

### Dynamic Traits

Traits that activate based on conversation content:

**Python:**
```python
adaptive_interview = (chatfield()
    .alice()
        .type("Career Counselor")

    .bob()
        .type("Professional")
        .trait.possible("junior", "less than 3 years experience")
        .trait.possible("senior", "10+ years or leadership")
        .trait.possible("career_changer", "switching industries")

    .field("background")
        .desc("Tell me about your background")
    .field("goals")
        .desc("What are your career goals?")

    .build())

# Traits activate automatically based on responses
```

**TypeScript:**
```typescript
const adaptiveInterview = chatfield()
  .alice()
    .type('Career Counselor')

  .bob()
    .type('Professional')
    .trait.possible('junior', 'less than 3 years experience')
    .trait.possible('senior', '10+ years or leadership')
    .trait.possible('careerChanger', 'switching industries')

  .field('background')
    .desc('Tell me about your background')
  .field('goals')
    .desc('What are your career goals?')

  .build()

// Traits activate automatically based on responses
```

## Special Field Types

### Confidential Fields

Track information silently without directly asking:

**Python:**
```python
interview = (chatfield()
    .field("experience")
        .desc("Years of experience")
        .as_int()

    .field("shows_leadership")
        .desc("Demonstrates leadership qualities")
        .confidential()  # Never mentioned, only tracked
        .as_bool()

    .field("mentions_mentoring")
        .desc("Mentions mentoring experience")
        .confidential()
        .as_bool()

    .build())

# After conversation:
print(f"Experience: {interview.experience.as_int} years")
print(f"Shows leadership: {interview.shows_leadership.as_bool}")
print(f"Mentions mentoring: {interview.mentions_mentoring.as_bool}")
```

**TypeScript:**
```typescript
const interview = chatfield()
  .field('experience')
    .desc('Years of experience')
    .as_int()

  .field('showsLeadership')
    .desc('Demonstrates leadership qualities')
    .confidential()  // Never mentioned, only tracked
    .as_bool()

  .field('mentionsMentoring')
    .desc('Mentions mentoring experience')
    .confidential()
    .as_bool()

  .build()

// After conversation:
console.log(`Experience: ${interview.experience.as_int} years`)
console.log(`Shows leadership: ${interview.showsLeadership.as_bool}`)
console.log(`Mentions mentoring: ${interview.mentionsMentoring.as_bool}`)
```

### Conclude Fields

Evaluated only after all other fields are collected:

**Python:**
```python
assessment = (chatfield()
    .field("technical_skills")
        .desc("Technical competencies")

    .field("project_experience")
        .desc("Project background")

    .field("communication_quality")
        .desc("Communication effectiveness throughout conversation")
        .conclude()  # Evaluated at end
        .as_percent()

    .field("overall_fit")
        .desc("Overall fit for the role")
        .conclude()
        .as_one('rating', 'poor', 'fair', 'good', 'excellent')

    .build())

# Conclude fields are filled after conversation ends
```

**TypeScript:**
```typescript
const assessment = chatfield()
  .field('technicalSkills')
    .desc('Technical competencies')

  .field('projectExperience')
    .desc('Project background')

  .field('communicationQuality')
    .desc('Communication effectiveness throughout conversation')
    .conclude()  // Evaluated at end
    .as_percent()

  .field('overallFit')
    .desc('Overall fit for the role')
    .conclude()
    .as_one('rating', 'poor', 'fair', 'good', 'excellent')

  .build()

// Conclude fields are filled after conversation ends
```

## Context and Quote Capture

Preserve conversational context and exact user quotes:

**Python:**
```python
support_ticket = (chatfield()
    .field("issue")
        .desc("What problem are you experiencing?")
        .as_quote()    # Capture exact words
        .as_context()  # Capture conversation context

    .field("impact")
        .desc("How is this affecting your work?")
        .as_quote()

    .build())

# After collection:
issue = support_ticket.issue                # "Cannot access dashboard"
issue_quote = support_ticket.issue.as_quote # "I can't get into my dashboard, it spins forever"
issue_context = support_ticket.issue.as_context # "User mentioned recent password change"

impact = support_ticket.impact              # "Critical - blocking all work"
impact_quote = support_ticket.impact.as_quote # "We literally can't do anything!"
```

**TypeScript:**
```typescript
const supportTicket = chatfield()
  .field('issue')
    .desc('What problem are you experiencing?')
    .as_quote()    // Capture exact words
    .as_context()  // Capture conversation context

  .field('impact')
    .desc('How is this affecting your work?')
    .as_quote()

  .build()

// After collection:
const issue = supportTicket.issue                // "Cannot access dashboard"
const issueQuote = supportTicket.issue.as_quote  // "I can't get into my dashboard, it spins forever"
const issueContext = supportTicket.issue.as_context // "User mentioned recent password change"

const impact = supportTicket.impact              // "Critical - blocking all work"
const impactQuote = supportTicket.impact.as_quote // "We literally can't do anything!"
```

## Complete Examples

### Job Application System

**Python:**
```python
from chatfield import chatfield, Interviewer

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
        .trait.possible("startup_experience", "mentions startups")
        .trait.possible("enterprise_experience", "mentions large companies")

    # Basic information
    .field("name")
        .desc("Your full name")
        .must("include first and last name")

    .field("email")
        .desc("Email address")
        .must("be a valid email")

    # Experience with transformations
    .field("years_experience")
        .desc("Years of professional experience")
        .as_int()
        .must("be realistic (0-50 years)")
        .as_bool('senior', 'True if >= 5 years')
        .as_bool('lead', 'True if >= 8 years')

    # Skills selection
    .field("primary_languages")
        .desc("Primary programming languages")
        .as_multi('langs', 'Python', 'JavaScript', 'Go', 'Java', 'C++', 'Rust')
        .must("select at least one")

    .field("frameworks")
        .desc("Frameworks you're proficient with")
        .as_any('tools', 'React', 'Django', 'Flask', 'FastAPI', 'Node.js', 'Spring')

    # Salary with formatting
    .field("salary_expectation")
        .desc("Salary expectations")
        .hint("You can give a range")
        .as_int()
        .as_str('formatted', 'Formatted as $XXX,XXX')

    # Work preferences
    .field("work_location")
        .desc("Preferred work arrangement")
        .as_one('preference', 'Remote', 'Hybrid', 'Office')

    # Confidential assessments
    .field("values_concern")
        .desc("Candidate mentions something raising a values concern")
        .confidential()
        .as_bool()

    # Evaluate the entire conversation to conclude the communication style
    .field('communication_score')
        .desc('Clarity, focus, active listening during the conversation')
        .conclude()
        .as_percent()

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

# Access results
print(f"Name: {job_application.name}")
print(f"Years: {job_application.years_experience.as_int}")
print(f"Is Senior: {job_application.years_experience.as_bool_senior}")
print(f"Languages: {job_application.primary_languages.as_multi_langs}")
print(f"Salary: {job_application.salary_expectation.as_str_formatted}")
print(f"Communication: {job_application.communication_quality.as_one_level}")
print(f"Values concern: {job_application.values_concern.as_bool}")
```

**TypeScript:**
```typescript
import { chatfield, Interviewer } from '@chatfield/core'

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
    .trait.possible('startupExperience', 'mentions startups')
    .trait.possible('enterpriseExperience', 'mentions large companies')

  // Basic information
  .field('name')
    .desc('Your full name')
    .must('include first and last name')

  .field('email')
    .desc('Email address')
    .must('be a valid email')

  // Experience with transformations
  .field('yearsExperience')
    .desc('Years of professional experience')
    .as_int()
    .must('be realistic (0-50 years)')
    .as_bool('senior', 'True if >= 5 years')
    .as_bool('lead', 'True if >= 8 years')

  // Skills selection
  .field('primaryLanguages')
    .desc('Primary programming languages')
    .as_multi('langs', 'Python', 'JavaScript', 'Go', 'Java', 'C++', 'Rust')
    .must('select at least one')

  .field('frameworks')
    .desc("Frameworks you're proficient with")
    .as_any('tools', 'React', 'Django', 'Flask', 'FastAPI', 'Node.js', 'Spring')

  // Salary with formatting
  .field('salaryExpectation')
    .desc('Salary expectations')
    .hint('You can give a range')
    .as_int()
    .as_str('formatted', 'Formatted as $XXX,XXX')

  // Work preferences
  .field('workLocation')
    .desc('Preferred work arrangement')
    .as_one('preference', 'Remote', 'Hybrid', 'Office')

  // Confidential assessments
  .field('communicationQuality')
    .desc('Communication clarity during interview')
    .confidential()
    .as_one('level', 'poor', 'adequate', 'good', 'excellent')

  // Confidential assessments
  .field("valuesConcern")
    .desc("Candidate mentions something raising a values concern")
    .confidential()
    .as_bool()

  // Evaluate the entire conversation to conclude the communication style
  .field('communicationScore')
    .desc('Clarity, focus, active listening during the conversation')
    .conclude()
    .as_percent()

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
    userInput = await getUserInput()
  }
}

// Access results
console.log(`Name: ${jobApplication.name}`)
console.log(`Years: ${jobApplication.yearsExperience.as_int}`)
console.log(`Is Senior: ${jobApplication.yearsExperience.as_bool_senior}`)
console.log(`Languages: ${jobApplication.primaryLanguages.as_multi_langs}`)
console.log(`Salary: ${jobApplication.salaryExpectation.as_str_formatted}`)
console.log(`Communication: ${jobApplication.communicationQuality.as_one_level}`)
console.log(`Values concern: ${jobApplication.valuesConcern.as_bool}`)
```

### Product Launch Planning

**Python:**
```python
product_launch = (chatfield()
    .type("Product Launch")
    .desc("Product launch planning")

    .alice()
        .type("Product Manager")
        .trait("Focuses on user value")

    .bob()
        .type("Startup Founder")
        .trait("First-time founder")

    .field("product")
        .desc("Product description and target market")
        .must("clear value proposition")
        .must("target audience defined")
        .reject("everything for everyone")
        .hint("Who specifically will pay?")

    .field("first_year_users")
        .desc("First year user target")
        .as_int()
        .as_lang('ja')
        .must("realistic for MVP")
        .must("between 1000 and 100000")

    .field("market_share")
        .desc("Expected market share")
        .as_percent()
        .hint("Most startups capture <5% initially")

    .field("competitors")
        .desc("Direct competitors")
        .as_list()
        .must("at least 3 competitors")

    .field("unique_value")
        .desc("Unique value proposition")
        .as_dict()
        .hint("Format: feature, value, differentiator")

    .field("model")
        .desc("Business model")
        .as_one('selection', 'B2B', 'B2C', 'B2B2C', 'marketplace')

    .field("channels")
        .desc("Marketing channels")
        .as_multi('selection', 'organic', 'paid_ads', 'content', 'partnerships', 'social')
        .must("at least 2 channels")
        .must("no more than 3 to start")

    .field("ready")
        .desc("Ready to launch?")
        .as_bool()
        .as_bool('funded', 'True if you have funding')
        .as_bool('technical', 'True if you have technical co-founder')

    .field("enthusiasm")
        .desc("Level of founder enthusiasm")
        .confidential()
        .as_percent()

    .field("viability")
        .desc("Overall business viability")
        .conclude()
        .as_percent()

    .build())
```

**TypeScript:**
```typescript
const productLaunch = chatfield()
  .type('Product Launch')
  .desc('Product launch planning')

  .alice()
    .type('Product Manager')
    .trait('Focuses on user value')

  .bob()
    .type('Startup Founder')
    .trait('First-time founder')

  .field('product')
    .desc('Product description and target market')
    .must('clear value proposition')
    .must('target audience defined')
    .reject('everything for everyone')
    .hint('Who specifically will pay?')

  .field('firstYearUsers')
    .desc('First year user target')
    .as_int()
    .as_lang('ja')
    .must('realistic for MVP')
    .must('between 1000 and 100000')

  .field('marketShare')
    .desc('Expected market share')
    .as_percent()
    .hint('Most startups capture <5% initially')

  .field('competitors')
    .desc('Direct competitors')
    .as_list()
    .must('at least 3 competitors')

  .field('uniqueValue')
    .desc('Unique value proposition')
    .as_dict()
    .hint('Format: feature, value, differentiator')

  .field('model')
    .desc('Business model')
    .as_one('selection', 'B2B', 'B2C', 'B2B2C', 'marketplace')

  .field('channels')
    .desc('Marketing channels')
    .as_multi('selection', 'organic', 'paid_ads', 'content', 'partnerships', 'social')
    .must('at least 2 channels')
    .must('no more than 3 to start')

  .field('ready')
    .desc('Ready to launch?')
    .as_bool()
    .as_bool('funded', 'True if you have funding')
    .as_bool('technical', 'True if you have technical co-founder')

  .field('enthusiasm')
    .desc('Level of founder enthusiasm')
    .confidential()
    .as_percent()

  .field('viability')
    .desc('Overall business viability')
    .conclude()
    .as_percent()

  .build()
```

## API Reference

### Builder Methods

#### Core Builder
- `chatfield()` - Start building a new interview
- `.type(name)` - Set the interview type name
- `.desc(description)` - Set the interview description
- `.build()` - Build the final Interview object

#### Role Configuration
- `.alice()` - Configure the interviewer role
- `.bob()` - Configure the interviewee role
- `.type(role_type)` - Set role type (after .alice() or .bob())
- `.trait(trait)` - Add a trait
- `.trait.possible(name, trigger)` - Add a conditional trait

#### Field Definition
- `.field(name)` - Start defining a field
- `.desc(description)` - Set field description
- `.must(rule)` - Add a requirement
- `.reject(rule)` - Add a rejection rule
- `.hint(tip)` - Add helpful guidance
- `.confidential()` - Mark as silently tracked
- `.conclude()` - Evaluate only at end

#### Type Transformations
- `.as_int()` - Parse as integer
- `.as_float()` - Parse as float
- `.as_bool()` - Parse as boolean
- `.as_str()` - String format
- `.as_percent()` - Parse as 0.0-1.0
- `.as_list()` - Parse as list
- `.as_set()` - Parse as unique set
- `.as_dict()` / `.as_obj()` - Parse as dictionary/object
- `.as_lang(code)` - Translate to language
- `.as_quote()` - Capture exact user quote
- `.as_context()` - Capture conversation context

#### Custom Transformations
- `.as_bool(predicate, description)` - Custom boolean check
- `.as_int(transform, description)` - Custom integer transform
- `.as_str(format, description)` - Custom string format
- `.as_set(operation, description)` - Set operation

#### Choice Cardinality
- `.as_one(name, ...choices)` - Exactly one choice required
- `.as_maybe(name, ...choices)` - Zero or one choice
- `.as_multi(name, ...choices)` - One or more choices required
- `.as_any(name, ...choices)` - Zero or more choices

### Core Classes

#### Interview
Base class for conversational data collection:
- `._done` - Check if all fields are collected
- `.field_name` - Access field value (returns FieldProxy)
- `._chatfield` - Internal structure containing all metadata

#### Interviewer
Manages conversation flow:
- `constructor(interview, options)` - Create interviewer instance
- `.go(user_input)` - Process one conversation turn
- Returns AI message as string (Python) or Promise<string> (TypeScript)

#### FieldProxy
String-like class providing transformation access:
- Base value when accessed directly
- `.as_*` attributes for transformations
- All string methods available

## Environment Configuration

Set your OpenAI API key:

```bash
# Environment variable
export OPENAI_API_KEY=your-api-key

# Or .env file
echo "OPENAI_API_KEY=your-api-key" > .env
```

Pass API key directly:

**Python:**
```python
interviewer = Interviewer(interview, api_key="your-api-key")
```

**TypeScript:**
```typescript
const interviewer = new Interviewer(interview, { apiKey: "your-api-key" })
```

## Project Structure

```
Chatfield/
├── Python/                      # Python implementation
│   ├── chatfield/              # Core package
│   ├── tests/                  # Test suite
│   └── examples/               # Example scripts
├── TypeScript/                 # TypeScript implementation
│   ├── src/                    # Source code
│   ├── tests/                  # Test suite
│   └── examples/               # Example scripts
└── Documentation/              # Additional documentation
```

See language-specific READMEs for development setup:
- [Python Development](./Python/README.md)
- [TypeScript Development](./TypeScript/README.md)

## License

Apache License 2.0 - See [LICENSE](./LICENSE) for details.