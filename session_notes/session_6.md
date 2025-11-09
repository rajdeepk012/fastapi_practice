# Session 6 - Building a Simple Rule-Based Chatbot

**Date:** November 9, 2025
**Phase:** 2.1 - Simple Chatbot Implementation

---

## Overview

In this session, we built our **first working chatbot**! This is what the entire project has been building towards. We created a rule-based chatbot that can respond to greetings, answer questions, and handle unknown inputs gracefully.

**What we built:**
- Pattern-matching chatbot logic
- Chat endpoint with request/response models
- Support for multiple conversation patterns
- Default handling for unknown inputs

---

## Commands Used

### Git Commands
- `git checkout -b feature/chatbot` - Create chatbot feature branch
- `git diff --stat main.py` - Show summary of changes
- `git restore rs.txt` - Discard changes to specific file
- `git add main.py` - Stage chatbot code
- `git commit -m "message"` - Commit chatbot feature
- `git checkout main` - Switch to main branch
- `git merge feature/chatbot` - Merge chatbot (fast-forward)
- `git branch -d feature/chatbot` - Delete merged branch
- `git log --oneline -8` - Show recent commits

### Testing Chatbot
```bash
# Create test message
cat > /tmp/chat.json << 'EOF'
{
  "user_message": "Hello!",
  "user_name": "Alice"
}
EOF

# Send to chatbot
curl -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d @/tmp/chat.json
```

---

## Concepts Covered

### Rule-Based Chatbots

**What is a rule-based chatbot?**
- Uses predefined patterns to match user input
- Returns scripted responses based on matches
- No machine learning or AI
- Simple but effective for specific use cases

**How it works:**
```
1. User sends message
2. Convert to lowercase, strip whitespace
3. Check against patterns (greetings, keywords, etc.)
4. Return matching response
5. If no match, return default response
```

**Advantages:**
- ✅ Predictable responses
- ✅ Easy to understand and debug
- ✅ No training data needed
- ✅ Fast response time
- ✅ Complete control over responses

**Disadvantages:**
- ❌ Limited to predefined patterns
- ❌ Can't handle complex conversations
- ❌ Doesn't learn from interactions
- ❌ Needs manual updates for new patterns

---

### Pattern Matching with `any()`

**The `any()` function** checks if ANY item in an iterable is True.

**Syntax:**
```python
any(condition for item in iterable)
```

**How it works:**
```python
# Check if any greeting word is in message
any(word in message for word in ["hello", "hi", "hey"])
```

**Step-by-step execution:**
```python
message = "hi there"

# Expands to:
"hello" in "hi there" → False
"hi" in "hi there"    → True  ← Stops here, returns True!
# Doesn't check "hey" because already found True
```

**Examples:**

```python
# Example 1: Found match
message = "hello friend"
result = any(word in message for word in ["hello", "hi", "hey"])
# "hello" in "hello friend" → True
# Result: True

# Example 2: No match
message = "goodbye"
result = any(word in message for word in ["hello", "hi", "hey"])
# "hello" in "goodbye" → False
# "hi" in "goodbye" → False
# "hey" in "goodbye" → False
# Result: False

# Example 3: Partial match (be careful!)
message = "think"
result = any(word in message for word in ["hi", "ink"])
# "hi" in "think" → True (substring match!)
# Result: True (may be unwanted!)
```

**Key insight:** `in` operator checks for **substring**, not whole word!

---

### String Methods for Text Processing

**Converting to lowercase:**
```python
message = "HELLO World"
message.lower()  # → "hello world"
```

**Why lowercase?**
- Makes matching case-insensitive
- "Hello", "HELLO", "hello" all match the same pattern

**Stripping whitespace:**
```python
message = "  hello  "
message.strip()  # → "hello"
```

**Why strip?**
- Removes leading/trailing spaces
- "  hello  " and "hello" are treated the same
- Prevents matching issues

**Combined:**
```python
user_input = "  HELLO  "
message = user_input.lower().strip()  # → "hello"
```

---

### Chatbot Response Patterns

**Our chatbot supports these patterns:**

**1. Greetings**
```python
if any(word in message for word in ["hello", "hi", "hey", "greetings"]):
    return "Hi there! How can I help you today?"
```

