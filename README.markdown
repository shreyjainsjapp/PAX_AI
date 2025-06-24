# Work Breakdown Structure (WBS) Documentation for EmotionAware Chatbot POC

## Project Overview
The EmotionAware Chatbot Proof of Concept (POC) is developed using OpenAI's Large Language Model (LLM) integrated with a Streamlit-based user interface in Visual Studio Code (VSCode). This 8-day project, with each day allocated 8 hours of work, aims to create a functional chatbot capable of detecting user emotions, maintaining conversation context, generating therapist-like responses, and providing visualizations of emotional trends. The project is scheduled for completion by July 1, 2025, with a demo planned for July 4, 2025. Deployment on Microsoft Azure will involve a DevOps resource for the final 2-3 days, requiring Azure access.

This Work Breakdown Structure (WBS) outlines the tasks, deliverables, and timeline to ensure structured execution and timely delivery of the POC.

---

## WBS Breakdown

### Day 1: Project Setup & Core Infrastructure
**Objective**: Establish the foundational components of the chatbot application.
- **Tasks**:
  - Create a basic Streamlit application skeleton to define the UI structure.
  - Configure and test the connection to the OpenAI API for LLM integration.
  - Define a list of emotions (e.g., happy, sad, angry) and map them to corresponding colors for visualization.
  - Develop an emotion detection function leveraging OpenAI API to analyze user input.
- **Deliverables**:
  - Functional Streamlit app skeleton.
  - OpenAI API integration with successful test calls.
  - EMOTIONS list and color mapping dictionary.
  - Initial emotion detection function.
- **Duration**: 8 hours

### Day 2: Emotion Detection System
**Objective**: Build and test the core emotion detection and scoring mechanism.
- **Tasks**:
  - Design an Emotional Quotient (EQ) scoring system with weighted values for different emotions.
  - Implement the `update_eq_score()` function to dynamically adjust EQ scores based on detected emotions.
  - Test emotion detection accuracy using predefined sample inputs.
  - Document the logic and methodology behind emotion detection and EQ scoring.
- **Deliverables**:
  - EQ scoring system with weights.
  - Functional `update_eq_score()` function.
  - Test report for emotion detection.
  - Documentation of emotion detection logic.
- **Duration**: 8 hours

### Day 3: Memory & Context System
**Objective**: Enable the chatbot to maintain and utilize conversation history.
- **Tasks**:
  - Design a storage system for conversation history (e.g., in-memory or file-based).
  - Implement the `remember_everything()` function to store and retrieve conversation data.
  - Develop a mechanism to aggregate conversation context for coherent responses.
  - Test memory persistence across multiple sessions.
  - Add timestamp functionality to messages for tracking conversation flow.
- **Deliverables**:
  - Conversation history storage system.
  - Functional `remember_everything()` function.
  - Context aggregation logic.
  - Test report for memory persistence.
  - Timestamped message functionality.
- **Duration**: 8 hours

### Day 4: Response Generation System
**Objective**: Create a robust system for generating context-aware, therapist-like responses.
- **Tasks**:
  - Develop the `generate_response()` function to produce responses using OpenAI LLM.
  - Incorporate full conversation history into response generation for context continuity.
  - Design a therapist-like response template to ensure empathetic and supportive tone.
  - Embed detected emotion context into responses for personalization.
  - Test response quality across various emotional scenarios.
  - Implement response length control to optimize user experience.
  - Add fallback responses to handle API errors or unexpected inputs.
- **Deliverables**:
  - Functional `generate_response()` function.
  - Therapist-like response template.
  - Emotion-contextualized responses.
  - Test report for response quality.
  - Response length control mechanism.
  - Fallback response system.
- **Duration**: 8 hours

### Day 5: Visualization & Analytics
**Objective**: Provide visual insights into user emotions and EQ trends.
- **Tasks**:
  - Implement tracking of emotion history over time.
  - Develop a display for EQ score progress (e.g., line chart or progress bar).
  - Create a dataframe to store and analyze emotion frequency.
  - Optimize visualization performance for smooth rendering in Streamlit.
- **Deliverables**:
  - Emotion history tracking system.
  - EQ score progress visualization.
  - Emotion frequency dataframe.
  - Optimized visualization components.
- **Duration**: 8 hours

