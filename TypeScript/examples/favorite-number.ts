#!/usr/bin/env npx tsx
/**
 * Favorite Number Example
 * =======================
 * 
 * This example demonstrates the extensive transformation system:
 * - Basic transformations (asInt, asFloat, asBool)
 * - Language transformations (asLang)
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

import * as dotenv from 'dotenv';
import { parseArgs } from 'util';
import { chatfield } from '../src/builder';
import { Interviewer } from '../src/interviewer';
import type { Gatherer } from '../src/types';

// Load environment variables
dotenv.config();

function createNumberInterview(): Gatherer {
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
            .hint("Think about a number that has special meaning to you")
            
            // Basic transformations
            .asInt()
            .asFloat("The number as a floating point value")
            .asPercent("The number as a percentage of 100")
            
            // Language transformations
            .asLang('fr', "French translation")
            .asLang('de', "German translation")
            .asLang('es', "Spanish translation")
            .asLang('ja', "Japanese translation")
            .asLang('th', "Thai translation")
            
            // Boolean transformations with sub-attributes
            .asBool('even', "True if even, False if odd")
            .asBool('prime', "True if prime number")
            .asBool('perfect_square', "True if perfect square")
            .asBool('power_of_two', "True if power of two")
            
            // String transformation
            .asStr('longhand', "Written out in English words")
            
            // Set transformation
            .asSet('factors', "All factors of the number")
            
            // Cardinality decorators for properties
            .asOne('size_category', "tiny (1-10)", "small (11-25)", "medium (26-50)", "large (51-75)", "huge (76-100)")
            .asMaybe('special_property', "fibonacci", "perfect number", "triangular number")
            .asMulti('math_properties', "even", "odd", "prime", "composite", "square", "cubic")
            .asAny('cultural_significance', "lucky", "unlucky", "sacred", "mystical")
        
        .field("reason")
            .desc("Why is this your favorite number?")
            .hint("Share what makes this number special to you")
        
        .field("least_favorite")
            .desc("What number do you like the least? (1-100)")
            .must("a number between 1 and 100")
            .asInt()
            .asStr('longhand', "Written out in English words")
            .asBool('unlucky', "True if commonly considered unlucky")
        
        .build();
}

async function runInteractive(interview: Gatherer): Promise<boolean> {
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

async function runAutomated(interview: Gatherer): Promise<boolean> {
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

function displayResults(interview: Gatherer): void {
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