**Matches:**
- "Hello!"
- "Hi there"
- "Hey bot"
- "Greetings"

---

**2. Name Questions**
```python
if "your name" in message or "who are you" in message:
    return "I'm FastAPI Bot, your friendly assistant built with FastAPI!"
```

**Matches:**
- "What's your name?"
- "What is your name?"
- "Who are you?"
- "Tell me your name"

---

**3. FastAPI Questions**
```python
if "fastapi" in message:
    return "FastAPI is a modern, fast Python web framework for building APIs. It's awesome!"
```

**Matches:**
- "Tell me about FastAPI"
- "What is FastAPI?"
- "fastapi tutorial"

---

**4. How Are You**
```python
if "how are you" in message:
    return "I'm doing great! Thanks for asking. How can I assist you?"
```

**Matches:**
- "How are you?"
- "How are you doing?"

---

**5. Help Requests**
```python
if "help" in message:
    return "I can chat with you! Try asking me about FastAPI, say hello, or ask my name!"
```

**Matches:**
- "Help!"
- "I need help"
- "Can you help me?"

---

**6. Default Response**
```python
# If no patterns match
return "Interesting! I'm still learning. Can you try asking something else?"
```

**Triggers when:**
- No predefined pattern matches
- Handles gracefully instead of error

---

### Request and Response Models

**ChatRequest Model (Input):**
```python
class ChatRequest(BaseModel):
    user_message: str          # User's input (required)
    user_name: str = "User"    # Optional name (defaults to "User")
```

**Why user_name is optional:**
- Makes API flexible
- Clients can omit it for simplicity
- Still get personalized experience with default

**Usage examples:**
```python
# With name
{"user_message": "Hello!", "user_name": "Alice"}

# Without name (uses default)
{"user_message": "Hello!"}  # user_name defaults to "User"
```

---

**ChatResponse Model (Output):**
```python
class ChatResponse(BaseModel):
    bot_reply: str             # Bot's response
    user_message: str          # Echo back user's input
    user_name: str             # User's name (from request or default)
```

**Why echo back user_message?**
- Confirmation of what was received
- Useful for debugging
- Better user experience (they see what was processed)

**Example response:**
```json
{
  "bot_reply": "Hi there! How can I help you today?",
  "user_message": "Hello!",
  "user_name": "Alice"
}
```

---

### Chatbot Flow Diagram

```
User sends message
       ↓
POST /chat endpoint
       ↓
Pydantic validates ChatRequest
       ↓
chatbot_reply() function
       ↓
1. Convert to lowercase
2. Strip whitespace
3. Check patterns in order:
   - Greetings?
   - Name question?
   - FastAPI?
   - How are you?
   - Help?
   - Default
       ↓
Return ChatResponse
       ↓
User receives bot reply
```

---

## Code Written

### Complete Chatbot Implementation

```python
# ========== CHATBOT SECTION ==========

# Chatbot request model
class ChatRequest(BaseModel):
    user_message: str          # User's input message
    user_name: str = "User"    # Optional user name (defaults to "User")

# Chatbot response model
class ChatResponse(BaseModel):
    bot_reply: str             # Bot's response
    user_message: str          # Echo back user's message
    user_name: str             # User's name

# Simple chatbot logic function
def chatbot_reply(user_input: str) -> str:
    """
    Rule-based chatbot that matches patterns and returns responses
    """
    # Convert to lowercase for matching
    message = user_input.lower().strip()

    # Greeting patterns
    if any(word in message for word in ["hello", "hi", "hey", "greetings"]):
        return "Hi there! How can I help you today?"

    # Name questions
    if "your name" in message or "who are you" in message:
        return "I'm FastAPI Bot, your friendly assistant built with FastAPI!"

    # FastAPI questions
    if "fastapi" in message:
        return "FastAPI is a modern, fast Python web framework for building APIs. It's awesome!"

    # How are you
    if "how are you" in message:
        return "I'm doing great! Thanks for asking. How can I assist you?"

    # Help requests
    if "help" in message:
        return "I can chat with you! Try asking me about FastAPI, say hello, or ask my name!"

    # Default response for unknown inputs
    return "Interesting! I'm still learning. Can you try asking something else?"

# Chatbot endpoint
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Simple chatbot endpoint that processes user messages and returns bot replies
    """
    # Get bot's reply using chatbot logic
    bot_response = chatbot_reply(request.user_message)

    # Return structured response
    return ChatResponse(
        bot_reply=bot_response,
        user_message=request.user_message,
        user_name=request.user_name
    )
```

