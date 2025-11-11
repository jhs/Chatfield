/**
 * Tests for the Interviewer class conversation functionality.
 * Mirrors Python's test_interviewer_conversation.py with identical test descriptions.
 */
import * as dotenv from 'dotenv';
import * as path from 'path';

import { chatfield } from '../chatfield/builder';
import { Interviewer } from '../chatfield/interviewer';

// Load environment variables from project root .env file
const projectRoot = path.join(__dirname, '..', '..');
const envFile = path.join(projectRoot, '.env');
dotenv.config({ path: envFile });

describe('InterviewerConversation', () => {
  describe('go method', () => {
    const testFn = process.env.OPENAI_API_KEY ? test : test.skip;

    testFn('starts conversation with greeting', async () => {
      const interview = chatfield().type('SimpleInterview').field('name').desc('Your name').build();
      const interviewer = new Interviewer(interview);

      // Start conversation
      const aiMessage = await interviewer.go(null);

      console.log(
        `---------------\nAI Message:\n${JSON.stringify(aiMessage, null, 2)}\n---------------`,
      );
      expect(aiMessage).toBeDefined();
      expect(typeof aiMessage).toBe('string');
      expect(aiMessage!.length).toBeGreaterThan(0);
    });
  });
});
