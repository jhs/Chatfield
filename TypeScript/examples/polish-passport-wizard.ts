#!/usr/bin/env npx tsx
/**
 * Polish Passport Application Wizard Example
 * ===========================================
 *
 * This example demonstrates a multi-step passport application wizard for children
 * in Poland, supporting English-speaking users ("Bob") who may need assistance
 * understanding Polish administrative concepts.
 *
 * The wizard collects:
 * - Child's age range (determines available options)
 * - Application method (online or in-office)
 * - Application location (Poland or abroad)
 * - Pickup location (Poland or abroad)
 *
 * Features demonstrated:
 * - Conditional fields based on previous answers
 * - Choice constraints (.as_one for single selection)
 * - Helpful context for non-Polish speakers
 * - Professional government service tone
 * - Educational hints about Polish administrative processes
 *
 * Run with:
 *     npx tsx examples/polish-passport-wizard.ts
 *
 * For automated demo:
 *     npx tsx examples/polish-passport-wizard.ts --auto
 */

import * as path from 'path';
import * as dotenv from 'dotenv';
import { parseArgs } from 'util';
import { chatfield } from '../chatfield/builder';
import { Interview } from '../chatfield/interview';
import { Interviewer } from '../chatfield/interviewer';

// Load environment variables from top-level .env.secret file
dotenv.config({ path: path.resolve(__dirname, '../../.env.secret') });

function createPassportWizard(): Interview {
    /**
     * Create a passport application wizard interview.
     *
     * This mirrors the Polish government passport application form,
     * adapted for conversational data collection with an English-speaking user.
     */
    return chatfield()
        .type("PassportApplicationWizard")
        .desc("Polish Passport Application Assistant for Children")

        // Alice is the helpful government service representative
        .alice()
            .type("Passport Office Assistant")
            .trait("Professional and patient")
            .trait("Helpful with explaining Polish administrative procedures")
            .trait("Provides context for non-Polish speakers")

        // Bob is an English-speaking parent/guardian
        .bob()
            .type("Parent/Guardian")
            .trait.possible("unfamiliar-with-polish", "asks questions about Polish terms or procedures")
            .trait.possible("experienced-applicant", "mentions previous passport applications")

        // Field 1: Child's age range
        .field("child_age_range")
            .desc("What is the age of the child for whom you're applying for a passport?")
            .hint("This determines which documents and procedures apply")
            .hint("Polish passport rules differ by age group")
            .must("specify one of the three age ranges")
            .as_one(
                "up to 5 years old",
                "5 to 12 years old",
                "12 to 18 years old (until completion of 18th year)"
            )

        // Field 2: Application method
        .field("application_method")
            .desc("How would you like to submit the passport application?")
            .hint("Online applications can be submitted through the Polish government portal")
            .hint("In-office applications are submitted at a passport office (urząd)")
            .must("choose either online or in-office")
            .as_one(
                "online through internet",
                "in-office at passport office"
            )

        // Field 3: Application location (where to submit)
        .field("application_location")
            .desc("Where do you want to submit the passport application?")
            .hint("Applications can be submitted in Poland or at Polish consulates abroad")
            .hint("If you're currently abroad, find your nearest Polish consulate")
            .must("specify either Poland or abroad")
            .as_one(
                "in Poland",
                "abroad at Polish consulate"
            )

        // Field 4: Pickup location (where to collect passport)
        .field("pickup_location")
            .desc("Where would you like to pick up the completed passport?")
            .hint("You can collect the passport in Poland or at a Polish consulate abroad")
            .hint("Pickup location may differ from application location depending on your circumstances")
            .must("specify either Poland or abroad")
            .reject("vague answers like 'wherever is convenient'")
            .as_one(
                "in Poland",
                "abroad at Polish consulate"
            )

        // Confidential field: Track if user seems unfamiliar with process
        .field("needs_guidance")
            .desc("User asks clarifying questions or seems unfamiliar with Polish passport procedures")
            .confidential()
            .as_bool()

        // Conclusion: Provide next steps assessment
        .field("recommended_next_steps")
            .desc("Based on the application choices, provide a comprehensive summary of recommended next steps")
            .conclude()
            .hint("Consider the child's age, application method, and locations chosen")
            .hint("Include specific guidance about required documents for the age range")
            .as_str()

        .build();
}

async function runInteractive(interview: Interview): Promise<boolean> {
    /**Run the wizard interactively.**/
    const threadId = `passport-wizard-${process.pid}`;
    console.log(`Starting Polish Passport Application Wizard (thread: ${threadId})`);
    console.log("=".repeat(70));
    console.log("Welcome to the Polish Passport Application Assistant");
    console.log("This wizard will help you understand the process for applying");
    console.log("for a child's passport in Poland.");
    console.log("=".repeat(70));

    const interviewer = new Interviewer(interview, { threadId });

    let userInput: string | undefined = undefined;
    while (!interview._done) {
        const message = await interviewer.go(userInput);

        if (message) {
            console.log(`\nAssistant: ${message}`);
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
                console.log("\n[Wizard ended]");
                break;
            }
        }
    }

    return interview._done;
}