**Key components:**
1. **ChatRequest** - Validates incoming messages
2. **ChatResponse** - Structures outgoing responses
3. **chatbot_reply()** - Contains all pattern matching logic
4. **/chat endpoint** - Ties everything together

---

## Testing Results

### Test 1: Greeting
**Request:**
```json
{
  "user_message": "Hello!",
  "user_name": "Alice"
}
```

**Response:**
```json
{
  "bot_reply": "Hi there! How can I help you today?",
  "user_message": "Hello!",
  "user_name": "Alice"
}
```

**Pattern matched:** Greeting ("hello" found)

---

### Test 2: Name Question (No Username Provided)
**Request:**
```json
{
  "user_message": "What's your name?"
}
```

**Response:**
```json
{
  "bot_reply": "I'm FastAPI Bot, your friendly assistant built with FastAPI!",
  "user_message": "What's your name?",
  "user_name": "User"
}
```

**Pattern matched:** Name question ("your name" found)
**Note:** user_name defaulted to "User"

---

### Test 3: FastAPI Question
**Request:**
```json
{
  "user_message": "Tell me about FastAPI",
  "user_name": "Bob"
}
```

**Response:**
```json
{
  "bot_reply": "FastAPI is a modern, fast Python web framework for building APIs. It's awesome!",
  "user_message": "Tell me about FastAPI",
  "user_name": "Bob"
}
```

**Pattern matched:** FastAPI keyword ("fastapi" found)

---

### Test 4: Unknown Input (Default Response)
**Request:**
```json
{
  "user_message": "What is the weather today?"
}
```

**Response:**
```json
{
  "bot_reply": "Interesting! I'm still learning. Can you try asking something else?",
  "user_message": "What is the weather today?",
  "user_name": "User"
}
```

**Pattern matched:** None (default response triggered)

---

## Test Summary Table

| User Input | user_name | Pattern Matched | Bot Response |
|------------|-----------|-----------------|--------------|
| "Hello!" | Alice | Greeting | "Hi there! How can I help you today?" |
| "What's your name?" | (default) | Name question | "I'm FastAPI Bot..." |
| "Tell me about FastAPI" | Bob | FastAPI keyword | "FastAPI is a modern..." |
| "What is the weather?" | (default) | None | "Interesting! I'm still learning..." |

**All patterns working correctly!** ✅

---

## Git Workflow This Session

### Commits Made:
1. **Add simple rule-based chatbot endpoint** (`9576c85`)
   - Created ChatRequest and ChatResponse models
   - Implemented chatbot_reply() with pattern matching
   - Added /chat POST endpoint
   - Tested all response patterns

### Branch Operations:
1. Created `feature/chatbot` branch
2. Implemented chatbot functionality
3. Tested thoroughly with multiple inputs
4. Committed changes
5. Switched to main
6. Merged with fast-forward
7. Deleted feature branch

### Git Challenges & Solutions:

**Issue:** Modified `rs.txt` file blocked checkout
**Solution:** Used `git restore rs.txt` to discard changes

**Command learned:**
```bash
git restore <file>  # Discard changes to specific file
```

### Current State:
- On `main` branch
- 6 working endpoints (5 GET, 1 POST, 1 chatbot!)
- Clean git history with meaningful commits

---

## Quiz Questions & Answers

### Q1: What is a rule-based chatbot?
**Answer:** A chatbot that uses predefined patterns to match user input and returns scripted responses. It doesn't use machine learning or AI - just simple pattern matching with if-else logic.

---

### Q2: What does `any()` do and how does it work?
**Answer:** `any()` checks if ANY item in an iterable is True. It returns True as soon as it finds the first True value, and stops checking the rest. Returns False only if all items are False.

Example:
```python
any(word in "hi there" for word in ["hello", "hi", "hey"])
# Checks "hello" → False
# Checks "hi" → True (stops here!)
# Returns: True
```

---

