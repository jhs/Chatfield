# Chatfield Cookbook

A comprehensive guide to using Chatfield for conversational data collection, progressing from simple to advanced techniques. Each recipe includes examples for both Python and TypeScript implementations.

> **Quick Start:** For a quick overview with essential examples, see the [main README](../README.md). This cookbook provides detailed recipes for specific use cases and patterns.

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Basic Recipes](#2-basic-recipes)
3. [Validation Recipes](#3-validation-recipes)
4. [Transformation Recipes](#4-transformation-recipes)
5. [Role & Personality Recipes](#5-role--personality-recipes)
6. [Advanced Field Recipes](#6-advanced-field-recipes)
7. [Complex Conversation Recipes](#7-complex-conversation-recipes)
8. [Testing Recipes](#8-testing-recipes)
9. [Integration Recipes](#9-integration-recipes)
10. [Production Recipes](#10-production-recipes)
11. [Debugging & Troubleshooting](#11-debugging--troubleshooting)

---

## 1. Getting Started

### 1.1 Installation and Setup

**Python:**
```bash
cd Python
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

**TypeScript:**
```bash
cd TypeScript
npm install
npm run build
```

### 1.2 Environment Configuration

Create a `.env.secret` file in the project root:

```bash
OPENAI_API_KEY=your-api-key-here
LANGCHAIN_TRACING_V2=true  # Optional: Enable LangSmith tracing
```

Or export directly:
```bash
export OPENAI_API_KEY=your-api-key
```

### 1.3 Hello World - Travel Planner

The quintessential first example - a simple travel planner:

**Python:**
```python
from chatfield import chatfield, Interviewer

# Define the travel planner
trip = chatfield()\
    .field("destination")\
        .desc("Where would you like to go?")\
    .field("budget")\
        .desc("What is your budget?")\
    .build()

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

// Define the travel planner
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

---

## 2. Basic Recipes

### 2.1 Collecting Multiple Fields

**Python:**
```python
from chatfield import chatfield

interview = (chatfield()
    .type("ContactForm")
    .desc("Collecting contact information")
    .field("name")
    .desc("Your full name")
    .field("email")
    .desc("Your email address")
    .field("phone")
    .desc("Your phone number")
    .build())
```

**TypeScript:**
```typescript
const interview = chatfield()
  .type('ContactForm')
  .desc('Collecting contact information')
  .field('name')
    .desc('Your full name')
  .field('email')
    .desc('Your email address')
  .field('phone')
    .desc('Your phone number')
  .build()
```

### 2.2 Using Field Descriptions

Field descriptions guide the AI on what to ask for:

**Python:**
```python
interview = (chatfield()
    .field("favorite_color")
        .desc("Ask about their favorite color and why they like it")
    .field("mood")
        .desc("Current emotional state")
    .build())
```

**TypeScript:**
```typescript
const interview = chatfield()
  .field('favoriteColor')
    .desc('Ask about their favorite color and why they like it')
  .field('mood')
    .desc('Current emotional state')
  .build()
```

### 2.3 Automated Demo Mode

For testing or demonstrations without user interaction:

**Python:**
```python
def run_automated(interview):
    prefab_inputs = [
        "My name is Alice",
        "alice@example.com",
        "555-1234"
    ]

    interviewer = Interviewer(interview)
    input_iter = iter(prefab_inputs)
    user_input = None

    while not interview._done:
        message = interviewer.go(user_input)
        if message:
            print(f"AI: {message}")
        if not interview._done:
            user_input = next(input_iter)
            print(f"User: {user_input}")
```

**TypeScript:**
```typescript
async function runAutomated(interview: Interview) {
  const prefabInputs = [
    'My name is Alice',
    'alice@example.com',
    '555-1234'
  ]

  const interviewer = new Interviewer(interview)
  const inputIter = prefabInputs[Symbol.iterator]()
  let userInput: string | undefined = undefined

  while (!interview._done) {
    const message = await interviewer.go(userInput)
    if (message) {
      console.log(`AI: ${message}`)
    }
    if (!interview._done) {
      const next = inputIter.next()
      userInput = next.value
      console.log(`User: ${userInput}`)
    }
  }
}
```

---

## 3. Validation Recipes

### 3.1 Basic Must/Reject Rules

**Python:**
```python
interview = (chatfield()
    .field("email")
    .desc("Your email address")
        .must("be a valid email format")
        .must("use a professional domain")
        .reject("gmail, yahoo, or other free email providers")
    .build())
```

**TypeScript:**
```typescript
const interview = chatfield()
  .field('email')
    .desc('Your email address')
    .must('be a valid email format')
    .must('use a professional domain')
    .reject('gmail, yahoo, or other free email providers')
  .build()
```

### 3.2 Using Hints

Hints provide guidance without being strict requirements:

**Python:**
```python
interview = (chatfield()
    .field("company_name")
    .desc("Your company name")
        .must("be specific and complete")
        .hint("Include Inc, LLC, or other legal entity type")
        .hint("Use proper capitalization")
    .build())
```

**TypeScript:**
```typescript
const interview = chatfield()
  .field('companyName')
    .desc('Your company name')
    .must('be specific and complete')
    .hint('Include Inc, LLC, or other legal entity type')
    .hint('Use proper capitalization')
  .build()
```

### 3.3 Complex Validation Rules

**Python:**
```python
interview = (chatfield()
    .field("password")
    .desc("Create a secure password")
        .must("be at least 12 characters long")
        .must("contain uppercase, lowercase, numbers, and symbols")
        .reject("common passwords like 'password123'")
        .reject("personal information like names or birthdays")
        .hint("Use a passphrase with random words")
    .build())
```

**TypeScript:**
```typescript
const interview = chatfield()
  .field('password')
    .desc('Create a secure password')
    .must('be at least 12 characters long')
    .must('contain uppercase, lowercase, numbers, and symbols')
    .reject('common passwords like "password123"')
    .reject('personal information like names or birthdays')
    .hint('Use a passphrase with random words')
  .build()
```

### 3.4 Validation for Specific Formats

**Python:**
```python
interview = (chatfield()
    .field("phone")
    .desc("Your phone number")
        .must("be a valid US phone number")
        .must("include area code")
        .reject("international numbers")
    .field("zip_code")
    .desc("Your ZIP code")
        .must("be a 5-digit US ZIP code")
        .reject("ZIP+4 format")
    .build())
```

**TypeScript:**
```typescript
const interview = chatfield()
  .field('phone')
    .desc('Your phone number')
    .must('be a valid US phone number')
    .must('include area code')
    .reject('international numbers')
  .field('zipCode')
    .desc('Your ZIP code')
    .must('be a 5-digit US ZIP code')
    .reject('ZIP+4 format')
  .build()
```

---

## 4. Transformation Recipes

### 4.0 Understanding Transformations

Chatfield's transformations are computed by the LLM during data collection, not as post-processing. When you define `.as_int()` on a field, the LLM automatically converts natural language like "family of four" into `4` or "2.5k" into `2500`.

### 4.1 Basic Type Transformations

A comprehensive example showing all basic transformation types:

**Python:**
```python
booking = chatfield()\
    .field("group_size")\
        .desc("How many travelers?")\
        .as_int()  # "family of four" → 4\
    .field("trip_budget")\
        .desc("Trip budget per person")\
        .as_float()  # "2.5k" → 2500.0\
    .field("all_inclusive")\
        .desc("Want all-inclusive package?")\
        .as_bool()  # "yes please" → True\
    .field("destinations")\
        .desc("Countries to visit")\
        .as_list()  # "France, Italy, Greece" → ["France", "Italy", "Greece"]\
    .field("flexibility")\
        .desc("How flexible are your dates?")\
        .as_percent()  # "very flexible" → 0.85\
    .build()

# Access transformed values
travelers = booking.group_size.as_int       # integer
budget = booking.trip_budget.as_float       # float
inclusive = booking.all_inclusive.as_bool   # boolean
countries = booking.destinations.as_list    # list
flex = booking.flexibility.as_percent       # float (0.0-1.0)
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
const flex = booking.flexibility.as_percent     // number (0.0-1.0)
```

### 4.2 Language Transformations

Translate responses to different languages:

**Python:**
```python
interview = (chatfield()
    .field("greeting")
    .desc("Say hello")
        .as_lang('fr', "French translation")
        .as_lang('es', "Spanish translation")
        .as_lang('de', "German translation")
        .as_lang('ja', "Japanese translation")
    .build())

# After collection
print(interview.greeting.as_lang_fr)  # "Bonjour"
print(interview.greeting.as_lang_es)  # "Hola"
print(interview.greeting.as_lang_de)  # "Hallo"
print(interview.greeting.as_lang_ja)  # "こんにちは"
```

**TypeScript:**
```typescript
const interview = chatfield()
  .field('greeting')
    .desc('Say hello')
    .as_lang('fr', 'French translation')
    .as_lang('es', 'Spanish translation')
    .as_lang('de', 'German translation')
    .as_lang('ja', 'Japanese translation')
  .build()

// After collection
console.log(interview.greeting.as_lang_fr)  // "Bonjour"
console.log(interview.greeting.as_lang_es)  // "Hola"
console.log(interview.greeting.as_lang_de)  // "Hallo"
console.log(interview.greeting.as_lang_ja)  // "こんにちは"
```

### 4.3 Boolean Sub-Attributes

**Python:**
```python
interview = (chatfield()
    .field("number")
    .desc("Pick a number")
        .as_int()
        .as_bool('even', "True if even, False if odd")
        .as_bool('prime', "True if prime number")
        .as_bool('perfect_square', "True if perfect square")
    .build())

# After collection
if interview.number.as_bool_even:
    print("Even number!")
if interview.number.as_bool_prime:
    print("Prime number!")
```

**TypeScript:**
```typescript
const interview = chatfield()
  .field('number')
    .desc('Pick a number')
    .as_int()
    .as_bool('even', 'True if even, False if odd')
    .as_bool('prime', 'True if prime number')
    .as_bool('perfect_square', 'True if perfect square')
  .build()

// After collection
if (interview.number.as_bool_even) {
  console.log('Even number!')
}
if (interview.number.as_bool_prime) {
  console.log('Prime number!')
}
```

### 4.4 Percentage Transformations

Convert to 0.0-1.0 range:

**Python:**
```python
interview = (chatfield()
    .field("satisfaction")
    .desc("Rate your satisfaction from 0-100")
        .as_int()
        .as_percent("Normalized to 0.0-1.0")
    .build())

# After collection
satisfaction_pct = interview.satisfaction.as_percent  # 0.85 for "85"
```

**TypeScript:**
```typescript
const interview = chatfield()
  .field('satisfaction')
    .desc('Rate your satisfaction from 0-100')
    .as_int()
    .as_percent('Normalized to 0.0-1.0')
  .build()

// After collection
const satisfactionPct = interview.satisfaction.as_percent  // 0.85 for "85"
```

### 4.5 Set and List Transformations

**Python:**
```python
interview = (chatfield()
    .field("skills")
    .desc("List your programming skills")
        .as_list("Array of individual skills")
        .as_set("factors", "Unique skill categories")
    .build())

# After collection
skills_list = interview.skills.as_list  # ["Python", "JavaScript", "Go"]
skills_set = interview.skills.as_set_factors  # {"Backend", "Frontend"}
```

**TypeScript:**
```typescript
const interview = chatfield()
  .field('skills')
    .desc('List your programming skills')
    .as_list('Array of individual skills')
    .as_set('factors', 'Unique skill categories')
  .build()

// After collection
const skillsList = interview.skills.as_list  // ["Python", "JavaScript", "Go"]
const skillsSet = interview.skills.as_set_factors  // Set {"Backend", "Frontend"}
```

### 4.6 String Transformations

**Python:**
```python
interview = (chatfield()
    .field("number")
    .desc("Your favorite number")
        .as_int()
        .as_str('longhand', "Written out in English words")
    .build())

# After collection
print(interview.number.as_str_longhand)  # "forty-two" for 42
```

**TypeScript:**
```typescript
const interview = chatfield()
  .field('number')
    .desc('Your favorite number')
    .as_int()
    .as_str('longhand', 'Written out in English words')
  .build()

// After collection
console.log(interview.number.as_str_longhand)  // "forty-two" for 42
```

### 4.7 Context and Quote Capture

Preserve conversational context and exact user quotes for detailed records:

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

### 4.8 Dictionary and JSON Parsing

**Python:**
```python
api_form = chatfield()\
    .field("config")\
        .desc("Paste your configuration")\
        .as_dict()  # Parses JSON/dict\
    .field("metadata")\
        .desc("Additional metadata")\
        .as_obj()  # Alternative name for dict\
    .build()

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

---

## 5. Role & Personality Recipes

### 5.1 Defining Alice (Interviewer) and Bob (User)

**Python:**
```python
interview = (chatfield()
    .alice()
        .type("Professional Recruiter")
        .trait("Friendly and encouraging")
        .trait("Asks follow-up questions")
    .bob()
        .type("Job Candidate")
        .trait("Nervous but prepared")
    .field("experience")
    .desc("Tell me about your work experience")
    .build())
```

**TypeScript:**
```typescript
const interview = chatfield()
  .alice()
    .type('Professional Recruiter')
    .trait('Friendly and encouraging')
    .trait('Asks follow-up questions')
  .bob()
    .type('Job Candidate')
    .trait('Nervous but prepared')
  .field('experience')
    .desc('Tell me about your work experience')
  .build()
```

### 5.2 Fun Personalities

**Python:**
```python
interview = (chatfield()
    .alice()
        .type("Server")
        .trait("Speaks in limericks")
        .trait("Enthusiastic about food")
    .bob()
        .type("Hungry Diner")
    .field("order")
    .desc("What would you like to eat?")
    .build())
```

**TypeScript:**
```typescript
const interview = chatfield()
  .alice()
    .type('Server')
    .trait('Speaks in limericks')
    .trait('Enthusiastic about food')
  .bob()
    .type('Hungry Diner')
  .field('order')
    .desc('What would you like to eat?')
  .build()
```

### 5.3 Specialized Domain Experts

**Python:**
```python
interview = (chatfield()
    .alice()
        .type("Expert Technology Consultant")
        .trait("Technology partner for the Product Owner")
        .trait("Understands business and technical requirements")
        .trait("Keeps things simple without overwhelming")
    .bob()
        .type("Product Owner")
        .trait("Not deeply technical, but has clear vision")
    .field("project_scope")
    .desc("What would you like to build?")
        .must("specific enough to implement")
        .reject("anything requiring HIPAA or SOC2 compliance")
    .build())
```

**TypeScript:**
```typescript
const interview = chatfield()
  .alice()
    .type('Expert Technology Consultant')
    .trait('Technology partner for the Product Owner')
    .trait('Understands business and technical requirements')
    .trait('Keeps things simple without overwhelming')
  .bob()
    .type('Product Owner')
    .trait('Not deeply technical, but has clear vision')
  .field('projectScope')
    .desc('What would you like to build?')
    .must('specific enough to implement')
    .reject('anything requiring HIPAA or SOC2 compliance')
  .build()
```

---

## 6. Advanced Field Recipes

### 6.1 Cardinality - Choice Selection

**as_one** - Choose exactly one:

**Python:**
```python
interview = (chatfield()
    .field("main_course")
    .desc("Choose your main course")
        .as_one("selection",
                "Grilled Salmon",
                "Veggie Pasta",
                "Beef Tenderloin",
                "Chicken Parmesan")
    .build())
```

**TypeScript:**
```typescript
const interview = chatfield()
  .field('mainCourse')
    .desc('Choose your main course')
    .as_one('selection',
            'Grilled Salmon',
            'Veggie Pasta',
            'Beef Tenderloin',
            'Chicken Parmesan')
  .build()
```

**as_maybe** - Choose zero or one:

**Python:**
```python
interview = (chatfield()
    .field("number")
    .desc("Your favorite number")
        .as_maybe('special_property',
                  "fibonacci",
                  "perfect number",
                  "triangular number")
    .build())
```

**TypeScript:**
```typescript
const interview = chatfield()
  .field('number')
    .desc('Your favorite number')
    .as_maybe('special_property',
              'fibonacci',
              'perfect number',
              'triangular number')
  .build()
```

**as_multi** - Choose one or more:

**Python:**
```python
interview = (chatfield()
    .field("number")
    .desc("Your favorite number")
        .as_multi('math_properties',
                  "even", "odd", "prime",
                  "composite", "square", "cubic")
    .build())
```

**TypeScript:**
```typescript
const interview = chatfield()
  .field('number')
    .desc('Your favorite number')
    .as_multi('math_properties',
              'even', 'odd', 'prime',
              'composite', 'square', 'cubic')
  .build()
```

**as_any** - Choose zero or more:

**Python:**
```python
interview = (chatfield()
    .field("number")
    .desc("Your favorite number")
        .as_any('cultural_significance',
                "lucky", "unlucky", "sacred", "mystical")
    .build())
```

**TypeScript:**
```typescript
const interview = chatfield()
  .field('number')
    .desc('Your favorite number')
    .as_any('cultural_significance',
            'lucky', 'unlucky', 'sacred', 'mystical')
  .build()
```

### 6.2 Confidential Fields

Fields tracked internally but never mentioned in conversation:

**Python:**
```python
interview = (chatfield()
    .field("experience")
    .desc("Tell me about your experience")
    .field("has_mentored")
    .desc("Shows evidence of mentoring others")
        .confidential()
        .as_bool()
    .field("shows_leadership")
    .desc("Demonstrates leadership")
        .confidential()
        .as_bool()
    .build())

# After collection
if interview.has_mentored.as_bool:
    print("Candidate has mentoring experience")
```

**TypeScript:**
```typescript
const interview = chatfield()
  .field('experience')
    .desc('Tell me about your experience')
  .field('hasMentored')
    .desc('Shows evidence of mentoring others')
    .confidential()
    .as_bool()
  .field('showsLeadership')
    .desc('Demonstrates leadership')
    .confidential()
    .as_bool()
  .build()

// After collection
if (interview.hasMentored.as_bool) {
  console.log('Candidate has mentoring experience')
}
```

### 6.3 Conclusion Fields

Fields assessed at the end of the conversation:

**Python:**
```python
interview = (chatfield()
    .field("experience")
    .desc("Your work experience")
    .field("skills")
    .desc("Your technical skills")
    .field("preparedness")
    .desc("Overall preparation level")
        .conclude()
        .as_one.assessment("unprepared",
                          "somewhat prepared",
                          "well prepared",
                          "exceptionally prepared")
    .build())
```

**TypeScript:**
```typescript
const interview = chatfield()
  .field('experience')
    .desc('Your work experience')
  .field('skills')
    .desc('Your technical skills')
  .field('preparedness')
    .desc('Overall preparation level')
    .conclude()
    .as_one.assessment('unprepared',
                      'somewhat prepared',
                      'well prepared',
                      'exceptionally prepared')
  .build()
```

### 6.4 Combining Transformations

**Python:**
```python
interview = (chatfield()
    .field("age")
    .desc("Your age")
        .must("be between 18 and 120")
        .as_int()
        .as_float("Age as decimal")
        .as_lang('fr', "French")
        .as_lang('es', "Spanish")
        .as_bool('senior', "True if 65 or older")
        .as_str('decade', "Which decade (20s, 30s, etc)")
    .build())

# After collection - all transformations available
print(interview.age)              # "42" (string)
print(interview.age.as_int)       # 42
print(interview.age.as_float)     # 42.0
print(interview.age.as_lang_fr)   # "quarante-deux"
print(interview.age.as_bool_senior) # False
print(interview.age.as_str_decade)  # "40s"
```

**TypeScript:**
```typescript
const interview = chatfield()
  .field('age')
    .desc('Your age')
    .must('be between 18 and 120')
    .as_int()
    .as_float('Age as decimal')
    .as_lang('fr', 'French')
    .as_lang('es', 'Spanish')
    .as_bool('senior', 'True if 65 or older')
    .as_str('decade', 'Which decade (20s, 30s, etc)')
  .build()

// After collection - all transformations available
console.log(interview.age)              // "42" (string)
console.log(interview.age.as_int)       // 42
console.log(interview.age.as_float)     // 42.0
console.log(interview.age.as_lang_fr)   // "quarante-deux"
console.log(interview.age.as_bool_senior) // false
console.log(interview.age.as_str_decade)  // "40s"
```

---

## 7. Complex Conversation Recipes

### 7.1 Multi-Step Data Collection

**Python:**
```python
interview = (chatfield()
    .type("TechWorkRequest")
    .desc("Gathering project requirements")
    .alice()
        .type("Expert Technology Consultant")
    .bob()
        .type("Product Owner")
    .field("project_name")
    .desc("Project name")
        .hint("Short and memorable")
    .field("scope")
    .desc("What to build")
        .must("specific enough to implement")
        .reject("anything requiring HIPAA compliance")
    .field("target_users")
    .desc("Who will use this")
        .must("specific user groups or roles")
    .field("timeline")
    .desc("Completion deadline")
        .must("specific timeframe or deadline")
        .reject("ASAP without specific dates")
    .field("budget")
    .desc("Project budget")
        .must("specific amount")
        .as_int("USD amount, or -1 if unlimited")
    .build())
```

**TypeScript:**
```typescript
const interview = chatfield()
  .type('TechWorkRequest')
  .desc('Gathering project requirements')
  .alice()
    .type('Expert Technology Consultant')
  .bob()
    .type('Product Owner')
  .field('projectName')
    .desc('Project name')
    .hint('Short and memorable')
  .field('scope')
    .desc('What to build')
    .must('specific enough to implement')
    .reject('anything requiring HIPAA compliance')
  .field('targetUsers')
    .desc('Who will use this')
    .must('specific user groups or roles')
  .field('timeline')
    .desc('Completion deadline')
    .must('specific timeframe or deadline')
    .reject('ASAP without specific dates')
  .field('budget')
    .desc('Project budget')
    .must('specific amount')
    .as_int('USD amount, or -1 if unlimited')
  .build()
```

### 7.2 Restaurant Ordering with Context

**Python:**
```python
interview = (chatfield()
    .type("Restaurant Order")
    .alice()
        .type("Server")
        .trait("Speaks in limericks")
    .bob()
        .type("Diner")
        .trait("First-time visitor")
    .field("starter")
    .desc("Starter or appetizer")
        .as_one("selection",
                "Caesar Salad",
                "Shrimp Cocktail",
                "Garden Salad")
    .field("main_course")
    .desc("Main course")
        .as_one("selection",
                "Grilled Salmon",
                "Veggie Pasta",
                "Beef Tenderloin")
    .field("dessert")
    .desc("Dessert selection")
        .as_one("selection",
                "Cheesecake",
                "Chocolate Mousse",
                "Fruit Sorbet")
    .field("hurry")
    .desc("Wants quick service")
        .confidential()
        .as_bool()
    .field("politeness")
    .desc("Politeness level")
        .conclude()
        .as_percent()
    .build())
```

**TypeScript:**
```typescript
const interview = chatfield()
  .type('Restaurant Order')
  .alice()
    .type('Server')
    .trait('Speaks in limericks')
  .bob()
    .type('Diner')
    .trait('First-time visitor')
  .field('starter')
    .desc('Starter or appetizer')
    .as_one('selection',
            'Caesar Salad',
            'Shrimp Cocktail',
            'Garden Salad')
  .field('mainCourse')
    .desc('Main course')
    .as_one('selection',
            'Grilled Salmon',
            'Veggie Pasta',
            'Beef Tenderloin')
  .field('dessert')
    .desc('Dessert selection')
    .as_one('selection',
            'Cheesecake',
            'Chocolate Mousse',
            'Fruit Sorbet')
  .field('hurry')
    .desc('Wants quick service')
    .confidential()
    .as_bool()
  .field('politeness')
    .desc('Politeness level')
    .conclude()
    .as_percent()
  .build()
```

### 7.3 Job Interview with Assessment

**Python:**
```python
interview = (chatfield()
    .type("JobInterview")
    .desc("Software Engineer position")
    .alice()
        .type("Hiring Manager")
        .trait("Professional and encouraging")
    .bob()
        .type("Candidate")
    .field("experience")
    .desc("Relevant experience")
        .must("specific examples or projects")
    .field("technical_skills")
    .desc("Programming languages and tech")
        .hint("Mention specific languages and frameworks")
    .field("has_mentored")
    .desc("Evidence of mentoring")
        .confidential()
        .as_bool()
    .field("shows_leadership")
    .desc("Leadership qualities")
        .confidential()
        .as_bool()
    .field("preparedness")
    .desc("Preparation level")
        .conclude()
        .as_one.assessment("unprepared",
                          "somewhat prepared",
                          "well prepared",
                          "exceptionally prepared")
    .field("cultural_fit")
    .desc("Cultural fit assessment")
        .conclude()
        .as_one.assessment("poor fit",
                          "potential fit",
                          "good fit",
                          "excellent fit")
    .build())
```

**TypeScript:**
```typescript
const interview = chatfield()
  .type('JobInterview')
  .desc('Software Engineer position')
  .alice()
    .type('Hiring Manager')
    .trait('Professional and encouraging')
  .bob()
    .type('Candidate')
  .field('experience')
    .desc('Relevant experience')
    .must('specific examples or projects')
  .field('technicalSkills')
    .desc('Programming languages and tech')
    .hint('Mention specific languages and frameworks')
  .field('hasMentored')
    .desc('Evidence of mentoring')
    .confidential()
    .as_bool()
  .field('showsLeadership')
    .desc('Leadership qualities')
    .confidential()
    .as_bool()
  .field('preparedness')
    .desc('Preparation level')
    .conclude()
    .as_one.assessment('unprepared',
                      'somewhat prepared',
                      'well prepared',
                      'exceptionally prepared')
  .field('culturalFit')
    .desc('Cultural fit assessment')
    .conclude()
    .as_one.assessment('poor fit',
                      'potential fit',
                      'good fit',
                      'excellent fit')
  .build()
```

### 7.4 Thread Management for Persistence

**Python:**
```python
import os

# Create unique thread ID
thread_id = f"user-{user_id}-session-{session_id}"

# Initialize interviewer with thread
interviewer = Interviewer(interview, thread_id=thread_id)

# Conversation can be resumed later with same thread_id
# LangGraph checkpointer maintains state
```

**TypeScript:**
```typescript
// Create unique thread ID
const threadId = `user-${userId}-session-${sessionId}`

// Initialize interviewer with thread
const interviewer = new Interviewer(interview, { threadId })

// Conversation can be resumed later with same threadId
// LangGraph checkpointer maintains state
```

---

## 8. Testing Recipes

### 8.1 Mock LLM for Unit Tests

**Python:**
```python
from langchain_core.messages import AIMessage

class MockLLM:
    def __init__(self):
        self.temperature = 0.0
        self.model = 'mock'
        self.tools = []

    def invoke(self, messages):
        return AIMessage(content="Mock response")

    def bind_tools(self, tools):
        self.tools = tools
        return self

# Use in tests
def test_interview():
    interview = chatfield()\
        .field("name")\
    .desc("Your name")\
        .build()

    mock_llm = MockLLM()
    interviewer = Interviewer(interview, llm=mock_llm)
    # Test logic here
```

**TypeScript:**
```typescript
class MockLLMBackend {
  temperature = 0.0
  modelName = 'mock'
  tools: any[] = []
  boundTools: any[] = []

  async invoke(messages: any[]) {
    return { content: 'Mock response' }
  }

  bind(args: any) {
    if (args.tools) {
      this.boundTools = args.tools
    }
    return this
  }

  bindTools(tools: any[]) {
    this.tools = tools
    this.boundTools = tools
    return this
  }
}

// Use in tests
describe('Interview', () => {
  it('collects field data', async () => {
    const interview = chatfield()
      .field('name')
    .desc('Your name')
      .build()

    const mockLlm = new MockLLMBackend()
    const interviewer = new Interviewer(interview, { llm: mockLlm })
    // Test logic here
  })
})
```

### 8.2 Testing Field Discovery

**Python:**
```python
def test_field_discovery():
    interview = chatfield()\
        .field("name")\
    .desc("Your name")\
        .field("email")\
    .desc("Your email")\
        .field("age")\
            .as_int()\
        .build()

    # Verify fields were registered
    assert "name" in interview._chatfield['fields']
    assert "email" in interview._chatfield['fields']
    assert "age" in interview._chatfield['fields']

    # Verify transformations
    age_field = interview._chatfield['fields']['age']
    assert 'as_int' in age_field['casts']
```

**TypeScript:**
```typescript
describe('field discovery', () => {
  it('registers all fields', () => {
    const interview = chatfield()
      .field('name')
    .desc('Your name')
      .field('email')
    .desc('Your email')
      .field('age')
        .as_int()
      .build()

    // Verify fields were registered
    expect(interview._chatfield.fields['name']).toBeDefined()
    expect(interview._chatfield.fields['email']).toBeDefined()
    expect(interview._chatfield.fields['age']).toBeDefined()

    // Verify transformations
    const ageField = interview._chatfield.fields['age']
    expect(ageField.casts['as_int']).toBeDefined()
  })
})
```

### 8.3 Testing Validation Rules

**Python:**
```python
def test_validation_specs():
    interview = chatfield()\
        .field("email")\
    .desc("Your email")\
            .must("be valid email format")\
            .must("use professional domain")\
            .reject("free email providers")\
            .hint("Use company email")\
        .build()

    specs = interview._chatfield['fields']['email']['specs']
    assert len(specs['must']) == 2
    assert len(specs['reject']) == 1
    assert len(specs['hint']) == 1
```

**TypeScript:**
```typescript
describe('validation rules', () => {
  it('stores must/reject/hint specs', () => {
    const interview = chatfield()
      .field('email')
    .desc('Your email')
        .must('be valid email format')
        .must('use professional domain')
        .reject('free email providers')
        .hint('Use company email')
      .build()

    const specs = interview._chatfield.fields['email'].specs
    expect(specs.must).toHaveLength(2)
    expect(specs.reject).toHaveLength(1)
    expect(specs.hint).toHaveLength(1)
  })
})
```

### 8.4 Integration Testing with Real API

**Python:**
```python
import pytest
import os

@pytest.mark.requires_api_key
def test_real_conversation():
    if not os.getenv('OPENAI_API_KEY'):
        pytest.skip("No API key")

    interview = chatfield()\
        .field("name")\
    .desc("Your name")\
        .build()

    interviewer = Interviewer(interview)

    # Simulate user responses
    message = interviewer.go(None)
    assert message  # AI should greet

    message = interviewer.go("My name is Alice")

    # Should complete after valid input
    assert interview._done
    assert interview.name == "Alice"
```

**TypeScript:**
```typescript
describe('integration tests', () => {
  it('completes real conversation', async () => {
    if (!process.env.OPENAI_API_KEY) {
      return // Skip if no API key
    }

    const interview = chatfield()
      .field('name')
    .desc('Your name')
      .build()

    const interviewer = new Interviewer(interview)

    // Simulate user responses
    let message = await interviewer.go()
    expect(message).toBeTruthy() // AI should greet

    message = await interviewer.go('My name is Alice')

    // Should complete after valid input
    expect(interview._done).toBe(true)
    expect(interview.name).toBe('Alice')
  })
})
```

---

## 9. Integration Recipes

### 9.1 React Integration

**TypeScript:**
```typescript
import { useConversation } from './chatfield/integrations/react'

function ContactForm() {
  const interview = chatfield()
    .field('name')
    .desc('Your name')
    .field('email')
    .desc('Your email')
    .build()

  const {
    messages,
    sendMessage,
    isComplete,
    result
  } = useConversation(interview)

  return (
    <div>
      {messages.map((msg, i) => (
        <div key={i} className={msg.role}>
          {msg.content}
        </div>
      ))}
      {!isComplete && (
        <input
          onSubmit={(e) => sendMessage(e.target.value)}
        />
      )}
      {isComplete && (
        <div>
          <h2>Results</h2>
          <p>Name: {result.name}</p>
          <p>Email: {result.email}</p>
        </div>
      )}
    </div>
  )
}
```

### 9.2 CopilotKit Integration

**TypeScript:**
```typescript
import { CopilotSidebar } from './chatfield/integrations/copilotkit'

function App() {
  const interview = chatfield()
    .field('requirements')
    .desc('Project requirements')
    .build()

  return (
    <CopilotKit>
      <CopilotSidebar interview={interview} />
      <YourMainApp />
    </CopilotKit>
  )
}
```

### 9.3 Express.js API

**TypeScript:**
```typescript
import express from 'express'
import { chatfield, Interviewer } from './chatfield'

const app = express()
app.use(express.json())

const interviews = new Map()

app.post('/interview/start', (req, res) => {
  const interview = chatfield()
    .field('name')
    .desc('Your name')
    .field('email')
    .desc('Your email')
    .build()

  const threadId = `session-${Date.now()}`
  const interviewer = new Interviewer(interview, { threadId })

  interviews.set(threadId, { interview, interviewer })

  res.json({ threadId })
})

app.post('/interview/:threadId/message', async (req, res) => {
  const { threadId } = req.params
  const { message } = req.body

  const { interview, interviewer } = interviews.get(threadId)

  const response = await interviewer.go(message)

  res.json({
    message: response,
    done: interview._done,
    result: interview._done ? {
      name: interview.name,
      email: interview.email
    } : null
  })
})

app.listen(3000)
```

### 9.4 CLI Application

**Python:**
```python
#!/usr/bin/env python3
import argparse
import os
from chatfield import chatfield, Interviewer

def main():
    parser = argparse.ArgumentParser(description='Contact Form CLI')
    parser.add_argument('--thread', help='Thread ID for resuming')
    args = parser.parse_args()

    interview = chatfield()\
        .field("name")\
    .desc("Your full name")\
        .field("email")\
    .desc("Your email address")\
        .field("phone")\
    .desc("Your phone number")\
        .build()

    thread_id = args.thread or f"cli-{os.getpid()}"
    interviewer = Interviewer(interview, thread_id=thread_id)

    print(f"Thread ID: {thread_id}")
    print("(Use --thread {thread_id} to resume)\n")

    user_input = None
    while not interview._done:
        message = interviewer.go(user_input)
        if message:
            print(f"\nAI: {message}")
        if not interview._done:
            user_input = input("\nYou: ").strip()

    print("\n--- Collected Information ---")
    print(f"Name: {interview.name}")
    print(f"Email: {interview.email}")
    print(f"Phone: {interview.phone}")

if __name__ == "__main__":
    main()
```

---

## 10. Production Recipes

### 10.1 Error Handling

**Python:**
```python
from chatfield import chatfield, Interviewer

def run_interview_safely(interview):
    try:
        interviewer = Interviewer(interview)
        user_input = None

        while not interview._done:
            try:
                message = interviewer.go(user_input)
                if message:
                    print(f"AI: {message}")
                if not interview._done:
                    user_input = input("You: ").strip()
            except KeyboardInterrupt:
                print("\n[Interview paused]")
                print(f"Thread ID: {interviewer.thread_id}")
                break
            except Exception as e:
                print(f"Error during conversation: {e}")
                # Log error, retry, or exit
                break

        return interview._done

    except Exception as e:
        print(f"Failed to start interview: {e}")
        return False
```

**TypeScript:**
```typescript
async function runInterviewSafely(interview: Interview) {
  try {
    const interviewer = new Interviewer(interview)
    let userInput: string | undefined = undefined

    while (!interview._done) {
      try {
        const message = await interviewer.go(userInput)
        if (message) {
          console.log(`AI: ${message}`)
        }
        if (!interview._done) {
          userInput = await getUserInput()
        }
      } catch (error) {
        console.error('Error during conversation:', error)
        // Log error, retry, or exit
        break
      }
    }

    return interview._done

  } catch (error) {
    console.error('Failed to start interview:', error)
    return false
  }
}
```

### 10.2 Rate Limiting

**Python:**
```python
import time
from functools import wraps

def rate_limit(calls_per_minute=10):
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = min_interval - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
            last_called[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(calls_per_minute=20)
def call_interviewer(interviewer, user_input):
    return interviewer.go(user_input)
```

**TypeScript:**
```typescript
class RateLimiter {
  private lastCalled: number = 0
  private minInterval: number

  constructor(callsPerMinute: number = 10) {
    this.minInterval = 60000 / callsPerMinute // ms
  }

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    const elapsed = Date.now() - this.lastCalled
    const waitTime = this.minInterval - elapsed

    if (waitTime > 0) {
      await new Promise(resolve => setTimeout(resolve, waitTime))
    }

    this.lastCalled = Date.now()
    return await fn()
  }
}

const limiter = new RateLimiter(20)

async function callInterviewer(interviewer, userInput) {
  return await limiter.execute(() => interviewer.go(userInput))
}
```

### 10.3 Logging and Monitoring

**Python:**
```python
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('chatfield')

def run_with_logging(interview):
    logger.info(f"Starting interview: {interview._chatfield['type']}")
    start_time = datetime.now()

    interviewer = Interviewer(interview)
    user_input = None
    message_count = 0

    while not interview._done:
        message = interviewer.go(user_input)
        message_count += 1

        if message:
            logger.debug(f"AI message #{message_count}: {message[:50]}...")

        if not interview._done:
            user_input = input("You: ").strip()
            logger.debug(f"User input #{message_count}: {user_input[:50]}...")

    duration = (datetime.now() - start_time).total_seconds()
    logger.info(f"Interview completed in {duration:.2f}s with {message_count} messages")

    # Log collected fields
    for field_name in interview._chatfield['fields'].keys():
        value = getattr(interview, field_name, None)
        logger.info(f"Collected {field_name}: {value}")
```

**TypeScript:**
```typescript
import winston from 'winston'

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
})

async function runWithLogging(interview: Interview) {
  logger.info('Starting interview', {
    type: interview._chatfield.type
  })
  const startTime = Date.now()

  const interviewer = new Interviewer(interview)
  let userInput: string | undefined = undefined
  let messageCount = 0

  while (!interview._done) {
    const message = await interviewer.go(userInput)
    messageCount++

    if (message) {
      logger.debug('AI message', {
        count: messageCount,
        preview: message.substring(0, 50)
      })
    }

    if (!interview._done) {
      userInput = await getUserInput()
      logger.debug('User input', {
        count: messageCount,
        preview: userInput.substring(0, 50)
      })
    }
  }

  const duration = (Date.now() - startTime) / 1000
  logger.info('Interview completed', {
    duration,
    messageCount
  })

  // Log collected fields
  for (const fieldName of Object.keys(interview._chatfield.fields)) {
    const value = interview[fieldName]
    logger.info('Collected field', { fieldName, value })
  }
}
```

### 10.4 Cost Tracking

**Python:**
```python
class CostTracker:
    def __init__(self):
        self.input_tokens = 0
        self.output_tokens = 0
        # OpenAI GPT-4o pricing (example)
        self.input_cost_per_1k = 0.00250
        self.output_cost_per_1k = 0.01000

    def add_usage(self, usage):
        self.input_tokens += usage.get('prompt_tokens', 0)
        self.output_tokens += usage.get('completion_tokens', 0)

    def get_cost(self):
        input_cost = (self.input_tokens / 1000) * self.input_cost_per_1k
        output_cost = (self.output_tokens / 1000) * self.output_cost_per_1k
        return input_cost + output_cost

    def report(self):
        return {
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'total_cost': self.get_cost()
        }

# Usage
tracker = CostTracker()
# Track after each API call
# tracker.add_usage(response.usage)
```

**TypeScript:**
```typescript
class CostTracker {
  private inputTokens = 0
  private outputTokens = 0
  // OpenAI GPT-4o pricing (example)
  private inputCostPer1k = 0.00250
  private outputCostPer1k = 0.01000

  addUsage(usage: { prompt_tokens?: number; completion_tokens?: number }) {
    this.inputTokens += usage.prompt_tokens || 0
    this.outputTokens += usage.completion_tokens || 0
  }

  getCost(): number {
    const inputCost = (this.inputTokens / 1000) * this.inputCostPer1k
    const outputCost = (this.outputTokens / 1000) * this.outputCostPer1k
    return inputCost + outputCost
  }

  report() {
    return {
      inputTokens: this.inputTokens,
      outputTokens: this.outputTokens,
      totalCost: this.getCost()
    }
  }
}

// Usage
const tracker = new CostTracker()
// Track after each API call
// tracker.addUsage(response.usage)
```

---

## 11. Debugging & Troubleshooting

### 11.1 Inspecting Interview Structure

**Python:**
```python
import json

interview = (chatfield()
    .field("name")
    .desc("Your name")
        .must("include first and last")
        .as_string()
    .build())

# View full structure
print(json.dumps(interview._chatfield, indent=2))

# Check specific field
field_data = interview._chatfield['fields']['name']
print(f"Description: {field_data['desc']}")
print(f"Specs: {field_data['specs']}")
print(f"Casts: {field_data['casts']}")
```

**TypeScript:**
```typescript
const interview = chatfield()
  .field('name')
    .desc('Your name')
    .must('include first and last')
    .as_string()
  .build()

// View full structure
console.log(JSON.stringify(interview._chatfield, null, 2))

// Check specific field
const fieldData = interview._chatfield.fields['name']
console.log('Description:', fieldData.desc)
console.log('Specs:', fieldData.specs)
console.log('Casts:', fieldData.casts)
```

### 11.2 LangSmith Tracing

Enable detailed tracing with LangSmith:

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=your-langsmith-key
export LANGCHAIN_PROJECT=chatfield-debug
```

**Python:**
```python
# Tracing is automatically enabled when env vars are set
interviewer = Interviewer(interview)
# Check console for trace URLs
```

**TypeScript:**
```typescript
// Tracing is automatically enabled when env vars are set
const interviewer = new Interviewer(interview)
// Check console for trace URLs
```

### 11.3 Debugging Field Values

**Python:**
```python
# After collection
print(f"Raw value: {interview.name}")
print(f"As quote: {interview.name.as_quote}")
print(f"Context: {interview.name.as_context}")

# Check if field was collected
if hasattr(interview, 'name') and interview.name:
    print("Name was collected")
else:
    print("Name was not collected")

# View all field values
print(interview._pretty())
```

**TypeScript:**
```typescript
// After collection
console.log('Raw value:', interview.name)
console.log('As quote:', interview.name.as_quote)
console.log('Context:', interview.name.as_context)

// Check if field was collected
if (interview.name) {
  console.log('Name was collected')
} else {
  console.log('Name was not collected')
}

// View all field values
console.log(interview._pretty())
```

### 11.4 Debugging State Machine

**Python:**
```python
from chatfield import Interviewer

interviewer = Interviewer(interview)

# Get current state
state = interviewer.graph.get_state()
print(f"Current node: {state.next}")
print(f"Messages: {len(state.values.get('messages', []))}")

# Step through conversation
for step in interviewer.graph.stream({"messages": []}):
    print(f"Node: {step}")
```

**TypeScript:**
```typescript
import { Interviewer } from './chatfield/interviewer'

const interviewer = new Interviewer(interview)

// Get current state
const state = await interviewer.graph.getState()
console.log('Current node:', state.next)
console.log('Messages:', state.values.messages?.length || 0)

// Step through conversation
for await (const step of interviewer.graph.stream({ messages: [] })) {
  console.log('Node:', step)
}
```

### 11.5 Common Issues and Solutions

**Issue: Field not collected**
```python
# Check if field is defined
assert "field_name" in interview._chatfield['fields']

# Check if validation is too strict
field = interview._chatfield['fields']['field_name']
print(f"Must rules: {field['specs']['must']}")
print(f"Reject rules: {field['specs']['reject']}")
```

**Issue: Transformation not working**
```python
# Verify transformation is defined
field = interview._chatfield['fields']['field_name']
assert 'as_int' in field['casts']

# Check if field has value
assert interview.field_name is not None

# Access transformation
print(interview.field_name.as_int)
```

**Issue: Conversation not progressing**
```python
# Check _done flag
print(f"Interview done: {interview._done}")

# Check collected fields
collected = [name for name, field in interview._chatfield['fields'].items()
             if field.get('value') is not None]
print(f"Collected fields: {collected}")

# Check remaining fields
remaining = [name for name, field in interview._chatfield['fields'].items()
             if field.get('value') is None]
print(f"Remaining fields: {remaining}")
```

### 11.6 Performance Profiling

**Python:**
```python
import cProfile
import pstats

def profile_interview():
    interview = chatfield()\
        .field("name")\
    .desc("Your name")\
        .build()

    interviewer = Interviewer(interview)
    interviewer.go(None)
    interviewer.go("My name is Alice")

# Profile the function
profiler = cProfile.Profile()
profiler.enable()
profile_interview()
profiler.disable()

# Print stats
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

**TypeScript:**
```typescript
// Using built-in performance API
async function profileInterview() {
  performance.mark('interview-start')

  const interview = chatfield()
    .field('name')
    .desc('Your name')
    .build()

  const interviewer = new Interviewer(interview)
  await interviewer.go()
  await interviewer.go('My name is Alice')

  performance.mark('interview-end')
  performance.measure('interview', 'interview-start', 'interview-end')

  const measure = performance.getEntriesByName('interview')[0]
  console.log(`Duration: ${measure.duration}ms`)
}
```

---

## Appendix: Quick Reference

### Builder Methods

| Method | Python | TypeScript | Purpose |
|--------|--------|------------|---------|
| Interview Type | `.type("Name")` | `.type('Name')` | Set interview type |
| Description | `.desc("text")` | `.desc('text')` | Set description |
| Field | `.field("name")
    .desc("desc")` | `.field('name')
    .desc('desc')` | Define field |
| Alice Role | `.alice()` | `.alice()` | Configure interviewer |
| Bob Role | `.bob()` | `.bob()` | Configure user |
| Trait | `.trait("text")` | `.trait('text')` | Add personality |
| Validation | `.must("rule")` | `.must('rule')` | Add requirement |
| Rejection | `.reject("rule")` | `.reject('rule')` | Add rejection |
| Hint | `.hint("text")` | `.hint('text')` | Add guidance |
| Confidential | `.confidential()` | `.confidential()` | Hide from conversation |
| Conclusion | `.conclude()` | `.conclude()` | Assess at end |

### Transformation Methods

| Method | Python | TypeScript | Result Type |
|--------|--------|------------|-------------|
| Integer | `.as_int()` | `.as_int()` | `int` / `number` |
| Float | `.as_float()` | `.as_float()` | `float` / `number` |
| Boolean | `.as_bool()` | `.as_bool()` | `bool` / `boolean` |
| String | `.as_str('name')` | `.as_str('name')` | `str` / `string` |
| List | `.as_list()` | `.as_list()` | `list` / `Array` |
| Set | `.as_set('name')` | `.as_set('name')` | `set` / `Set` |
| Percent | `.as_percent()` | `.as_percent()` | `float` / `number` (0-1) |
| Language | `.as_lang('code')` | `.as_lang('code')` | `str` / `string` |
| One | `.as_one('name', ...)` | `.as_one('name', ...)` | Single choice |
| Maybe | `.as_maybe('name', ...)` | `.as_maybe('name', ...)` | 0 or 1 choice |
| Multi | `.as_multi('name', ...)` | `.as_multi('name', ...)` | 1+ choices |
| Any | `.as_any('name', ...)` | `.as_any('name', ...)` | 0+ choices |

### Field Access

| Access | Python | TypeScript | Returns |
|--------|--------|------------|---------|
| Raw Value | `interview.field` | `interview.field` | String value |
| Quote | `interview.field.as_quote` | `interview.field.as_quote` | Direct quote |
| Context | `interview.field.as_context` | `interview.field.as_context` | Conversation context |
| Transform | `interview.field.as_int` | `interview.field.as_int` | Transformed value |
| Pretty Print | `interview._pretty()` | `interview._pretty()` | Formatted output |

---

## Contributing

To contribute new recipes to this cookbook:

1. Follow the existing format and structure
2. Include both Python and TypeScript examples
3. Test all code examples before submitting
4. Add recipes in order of complexity
5. Update the table of contents

For questions or suggestions, open an issue at the Chatfield repository.

---

**Version:** 1.0
**Last Updated:** January 2025
**Compatible With:** Chatfield Python v0.2.0, TypeScript v0.1.0
