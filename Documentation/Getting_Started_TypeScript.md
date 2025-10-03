# Getting Started with Chatfield (TypeScript/JavaScript)

This guide walks you through creating your first Chatfield project in TypeScript.

## Prerequisites

- Node.js 20.0.0 or higher
- npm or yarn package manager
- OpenAI API key (see [Mandatory_Environment_File.md](Mandatory_Environment_File.md))

## Quick Start

### 1. Clone the Chatfield Repository

```bash
git clone https://github.com/jhs/Chatfield.git
cd Chatfield/TypeScript
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Link Chatfield Globally

```bash
npm link
```

**Note** Until the Rollup build works, skip to step 7.

### 4. Create Your Project Directory

```bash
cd ../..  # or wherever you want your project
mkdir my-chatfield-project
cd my-chatfield-project
npm init -y
```

### 5. Install TypeScript Dependencies (for TypeScript projects)

```bash
npm install --save-dev typescript tsx @types/node
```

### 6. Link Chatfield to Your Project

```bash
npm link @chatfield/core
```

### 7. Configure API Key

Create a `.env` file in your project directory:

```bash
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

### 8. Create Your First Script

Create a file named `my-first-form.ts`:

**Important:** Until the build works, you must place this file in the Chatfield `TypeScript/` directory or anywhere deeper. You must then import using a relative path to the `chatfield/` source code directory. For example, `TypeScript/my-first-form.ts`:

```typescript
import { chatfield, Interviewer } from './chatfield/';

// Load API key from environment
process.env['OPENAI_API_KEY'] = process.env['OPENAI_API_KEY'] || '';

// Define your form using the fluent builder API
let form = chatfield()
    .type('Example Form')
    .field('name')
        .desc('Your Name')
    .field('age')
        .desc('Your Age')
        .as_int()
    .build();

// Create the interviewer
let interviewer = new Interviewer(form);

// Start the conversation
async function main() {
    let first_message;
    if (process.env['OPENAI_API_KEY']) {
        first_message = await interviewer.go();
    } else {
        first_message = 'No OPENAI_API_KEY set yet';
    }

    // Display the results
    console.log('-------------');
    console.log(first_message);
    console.log('-------------');
    console.log(form._pretty());
}

main()
```

### 9. Run Your Script

```bash
# Using tsx (TypeScript)
npx tsx my-first-form.ts
```

Or compile TypeScript to JavaScript and run:

```bash
npx tsc my-first-form.ts
node my-first-form.js
```

## What's Happening?

1. **Form Definition**: The `chatfield()` builder creates a conversational form with two fields:
   - `name`: A text field for the user's name
   - `age`: A number field that will be validated and converted to an integer

2. **Interviewer**: The `Interviewer` class orchestrates the conversation using LangGraph

3. **Conversation Flow**: The `go()` method starts the conversation and returns the first message (async)

4. **Pretty Print**: The `_pretty()` method displays the form structure and collected values

## Using with JavaScript

For plain JavaScript projects, create `my-first-form.js`:

```javascript
const { chatfield, Interviewer } = require('@chatfield/core');

process.env['OPENAI_API_KEY'] = process.env['OPENAI_API_KEY'] || '';

const form = chatfield()
    .type('Example Form')
    .field('name')
        .desc('Your Name')
    .field('age')
        .desc('Your Age')
        .as_int()
    .build();

const interviewer = new Interviewer(form);

(async () => {
    const first_message = process.env['OPENAI_API_KEY']
        ? await interviewer.go()
        : 'No OPENAI_API_KEY set yet';

    console.log('-------------');
    console.log(first_message);
    console.log('-------------');
    console.log(form._pretty());
})();
```

Run with:
```bash
node my-first-form.js
```

## Next Steps

### Add Validation

```typescript
const form = chatfield()
    .field('email')
        .desc('Your email address')
        .must('be a valid email format')
    .field('age')
        .desc('Your age')
        .as_int()
        .must('be between 18 and 120')
    .build();
```

### Add Transformation

```typescript
const form = chatfield()
    .field('languages')
        .desc('Programming languages you know')
        .as_list()
    .field('confirm')
        .desc('Do you agree to the terms?')
        .as_bool()
    .build();
```

### Add Multiple Choice

```typescript
const form = chatfield()
    .field('favorite_color')
        .desc('What is your favorite color?')
        .as_one(['Red', 'Blue', 'Green', 'Yellow'])
    .field('skills')
        .desc('What skills do you have?')
        .as_multi(['Python', 'JavaScript', 'Go', 'Rust'])
    .build();
```

