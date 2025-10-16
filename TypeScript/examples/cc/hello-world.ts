/**
 * Hello World Form - Placeholder Interview
 * ==========================================
 *
 * This is a simple placeholder interview used by boilerplate.ts.
 * Replace this import in boilerplate.ts with your actual form model.
 *
 * To create your own form model:
 * 1. Use Playwright MCP to inspect the target web form
 * 2. Create a new file in this directory (e.g., contact-form.ts)
 * 3. Define fields matching the web form
 * 4. Update boilerplate.ts to import your interview instead
 */

import { chatfield } from '../../chatfield/builder';
import { Interview } from '../../chatfield/interview';

export const interview: Interview = chatfield()
    .type("Hello World Form")
    .desc("A simple placeholder interview for demonstration")

    .alice()
        .type("Friendly Assistant")
        .trait("Helpful, patient, and professional")

    .bob()
        .type("Web User")

    .field("name")
        .desc("Your full name")
        .must("include both first and last name")

    .field("_chatfield_ready")
        .desc("Ready to fill the form?")
        .must("be explicit user instruction to proceed, or direct affirmative answer to this question")
        .hint("User approval to end this conversation and proceed to populate the form")
        .hint("Ask this question last")
        .as_bool()

    .build();