async function runAutomated(interview: Interview): Promise<boolean> {
    /**Run with prefab inputs for demonstration.**/
    const prefabInputs = [
        // Response 1: Child age
        "My daughter just turned 4, so she's under 5 years old",

        // Response 2: Application method
        "I'd like to do it online if possible. Is that easy to do? " +
        "I'm not very familiar with the Polish system.",

        // Response 3: Application location
        "We're currently living in Poland, in Warsaw, so I'd like to submit it here in Poland.",

        // Response 4: Pickup location
        "And we'll pick it up in Poland as well, since we'll be here for at least the next year."
    ];

    const threadId = `passport-demo-${process.pid}`;
    console.log(`Running automated demo (thread: ${threadId})`);
    console.log("=".repeat(70));
    console.log("Polish Passport Application Wizard - Automated Demo");
    console.log("=".repeat(70));

    const interviewer = new Interviewer(interview, { threadId });

    const inputIter = prefabInputs[Symbol.iterator]();
    let userInput: string | undefined = undefined;

    while (!interview._done) {
        const message = await interviewer.go(userInput);

        if (message) {
            console.log(`\nAssistant: ${message}`);
        }

        if (!interview._done) {
            const next = inputIter.next();
            if (next.done) {
                console.log("\n[Demo inputs exhausted]");
                break;
            }
            userInput = next.value;
            console.log(`\nYou: ${userInput}`);

            // Add small delay for readability
            await new Promise(resolve => setTimeout(resolve, 800));
        }
    }

    return interview._done;
}

function displayResults(interview: Interview): void {
    /**Display the wizard results and guidance.**/
    console.log("\n" + "=".repeat(70));
    console.log("PASSPORT APPLICATION SUMMARY");
    console.log("-".repeat(70));

    // Get the raw field data
    const childAgeField = (interview as any).child_age_range;
    const appMethodField = (interview as any).application_method;
    const appLocationField = (interview as any).application_location;
    const pickupLocationField = (interview as any).pickup_location;

    // Display collected information
    if (childAgeField) {
        console.log(`\nChild Age Range: ${childAgeField}`);
    }

    if (appMethodField) {
        console.log(`Application Method: ${appMethodField}`);
    }

    if (appLocationField) {
        console.log(`Application Location: ${appLocationField}`);
    }

    if (pickupLocationField) {
        console.log(`Pickup Location: ${pickupLocationField}`);
    }

    // Check if user needed extra guidance (access roles as object, not Map)
    const bobRole = interview._chatfield.roles['bob'];
    if (bobRole?.possible_traits?.['unfamiliar-with-polish']?.active) {
        console.log("\n[Note: Additional guidance was provided for Polish procedures]");
    }
    if (bobRole?.possible_traits?.['experienced-applicant']?.active) {
        console.log("\n[Note: User has previous experience with passport applications]");
    }

    // Display recommended next steps
    const nextStepsField = (interview as any).recommended_next_steps;
    if (nextStepsField) {
        console.log("\n" + "-".repeat(70));
        console.log("RECOMMENDED NEXT STEPS:");
        console.log("-".repeat(70));
        console.log(nextStepsField);
    }

    // Add contextual guidance based on selections
    console.log("\n" + "-".repeat(70));
    console.log("IMPORTANT INFORMATION:");
    console.log("-".repeat(70));

    const ageRange = childAgeField;
    if (ageRange === "up to 5 years old") {
        console.log("\n📋 Required Documents for Children Under 5:");
        console.log("   • Child's birth certificate");
        console.log("   • Parent/guardian ID");
        console.log("   • Recent photograph (35×45 mm, light background)");
        console.log("   • Both parents must consent (or legal custody documents)");
    } else if (ageRange === "5 to 12 years old") {
        console.log("\n📋 Required Documents for Children 5-12 Years:");
        console.log("   • Child's birth certificate");
        console.log("   • Parent/guardian ID");
        console.log("   • Recent photograph (35×45 mm, light background)");
        console.log("   • Child must be present for biometric data");
        console.log("   • Both parents must consent (or legal custody documents)");
    } else if (ageRange === "12 to 18 years old (until completion of 18th year)") {
        console.log("\n📋 Required Documents for Children 12-18 Years:");
        console.log("   • Child's birth certificate or ID");
        console.log("   • Recent photograph (35×45 mm, light background)");
        console.log("   • Child must be present for biometric data and signature");
        console.log("   • Parental consent required");
    }

    const method = appMethodField;
    if (method === "online through internet") {
        console.log("\n🌐 Online Application Process:");
        console.log("   • Visit: https://paszport.gov.pl");
        console.log("   • You'll need: Trusted Profile (Profil Zaufany) or e-ID");
        console.log("   • Complete form online, then visit office for biometrics");
        console.log("   • Processing time: ~30 days");
    } else if (method === "in-office at passport office") {
        console.log("\n🏢 In-Office Application Process:");
        console.log("   • Find your local passport office (urząd paszportowy)");
        console.log("   • Bring all required documents");
        console.log("   • Biometric data collected during visit");
        console.log("   • Processing time: ~30 days");
    }

    console.log("\n💰 Fees:");
    console.log("   • Standard passport (10 years): ~140 PLN");
    console.log("   • Express processing available for additional fee");

    console.log("\n📞 Need Help?");
    console.log("   • Passport Information Hotline: +48 22 601 55 55");
    console.log("   • Website: https://www.gov.pl/paszport");
    console.log("   • Email: info@paszport.gov.pl");

    console.log("\n" + "=".repeat(70));
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
        console.error("Please set your OpenAI API key in .env.secret file");
        process.exit(1);
    }

    // Create and run the wizard
    const interview = createPassportWizard();

    let completed: boolean;
    if (values.auto) {
        completed = await runAutomated(interview);
    } else {
        completed = await runInteractive(interview);
    }

    // Display results (even if not fully completed in auto mode)
    if (completed || values.auto) {
        displayResults(interview);
    } else {
        console.log("\n[Wizard not completed]");
    }

    process.exit(0);
}

// Run main function
main().catch((error) => {
    console.error('Error:', error);
    process.exit(1);
});

// Export for testing
export { createPassportWizard, displayResults };
