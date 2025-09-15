#!/usr/bin/env npx tsx
/**
 * Favorite Number Example
 * =======================
 * 
 * This example demonstrates the extensive transformation system:
 * - Basic transformations (as_int, as_float, as_bool)
 * - Language transformations (as_lang)
 * - Set and list transformations (asSet, asList)
 * - Cardinality decorators (asOne, asMaybe, asMulti, asAny)
 * - Complex sub-attribute transformations
 * 
 * Run with:
 *     npx tsx examples/favorite-number.ts
 * 
 * For automated demo:
 *     npx tsx examples/favorite-number.ts --auto
 */

import * as path from 'path';
import * as dotenv from 'dotenv';
import { parseArgs } from 'util';
import { chatfield } from '../src/builder';
import { Interview } from '../src/interview';
import { Interviewer } from '../src/interviewer';

// Load environment variables from top-level .env file
dotenv.config({ path: path.resolve(__dirname, '../../.env') });

function createNumberInterview(): Interview {
    /**Create an interview about favorite numbers with many transformations.**/
    return chatfield()
        .type("NumberInterview")
        .desc("Let's explore your relationship with numbers")
        
        .alice()
            .type("Mathematician")
            .trait("Enthusiastic about number properties")
        
        .bob()
            .type("Number Enthusiast")
        
        .field("favorite")
            .desc("What is your favorite number?")
            .must("a number between 1 and 100")
            .must("Not obscure like 73 or 88")
            .must("Not too common like 7 or 10")
            .must("A whole number")
            .must("Not cliche like 42")
            .hint("Do not cite the validation rules unless asked or an invalid answer is given")
            
            // Basic transformations
            .as_int()
            .as_float("The number as a floating point value")
            .as_percent("The number as a real 0.0-1.0")
            
            // Language transformations
            .as_lang('fr', "French translation")
            .as_lang('de', "German translation")
            .as_lang('es', "Spanish translation")
            .as_lang('ja', "Japanese translation")
            .as_lang('th', "Thai translation")
            
            // Boolean transformations with sub-attributes
            .as_bool('even', "True if even, False if odd")
            .as_bool('prime', "True if prime number")
            .as_bool('perfect_square', "True if perfect square")
            .as_bool('power_of_two', "True if power of two")
            
            // // String transformation
            .as_str('longhand', "Written out in English words")
            
            // // Set transformation
            .as_set('factors', "All factors of the number not counting 1")
            
            // // Cardinality decorators for properties
            .as_one('size_category', "tiny (1-10)", "small (11-25)", "medium (26-50)", "large (51-75)", "huge (76-100)")
            .as_maybe('special_property', "fibonacci", "perfect number", "triangular number")
            .as_multi('math_properties', "even", "odd", "prime", "composite", "square", "cubic")
            .as_any('cultural_significance', "lucky", "unlucky", "sacred", "mystical")
        
        .field("reason")
            .desc("Why is this your favorite number?")
            .hint("Perhaps from a well-known reference or personal experience")
        
        .build();
}

async function runInteractive(interview: Interview): Promise<boolean> {
    /**Run the interview interactively.**/
    const threadId = `numbers-${process.pid}`;
    console.log(`Starting number interview (thread: ${threadId})`);
    console.log("=".repeat(60));
    
    const interviewer = new Interviewer(interview, { threadId });
    
    let userInput: string | undefined = undefined;
    while (!interview._done) {
        const message = await interviewer.go(userInput);
        
        if (message) {
            console.log(`\nMathematician: ${message}`);
        }
        
        if (!interview._done) {
            try {
                process.stdout.write("\nYou: ");
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
                console.log("\n[Interview ended]");
                break;
            }
        }
    }
    
    return interview._done;
}

async function runAutomated(interview: Interview): Promise<boolean> {
    /**Run with prefab inputs for demonstration.**/
    const prefabInputs = [
        "My favorite number is 42",
        "It's the answer to life, the universe, and everything according to Douglas Adams!",
        "I really don't like 13, it feels unlucky"
    ];
    
    const threadId = `numbers-demo-${process.pid}`;
    console.log(`Running automated demo (thread: ${threadId})`);
    console.log("=".repeat(60));
    
    const interviewer = new Interviewer(interview, { threadId });
    
    const inputIter = prefabInputs[Symbol.iterator]();
    let userInput: string | undefined = undefined;
    
    while (!interview._done) {
        const message = await interviewer.go(userInput);
        
        if (message) {
            console.log(`\nMathematician: ${message}`);
        }
        
        if (!interview._done) {
            const next = inputIter.next();
            if (next.done) {
                console.log("\n[Demo inputs exhausted]");
                break;
            }
            userInput = next.value;
            console.log(`\nYou: ${userInput}`);
        }
    }
    
    return interview._done;
}

function displayResults(interview: Interview): void {
    /**Display the collected number information with transformations.**/
    console.log("\n" + "=".repeat(60));
    console.log("NUMBER ANALYSIS");
    console.log("-".repeat(60));
    console.log(interview._pretty());
    console.log("=".repeat(60));
}

async function main(): Promise<void> {
    /**Main entry point.**/
    const { values } = parseArgs({
        args: process.argv.slice(2),
        options: {
            auto: {
                type: 'boolean',
                short: 'a',
                default: false
            }
        }
    });
    
    // Check for API key
    if (!process.env.OPENAI_API_KEY) {
        console.error("Error: OPENAI_API_KEY not found in environment");
        console.error("Please set your OpenAI API key in .env file");
        process.exit(1);
    }
    
    // Create and run the interview
    const interview = createNumberInterview();
    
    let completed: boolean;
    if (values.auto) {
        completed = await runAutomated(interview);
    } else {
        completed = await runInteractive(interview);
    }
    
    // Display results if completed
    if (completed) {
        displayResults(interview);
    } else {
        console.log("\n[Interview not completed]");
    }
    
    process.exit(0);
}

// Run main function
main().catch((error) => {
    console.error('Error:', error);
    process.exit(1);
});