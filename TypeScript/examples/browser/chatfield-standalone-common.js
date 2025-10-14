/**
 * Chatfield Standalone Common Utilities
 * ======================================
 *
 * This file contains all the common boilerplate code for running Chatfield
 * interviews in a standalone browser environment. Import this file and use
 * the runChatfieldInterview() function to run any interview definition.
 *
 * Usage:
 * ------
 * 1. Import this file in your HTML:
 *    <script type="module" src="./chatfield-standalone-common.js"></script>
 *
 * 2. Import and use in your script:
 *    import { runChatfieldInterview } from './chatfield-standalone-common.js';
 *
 * 3. Define your interview using chatfield() builder:
 *    const interview = chatfield()
 *      .field('name')
 *      .field('age').asInt()
 *      .build();
 *
 * 4. Configure interviewer options:
 *    const config = {
 *      baseUrl: 'http://127.0.0.1:4000',
 *      apiKey: 'api-key-TEST',
 *      llmId: 'jason'
 *    };
 *
 * 5. Run the interview:
 *    runChatfieldInterview(interview, config);
 *
 * This will automatically handle:
 * - DOM manipulation for messages
 * - User input handling
 * - Interview state management
 * - Result display
 * - Error handling
 */

/**
 * Main function to run a Chatfield interview in the browser
 *
 * @param {Interview} interview - The interview instance created with chatfield().build()
 * @param {Object} interviewerConfig - Configuration for the Interviewer
 * @param {string} [interviewerConfig.baseUrl] - Base URL for the LLM API
 * @param {string} [interviewerConfig.apiKey] - API key for authentication
 * @param {string} [interviewerConfig.llmId] - LLM model identifier
 * @param {Function} [Interviewer] - Interviewer constructor (auto-imported if not provided)
 */
export async function runChatfieldInterview(interview, interviewerConfig, Interviewer) {
  // Auto-import Interviewer if not provided
  if (!Interviewer) {
    const module = await import('../../dist/standalone/esm/index.js');
    Interviewer = module.Interviewer;
  }

  // DOM elements
  const messagesDiv = document.getElementById('messages');
  const userInput = document.getElementById('user-input');
  const sendBtn = document.getElementById('send-btn');
  const statusDiv = document.getElementById('status');

  // State
  let waitingForInput = false;
  let resolveInput = null;

  // Utilities
  function addMessage(type, text) {
    const msg = document.createElement('div');
    msg.className = `message ${type}`;

    const label = document.createElement('div');
    label.className = 'message-label';
    label.textContent = type === 'ai' ? 'AI' : 'You';

    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = text;

    if (type === 'ai') {
      msg.appendChild(label);
      msg.appendChild(content);
    } else {
      msg.appendChild(content);
    }

    messagesDiv.appendChild(msg);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }

  function showResult(interviewInstance) {
    const result = document.createElement('div');
    result.className = 'result';

    // Build HTML table from interview fields
    let tableHTML = '<table class="result-table">';
    tableHTML += '<thead><tr><th>Field</th><th>Value</th></tr></thead>';
    tableHTML += '<tbody>';

    // Get interview type
    const interviewType = interviewInstance._chatfield.type || 'Interview';

    // Iterate through all fields
    for (const [fieldName, fieldData] of Object.entries(interviewInstance._chatfield.fields)) {
      // Check if field has a value
      if (!fieldData.value) {
        tableHTML += `<tr><td class="field-name">${fieldName}</td><td class="field-value">(not set)</td></tr>`;
        continue;
      }

      // Get the main value (nested at fieldData.value.value)
      const mainValue = fieldData.value.value || '(empty)';

      // Add main field row
      tableHTML += `<tr><td class="field-name">${fieldName}</td><td class="field-value">${escapeHtml(mainValue)}</td></tr>`;

      // Add transformation rows - look for properties starting with 'as_'
      for (const [key, value] of Object.entries(fieldData.value)) {
        if (key.startsWith('as_') && key !== 'as_quote') {
          const displayValue = typeof value === 'boolean' ? value.toString() :
                               typeof value === 'number' ? value.toString() :
                               JSON.stringify(value);
          tableHTML += `<tr><td class="transform-name">↳ ${key}</td><td class="transform-value">${escapeHtml(displayValue)}</td></tr>`;
        }
      }
    }

    tableHTML += '</tbody></table>';

    result.innerHTML = `
      <div class="result-title">✓ ${interviewType} Completed</div>
      ${tableHTML}
    `;
    messagesDiv.appendChild(result);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function setStatus(text) {
    statusDiv.textContent = text;
  }

  function enableInput() {
    waitingForInput = true;
    userInput.disabled = false;
    sendBtn.disabled = false;
    userInput.focus();
    setStatus('');
  }

  function disableInput() {
    waitingForInput = false;
    userInput.disabled = true;
    sendBtn.disabled = true;
    userInput.value = '';
    setStatus('AI is thinking...');
  }

  function sendMessage() {
    if (!waitingForInput || !resolveInput) return;

    const text = userInput.value.trim();
    if (!text) return;

    addMessage('user', text);
    disableInput();

    const callback = resolveInput;
    resolveInput = null;
    callback(text);
  }

  // Event handlers
  sendBtn.addEventListener('click', sendMessage);

  userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  userInput.addEventListener('input', () => {
    // Auto-resize textarea
    userInput.style.height = 'auto';
    userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
  });

  // Interview logic
  async function getUserInput() {
    return new Promise((resolve) => {
      resolveInput = resolve;
      enableInput();
    });
  }

  async function runInterview() {
    setStatus('Initializing...');

    const interviewer = new Interviewer(interview, interviewerConfig);

    let userResponse = null;

    while (true) {
      try {
        const msg = await interviewer.go(userResponse);
        addMessage('ai', msg);

        if (interview._done) {
          showResult(interview);
          setStatus('Interview complete!');
          break;
        }

        userResponse = await getUserInput();
      } catch (error) {
        addMessage('ai', `Error: ${error.message}`);
        setStatus('Error occurred');
        enableInput();
        break;
      }
    }
  }

  // Start the interview
  runInterview();
}

/**
 * Default HTML template that can be used with this common file.
 * Copy this into your HTML file and customize as needed.
 */
export const DEFAULT_HTML_TEMPLATE = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chatfield Interactive Example</title>
  <link rel="stylesheet" href="./chatfield-standalone-styles.css">
</head>
<body>
  <div id="app">
    <div id="header">
      <h1>Chatfield Interactive</h1>
      <p>Conversational form demo • Enter to send • Shift+Enter for newline</p>
    </div>
    <div id="messages"></div>
    <div id="input-area">
      <div id="status" class="status"></div>
      <div id="input-container">
        <textarea
          id="user-input"
          rows="1"
          placeholder="Type your response..."
          disabled
        ></textarea>
        <button id="send-btn" disabled>▶</button>
      </div>
    </div>
  </div>

  <script type="module">
    import { chatfield, Interviewer } from '../../dist/standalone/esm/index.js';
    import { runChatfieldInterview } from './chatfield-standalone-common.js';

    // ============================================================
    // CUSTOMIZE THIS SECTION - Define your interview here
    // ============================================================

    const interview = chatfield()
      .type('Your Interview Type')
      .field('fieldName', 'Field description')
      .build();

    const config = {
      baseUrl: 'http://127.0.0.1:4000',
      apiKey: 'api-key-TEST',
      llmId: 'jason'
    };

    // ============================================================
    // END CUSTOMIZATION - Everything else is handled automatically
    // ============================================================

    runChatfieldInterview(interview, config, Interviewer);
  </script>
</body>
</html>
`;
