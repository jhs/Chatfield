#!/usr/bin/env -S npx tsx
/**
 * Demo script that generates the CC-guidance prompt (Claude Code Form Completion Assistant)
 * and prints it to stdout with colored debug visualization.
 *
 * This prompt guides Claude Code to:
 * 1. Inspect web forms using Playwright MCP
 * 2. Generate Chatfield interview definitions
 * 3. Collect data through conversation
 * 4. Populate and submit forms safely with phase-based approval
 */

import { TemplateEngine } from '../chatfield/template-engine';
import { Interviewer } from '../chatfield/interviewer';
import * as path from 'path';

// Create template engine instance pointing to project Prompts directory
const promptsDir = path.join(__dirname, '../../Prompts');
const templateEngine = new TemplateEngine(promptsDir);

// Render the CC-guidance prompt
const ccGuidancePrompt = templateEngine.render('CC-guidance', {});

// Use Interviewer's debug prompt visualization for colored output
const debugView = Interviewer.debugPrompt(ccGuidancePrompt);

console.log(debugView);
console.log('\n' + '='.repeat(80));
console.log('CC-GUIDANCE PROMPT GENERATED');
console.log('='.repeat(80));
console.log(`\nPrompt length: ${ccGuidancePrompt.length} characters`);
console.log(`Template location: ${promptsDir}/CC-guidance.hbs.txt`);
console.log('\nThis prompt includes:');
console.log('  - Phase 1: GATHER (Read-Only Form Inspection)');
console.log('  - Phase 2: POPULATE (Fill Form Fields)');
console.log('  - User Submission (User reviews and submits)');
console.log('\nPartials used:');
console.log('  - playwright-input.hbs.txt  (Phase 1 field extraction)');
console.log('  - playwright-output.hbs.txt (Phase 2 population)');