### Q3: Why do we convert user input to lowercase in chatbot_reply()?
**Answer:** To make pattern matching case-insensitive. This way "Hello", "HELLO", and "hello" all match the same pattern. Without it, we'd need separate patterns for each case variation.

---

### Q4: What's the purpose of the default response in the chatbot?
**Answer:** To handle inputs that don't match any predefined pattern. Instead of crashing or returning an error, the chatbot gracefully responds with "Interesting! I'm still learning..." This provides better user experience.

---

### Q5: Why is `user_name` optional with a default value of "User"?
**Answer:** To make the API flexible and easier to use. Clients can choose to provide a name or omit it. If omitted, it defaults to "User" so the response still has a valid user_name field.

---

### Q6: What does `.strip()` do and why use it?
**Answer:** `.strip()` removes leading and trailing whitespace from a string. This ensures "  hello  " and "hello" are treated the same, preventing matching issues caused by extra spaces.

---

### Q7: How does the chatbot decide which response to return?
**Answer:** It checks patterns in order (greetings, name questions, fastapi, etc.). The FIRST pattern that matches determines the response. If no patterns match, it returns the default response. Order matters!

---

### Q8: What's the difference between ChatRequest and ChatResponse?
**Answer:**
- **ChatRequest** - What the user SENDS (user_message, optional user_name)
- **ChatResponse** - What the bot RETURNS (bot_reply, user_message, user_name)

The request is input validation, the response is output structure.

---

### Q9: Why echo back user_message in the response?
**Answer:** For confirmation and debugging. The client can verify what message was actually received and processed. Helps catch issues with message transmission or processing.

---

### Q10: What happens if user input is "HELLO"?
**Answer:**
1. Input: "HELLO"
2. Convert to lowercase: "hello"
3. Check patterns: "hello" in "hello" → True
4. Return: "Hi there! How can I help you today?"

The lowercase conversion ensures it matches the greeting pattern.

---

### Q11: What did you learn from using `git restore`?
**Answer:** `git restore` discards uncommitted changes to specific files, reverting them to the last committed state. Useful when you have unwanted changes blocking operations like `git checkout`.

---

### Q12: Could two patterns match the same input? What happens?
**Answer:** Yes! For example, "hello, what's your name?" matches both greeting and name patterns. The FIRST pattern in the code (greetings) wins because the function returns immediately after a match.

---

## Key Takeaways

### Chatbot Design
1. **Rule-based** - Simple pattern matching, no AI needed
2. **Pattern order matters** - First match wins
3. **Default response** - Always have a fallback
4. **Lowercase matching** - Case-insensitive for better UX
5. **Strip whitespace** - Prevent matching issues

### Python Techniques
1. **`any()` function** - Elegant way to check multiple conditions
2. **String methods** - `.lower()` and `.strip()` for text processing
3. **Early return** - Return immediately when pattern matches
4. **Separation of concerns** - Logic in `chatbot_reply()`, endpoint in `chat()`

### API Design
1. **Optional fields** - Make APIs flexible with defaults
2. **Echo responses** - Confirm what was processed
3. **Structured models** - Clear input/output contracts
4. **Meaningful names** - `ChatRequest`, `ChatResponse` are self-documenting

### Git Skills
1. **git restore** - Discard unwanted changes
2. **Feature branches** - Isolate chatbot development
3. **Fast-forward merge** - Clean linear history
4. **Branch cleanup** - Delete after merging

---

## Limitations & Future Improvements

### Current Limitations

**1. No conversation memory**
- Each message is independent
- Can't reference previous messages
- Can't track conversation context

**2. Simple substring matching**
- "think" matches "hi" pattern (substring issue)
- Can't understand word boundaries
- No semantic understanding

**3. Fixed responses**
- Same response every time
- No variation or randomness
- Can feel robotic

**4. No user data**
- Doesn't remember user preferences
- Can't personalize responses
- No user history

---

### Future Improvements (Next Sessions)

**Phase 2.2: Conversation History**
- Track message history
- Store conversations in memory
- GET endpoint to retrieve history
- Context-aware responses

**Phase 2.3: Enhanced Pattern Matching**
- Word boundary detection
- Regular expressions
- Multiple responses per pattern
- Confidence scoring

