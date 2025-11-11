#!/usr/bin/env npx tsx

/**
 * Chatfield Form Completion Boilerplate
 * ======================================
 *
 * This boilerplate drives a Chatfield interview in the terminal via stdio.
 * It's designed to work with form models created using the CC-guidance prompt.
 *
 * Workflow:
 * 1. Runs the imported Chatfield interview
 * 2. Conducts conversation to collect all field data
 * 3. Waits for user approval (_chatfield_ready field)
 * 4. Outputs complete structured data for form population
 *
 * Usage:
 *     npx tsx examples/boilerplate.ts
 *
 * To use with your own form model:
 * 1. Create your interview definition in ./cc/your-form.ts
 * 2. Change the import below from "./cc/hello-world" to "./cc/your-form"
 * 3. Run this script
 *
 * The script will:
 * - Collect all field data through natural conversation
 * - Apply all transformations and validations
 * - Wait for explicit user approval
 * - Output the complete data structure ready for form population
 */
import * as dotenv from 'dotenv';
import * as path from 'path';

import { Interview } from '../chatfield/interview';
import { Interviewer } from '../chatfield/interviewer';
// ========================================
// EDIT THIS LINE TO USE YOUR FORM MODEL
// ========================================
import { interview } from './cc/china-visa-application';

// Example: import { interview } from "./cc/contact-form";
// Example: import { interview } from "./cc/registration-form";

// Load environment variables from top-level .env.secret file
dotenv.config({ path: path.resolve(__dirname, '../../.env.secret') });

async function runInterview(interview: Interview): Promise<boolean> {
  /**Run the interview interactively via stdin/stdout.**/
  const threadId = `form-${process.pid}-${Date.now()}`;

  const interviewer = new Interviewer(interview, { threadId });

  let userInput: string | undefined = undefined;
  while (!interview._done) {
    const message = await interviewer.go(userInput);

    if (message) {
      console.log(`\nAssistant: ${message}`);
    }

    if (!interview._done) {
      try {
        process.stdout.write('\nYou: ');
        userInput = await new Promise<string>((resolve) => {
          const stdin = process.stdin;
          stdin.setRawMode(false);
          stdin.resume();
          stdin.setEncoding('utf8');
          stdin.once('data', (data) => {
            stdin.pause();
            resolve(data.toString().trim());
          });
        });
      } catch (error) {
        console.log('\n[Interview ended]');
        break;
      }
    }
  }

  return interview._done;
}

function displayResults(interview: Interview): void {
  console.log(interview._pretty());
}

async function main(): Promise<void> {
  /**Main entry point.**/

  // Check for API key
  if (!process.env.OPENAI_API_KEY) {
    console.error('Error: OPENAI_API_KEY not found in environment');
    console.error('Please set your OpenAI API key in .env.secret file');
    console.error('\nCreate a file at: Chatfield/.env.secret');
    console.error('Add line: OPENAI_API_KEY=your-api-key-here');
    process.exit(1);
  }

  // Run the interview
  const completed = await runInterview(interview);

  // Display results if completed
  if (completed) {
    displayResults(interview);
  } else {
    console.log('\n[Interview not completed]');
    process.exit(1);
  }

  process.exit(0);
}

// Run main function
main().catch((error) => {
  console.error('Error:', error);
  process.exit(1);
});
