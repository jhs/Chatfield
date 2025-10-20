/**
 * Phoenix LiveView Hook for Chatfield Integration
 *
 * This hook integrates Chatfield conversational UI with Phoenix LiveView forms.
 * When the interview completes, it populates the LiveView form fields.
 */

export const ChatfieldHook = {
  mounted() {
    console.log('Chatfield hook mounted');

    // Initialize Chatfield when the standalone module is loaded
    this.initializeChatfield();
  },

  async initializeChatfield() {
    try {
      // Import Chatfield from the served examples (http://127.0.0.1:8080)
      const { chatfield, Interviewer } = await import('http://127.0.0.1:8080/dist/standalone/esm/index.js');

      console.log('Chatfield loaded successfully');

      // Define the blog post interview
      const interview = chatfield()
        .type('Blog Post')

        .alice()
          .type('Blog Writing Assistant')
          .trait('can fill in details for form fields as guided by Bob')

        .bob()
          .type('Blog Writer')
          .trait('name is "Albert Frank Wallace"')

        .field('title')
          .desc('The title of your blog post')
          .as_lang('th')

        .field('body')
          .desc('The main content of your post')
          .as_lang('th')

        .field('category')
          .desc('Post category')
          .hint('One of: Technology, Design, Business, Personal')
          .as_one('Technology', 'Design', 'Business', 'Personal')

        .field('tags')
          .desc('Relevant tags extracted from the post content and conversation')
          .as_set('tags')
          .conclude()

        .build();

      // Configuration for the interviewer
      const config = {
        baseUrl: 'http://127.0.0.1:4000',
        apiKey: 'api-key-TEST',
      };

      // Run the interview
      await this.runChatfieldInterview(interview, config, Interviewer);

    } catch (error) {
      console.error('Failed to load Chatfield:', error);
      this.showError('Failed to load Chatfield. Make sure the examples server is running on port 8080.');
    }
  },

  async runChatfieldInterview(interview, interviewerConfig, Interviewer) {
    // DOM elements
    const messagesDiv = this.el.querySelector('#chatfield-messages');
    const userInput = this.el.querySelector('#chatfield-user-input');
    const sendBtn = this.el.querySelector('#chatfield-send-btn');
    const statusDiv = this.el.querySelector('#chatfield-status');
    const chatfieldContainer = this.el.querySelector('#chatfield-container');

    // State
    let waitingForInput = false;
    let resolveInput = null;

    // Utilities
    const addMessage = (type, text) => {
      const msg = document.createElement('div');
      msg.className = `chatfield-message ${type}`;

      const content = document.createElement('div');
      content.className = 'chatfield-message-content';
      content.textContent = text;

      if (type === 'ai') {
        const label = document.createElement('div');
        label.className = 'chatfield-message-label';
        label.textContent = 'AI';
        msg.appendChild(label);
      }

      msg.appendChild(content);
      messagesDiv.appendChild(msg);
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    };

    const setStatus = (text) => {
      statusDiv.textContent = text;
    };

    const enableInput = () => {
      waitingForInput = true;
      userInput.disabled = false;
      sendBtn.disabled = false;
      userInput.focus();
      setStatus('');
    };

    const disableInput = () => {
      waitingForInput = false;
      userInput.disabled = true;
      sendBtn.disabled = true;
      userInput.value = '';
      setStatus('AI is thinking...');
    };

    const sendMessage = () => {
      if (!waitingForInput || !resolveInput) return;

      const text = userInput.value.trim();
      if (!text) return;

      addMessage('user', text);
      disableInput();

      const callback = resolveInput;
      resolveInput = null;
      callback(text);
    };

    const getUserInput = () => {
      return new Promise((resolve) => {
        resolveInput = resolve;
        enableInput();
      });
    };

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

    // Interview loop
    setStatus('Initializing...');

    const interviewer = new Interviewer(interview, interviewerConfig);
    let userResponse = null;

    while (true) {
      try {
        const msg = await interviewer.go(userResponse);
        addMessage('ai', msg);

        // if (interview._done) {
        if (interview._enough) {
          setStatus('Interview complete! Populating form...');
          this.populateForm(interview);

          // Hide Chatfield UI after completion
          setTimeout(() => {
            chatfieldContainer.style.display = 'none';
          }, 2000);

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
  },

  populateForm(interview) {
    console.log('Populating form with interview data:', interview);

    // Get field values from the interview
    const fields = interview._chatfield.fields;

    // Populate each form field
    for (const [fieldName, fieldData] of Object.entries(fields)) {
      if (!fieldData.value) continue;

      const value = fieldData.value.value || '';

      // Find the corresponding form input
      let inputSelector;

      if (fieldName === 'tags') {
        // Tags: convert set to comma-separated string
        const tagsSet = fieldData.value.as_set_tags || [];
        const tagsString = Array.from(tagsSet).join(', ');
        inputSelector = `#post-form input[name="post[tags]"]`;
        this.setFormValue(inputSelector, tagsString);
      } else if (fieldName === 'title') {
        inputSelector = `#post-form input[name="post[title]"]`;
        this.setFormValue(inputSelector, value);

        // Also populate Thai translation if available
        const titleTh = fieldData.value.as_lang_th;
        if (titleTh) {
          const thSelector = `#post-form input[name="post[title_th]"]`;
          this.setFormValue(thSelector, titleTh);
        }
      } else if (fieldName === 'body') {
        inputSelector = `#post-form textarea[name="post[body]"]`;
        this.setFormValue(inputSelector, value);

        // Also populate Thai translation if available
        const bodyTh = fieldData.value.as_lang_th;
        if (bodyTh) {
          const thSelector = `#post-form textarea[name="post[body_th]"]`;
          this.setFormValue(thSelector, bodyTh);
        }
      } else if (fieldName === 'category') {
        inputSelector = `#post-form select[name="post[category]"]`;
        this.setFormValue(inputSelector, value);
      }
    }

    // Trigger validation by pushing a "validate" event to LiveView
    this.pushEvent('chatfield_complete', {});
  },

  setFormValue(selector, value) {
    const input = document.querySelector(selector);
    if (input) {
      input.value = value;
      // Trigger input event for LiveView to detect the change
      input.dispatchEvent(new Event('input', { bubbles: true }));
      console.log(`Set ${selector} = ${value}`);
    } else {
      console.warn(`Could not find input: ${selector}`);
    }
  },

  showError(message) {
    const container = this.el.querySelector('#chatfield-container');
    container.innerHTML = `
      <div style="padding: 20px; background: #fee; border: 1px solid #fcc; border-radius: 4px; color: #c00;">
        <strong>Error:</strong> ${message}
      </div>
    `;
  }
};
