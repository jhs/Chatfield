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
import * as path from 'path';

import { Interviewer } from '../chatfield/interviewer';
import { TemplateEngine } from '../chatfield/template-engine';

// Create template engine instance pointing to project Prompts directory
const promptsDir = path.join(__dirname, '../../Prompts');
const templateEngine = new TemplateEngine(promptsDir);

// Render the CC-guidance prompt
const ccGuidancePrompt = templateEngine.render('CC-guidance', {});

// Use Interviewer's debug prompt visualization for colored output
// const debugView = Interviewer.debugPrompt(ccGuidancePrompt);
const debugView = ccGuidancePrompt;

console.log(debugView);