### Day 6: UI/UX Enhancement
**Objective**: Enhance the user interface for better engagement and usability.
- **Tasks**:
  - Design chat message bubbles for a conversational look and feel.
  - Implement emotion-based emoji display to reflect user sentiment.
  - Add avatars for the user and chatbot to personalize interactions.
  - Incorporate responsive design elements for cross-device compatibility.
  - Add loading spinners to indicate processing during API calls.
  - Create help/instruction tooltips to guide users.
- **Deliverables**:
  - Styled chat message bubbles.
  - Emotion emoji display system.
  - User and bot avatars.
  - Responsive UI design.
  - Loading spinners.
  - Help/instruction tooltips.
- **Duration**: 8 hours

### Day 7: Testing & Debugging
**Objective**: Ensure the application is robust and reliable.
- **Tasks**:
  - Test edge cases for emotion detection (e.g., ambiguous or mixed emotions).
  - Validate EQ scoring calculations for accuracy.
  - Verify memory persistence under various scenarios.
  - Test conversation flow for continuity and coherence.
  - Validate visualization accuracy against stored data.
  - Perform stress testing with long conversations to identify performance bottlenecks.
- **Deliverables**:
  - Test report for emotion detection edge cases.
  - Validated EQ scoring results.
  - Memory persistence test report.
  - Conversation flow test report.
  - Visualization accuracy report.
  - Stress test results.
- **Duration**: 8 hours

### Day 8: Deployment Prep & Documentation
**Objective**: Prepare the application for deployment and finalize documentation.
- **Tasks**:
  - Generate a `requirements.txt` file listing all dependencies.
  - Test deployment on Streamlit Cloud as a preliminary step.
  - Perform a final quality assurance (QA) check on all features.
  - Create comprehensive project documentation, including setup, usage, and maintenance instructions.
  - Coordinate with DevOps resource for Azure deployment planning (requires Azure access).
- **Deliverables**:
  - `requirements.txt` file.
  - Successful Streamlit Cloud deployment test.
  - Final QA report.
  - Project documentation.
  - Azure deployment plan outline.
- **Duration**: 8 hours

---

## Resource Allocation
- **Development Team**: One developer responsible for all tasks from Day 1 to Day 8, focusing on coding, testing, and documentation.
- **DevOps Resource**: One DevOps engineer allocated for the last 2-3 days (Days 6-8) to assist with Azure deployment setup and configuration. Azure access will be required for this resource.
- **Code Delivery**: All related code files will be provided by the developer by end of day (EOD) on July 1, 2025.

---

## Timeline & Milestones
- **Start Date**: June 24, 2025 (assuming 8 consecutive working days).
- **End Date**: July 1, 2025.
- **Key Milestones**:
  - Day 1 (June 24): Core infrastructure and emotion detection foundation completed.
  - Day 4 (June 27): Response generation system fully implemented.
  - Day 6 (June 29): UI/UX enhancements finalized.
  - Day 8 (July 1): Application ready for deployment, with documentation completed.
  - Demo Date: July 4, 2025.

---

## Assumptions & Dependencies
- **Assumptions**:
  - All required tools (VSCode, Streamlit, OpenAI API access) are available and configured by Day 1.
  - Azure access will be granted to the DevOps resource by Day 6 for deployment activities.
  - No significant changes to requirements during the 8-day period.
- **Dependencies**:
  - OpenAI API availability and performance for emotion detection and response generation.
  - Azure infrastructure readiness for deployment.
  - Timely provision of Azure credentials for the DevOps resource.

---

## Risks & Mitigation
- **Risk**: Delays in OpenAI API integration due to rate limits or authentication issues.
  - **Mitigation**: Test API connectivity early on Day 1 and maintain fallback responses for API failures.
- **Risk**: Azure deployment challenges due to limited access or configuration issues.
  - **Mitigation**: Engage DevOps resource early (Day 6) and test deployment on Streamlit Cloud as a backup.
- **Risk**: Edge cases in emotion detection affecting response quality.
  - **Mitigation**: Allocate sufficient time on Day 7 for rigorous testing and debugging.

---

## Conclusion
This WBS provides a structured approach to developing the EmotionAware Chatbot POC within the 8-day timeline. By breaking down tasks into daily deliverables, allocating resources effectively, and addressing potential risks, the project is positioned for successful completion by July 1, 2025, with a fully functional demo ready for July 4, 2025. The involvement of a DevOps resource for Azure deployment ensures a smooth transition to production, pending timely Azure access.



## Set Up :

1. python -m venv venv
2. .\venv\Scripts\Activate.ps1

# if an error occurs in step 2 :

3. Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
4. Repeat step 2
5. pip install -r requirements.txt
6. python app9.py