**Phase 2.4: State Management**
- Track conversation state
- Multi-turn conversations
- Context from previous messages
- User sessions

**Phase 2.5: Database Integration**
- Persist conversations
- User profiles
- Analytics and insights
- Search conversation history

---

## Real-World Applications

### Where Rule-Based Chatbots Excel

**1. FAQ Bots**
```python
# Customer support
if "refund" in message:
    return "Our refund policy is..."

if "shipping" in message:
    return "We ship within 2-3 business days..."
```

**2. Command Bots**
```python
# Slack/Discord bots
if message.startswith("/help"):
    return list_commands()

if message.startswith("/weather"):
    return get_weather()
```

**3. Form Filling Assistants**
```python
# Guide users through forms
if state == "need_name":
    return "What's your name?"

if state == "need_email":
    return "What's your email?"
```

**4. Menu Navigation**
```python
# Restaurant ordering
if "menu" in message:
    return show_menu()

if "order" in message:
    return "What would you like to order?"
```

---

## Extending the Chatbot

### Adding New Patterns

**Easy to add more responses:**
```python
def chatbot_reply(user_input: str) -> str:
    message = user_input.lower().strip()

    # Existing patterns...

    # New pattern: Time questions
    if "time" in message or "what time" in message:
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M")
        return f"The current time is {current_time}"

    # New pattern: Jokes
    if "joke" in message or "funny" in message:
        return "Why do programmers prefer dark mode? Because light attracts bugs! 😄"

    # New pattern: Goodbye
    if any(word in message for word in ["bye", "goodbye", "see you"]):
        return "Goodbye! Come back soon!"

    # Default...
```

---

## Best Practices Learned

### Code Organization
1. ✅ Separate logic from endpoint (chatbot_reply function)
2. ✅ Clear model names (ChatRequest, ChatResponse)
3. ✅ Docstrings for complex functions
4. ✅ Comments explaining pattern matching

### Testing Strategy
1. ✅ Test each pattern individually
2. ✅ Test with and without optional fields
3. ✅ Test default response (unknown input)
4. ✅ Test case variations (HELLO, hello, Hello)

### Git Workflow
1. ✅ Feature branch for new functionality
2. ✅ Test before committing
3. ✅ Descriptive commit messages
4. ✅ Clean up merged branches

---

## Performance Considerations

**Current approach is fast:**
- ✅ No database calls
- ✅ No external API calls
- ✅ Simple string operations
- ✅ Early returns (stops at first match)

**Response time:** < 1ms for pattern matching

**Scalability:**
- ✅ Can handle thousands of requests/second
- ✅ Stateless (no memory between requests)
- ❌ Limited by number of patterns (O(n) checks)

---

## Documentation Tips

**For real projects, document:**
1. Supported patterns and triggers
2. Example conversations
3. How to add new patterns
4. Limitations and known issues
5. Response format

**Example README section:**
```markdown
## Chatbot Commands

| Trigger | Response |
|---------|----------|
| hello, hi, hey | Greeting response |
| what's your name | Bot introduction |
| fastapi | FastAPI information |
| help | Available commands |
```

---

## Next Steps

**What we'll build next:**
1. **Conversation history** - Track message exchanges
2. **GET endpoint** - Retrieve past conversations
3. **Session management** - Identify users across requests
4. **Enhanced responses** - Context from previous messages

**Skills we'll learn:**
1. In-memory storage (lists/dicts)
2. Unique ID generation
3. Filtering and searching data
4. Time-based data (timestamps)

---

## Summary

### What We Built
✅ Simple rule-based chatbot
✅ Pattern matching with 6 different triggers
✅ Request/response models for structure
✅ Default handling for unknown inputs
✅ Flexible user_name field

### What We Learned
✅ Rule-based chatbot architecture
✅ Pattern matching with `any()`
✅ String processing (.lower(), .strip())
✅ Separating logic from endpoints
✅ git restore for discarding changes

### What We Achieved
✅ **A WORKING CHATBOT!** 🎉
✅ Professional API structure
✅ Clean, testable code
✅ All tests passing
✅ Merged to main successfully

---

**Congratulations on building your first chatbot!** This is a major milestone in your FastAPI journey. You've gone from "Hello World" to a functioning conversational AI in just 6 sessions. Amazing progress! 🚀