### Customize the Conversation

```typescript
const form = chatfield()
    .type('Job Application')
    .desc('Collect information about job candidates')
    .alice('Hiring Manager')
    .alice_trait('professional and friendly')
    .bob('Job Candidate')
    .field('position')
        .desc('What position are you applying for?')
        .must('include the specific role and department')
    .build();
```

## Complete Example

Here's a more comprehensive TypeScript example:

```typescript
import { chatfield, Interviewer } from '@chatfield/core';

process.env['OPENAI_API_KEY'] = process.env['OPENAI_API_KEY'] || '';

// Create a restaurant order form
const form = chatfield()
    .type('Restaurant Order')
    .desc('Take a customer order at a restaurant')
    .alice('Server')
    .alice_trait('friendly and attentive')
    .bob('Customer')

    .field('table_number')
        .desc('Table number')
        .as_int()
        .must('be between 1 and 50')

    .field('main_course')
        .desc('Main course selection')
        .as_one(['Steak', 'Salmon', 'Pasta', 'Salad'])

    .field('sides')
        .desc('Side dishes')
        .as_multi(['Fries', 'Rice', 'Vegetables', 'Soup'])

    .field('special_requests')
        .desc('Any special requests or dietary restrictions?')
        .hint('Allergies, preferences, etc.')

    .build();

const interviewer = new Interviewer(form);

// Start conversation
(async () => {
    const firstMessage = await interviewer.go();
    console.log(firstMessage);

    // In a real application, you would continue the conversation loop
    // by collecting user responses and calling interviewer.respond(userMessage)
})();
```

## TypeScript Configuration

Create a `tsconfig.json` for better type safety:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "moduleResolution": "node"
  },
  "include": ["**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
```

## React Integration

For React applications, Chatfield provides hooks and components:

```typescript
import { useConversation } from '@chatfield/core/integrations/react';

function MyForm() {
    const form = chatfield()
        .field('name').desc('Your name')
        .field('email').desc('Your email')
        .build();

    const { messages, sendMessage, isComplete } = useConversation(form);

    return (
        <div>
            {messages.map((msg, i) => (
                <div key={i}>{msg.content}</div>
            ))}
            {!isComplete && (
                <input onSubmit={(e) => sendMessage(e.target.value)} />
            )}
        </div>
    );
}
```

## CopilotKit Integration

For conversational UI with CopilotKit:

```typescript
import { ChatfieldSidebar } from '@chatfield/core/integrations/copilotkit';

function App() {
    const form = chatfield()
        .field('name').desc('Your name')
        .build();

    return <ChatfieldSidebar form={form} />;
}
```

## Running Tests

If you're developing with Chatfield, you can run the test suite:

```bash
# From the Chatfield/TypeScript directory
cd TypeScript
npm install
npm test
```

## Troubleshooting

### API Key Issues

If you see "No OPENAI_API_KEY set yet":
1. Verify your `.env` file exists and contains the key
2. Install dotenv: `npm install dotenv`
3. Load it in your script: `require('dotenv').config()`
4. Try setting the key directly: `export OPENAI_API_KEY=your-key-here`

### Import Errors

If you see `Cannot find module '@chatfield/core'`:
1. Ensure you've linked the package: `npm link @chatfield/core`
2. Verify the Chatfield repo has `npm link` run in the TypeScript directory
3. Check your `package.json` dependencies

### TypeScript Errors

If you encounter TypeScript compilation errors:
```bash
npm install --save-dev @types/node
```

### Async/Await Issues

Remember that `interviewer.go()` and `interviewer.respond()` are async:
```typescript
// ✅ Correct
const message = await interviewer.go();

// ❌ Wrong
const message = interviewer.go(); // Returns a Promise
```

## Resources

- [Full TypeScript Documentation](../TypeScript/CLAUDE.md)
- [TypeScript Examples](../TypeScript/examples/)
- [Environment Setup](Mandatory_Environment_File.md)
- [Test Harmonization Guide](Test_Harmonization.md)

## Development Mode

To work on Chatfield itself:

```bash
cd Chatfield/TypeScript
npm install
npm run build    # Compile TypeScript
npm run dev      # Watch mode
```

## Package Scripts

Add these to your `package.json`:

```json
{
  "scripts": {
    "start": "tsx my-first-form.ts",
    "build": "tsc",
    "dev": "tsx watch my-first-form.ts"
  }
}
```

Then run with:
```bash
npm start        # Run once
npm run dev      # Watch and reload
```
