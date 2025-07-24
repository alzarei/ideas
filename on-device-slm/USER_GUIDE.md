# 👤 User Guide - For Non-Technical Users

Welcome! This guide will help you install and use the On-Device LLM Assistant, even if you're not technical. Everything runs on your computer - no internet required for chatting!

## 🎯 What Is This?

This is a **private AI chat assistant** that runs entirely on your computer. Think of it like ChatGPT, but:
- ✅ **Completely private** - No data leaves your computer
- ✅ **Works offline** - No internet needed once set up
- ✅ **Multiple AI personalities** - Switch between different AI models
- ✅ **Free to use** - No subscriptions or API costs
- ✅ **Conversation memory** - Remembers your chat history

## 📥 Installation (One-Time Setup)

### Step 1: Install Required Software
You need these 3 programs installed first (like installing any other software):

1. **Python** - The "engine" that runs the AI
   - Go to: https://python.org/downloads/
   - Click the big "Download Python" button
   - Run the installer (check "Add to PATH" if asked)

2. **Node.js** - Builds the web interface
   - Go to: https://nodejs.org/
   - Click "Download for Windows/Mac" 
   - Run the installer

3. **Ollama** - Downloads and manages AI models
   - Go to: https://ollama.ai/download
   - Download for your operating system
   - Run the installer

### Step 2: Get the Project
- Download the project folder from your developer/GitHub
- Or get it as a ZIP file and extract it somewhere easy to find

### Step 3: Automatic Setup
1. **Open the project folder** you downloaded
2. **Windows**: Double-click on `setup.py`
   **Mac**: Right-click on `setup.py` → "Open with" → "Python Launcher"
3. **Wait for magic to happen** ✨
   - It will download AI models (this takes a few minutes)
   - Install everything needed
   - Build the web interface
   - Create easy startup shortcuts

### Step 4: Done! 🎉
The setup will automatically open your web browser to the chat interface.

## 🚀 How to Use Daily

### Starting the App
**Option 1 (Easiest):**
- **Windows**: Double-click `start.bat` 
- **Mac/Linux**: Double-click `start.sh`

**Option 2:**
- Open Command Prompt/Terminal in the project folder
- Type: `python launcher.py`

### Using the Chat Interface

1. **Access the app**: It opens at http://localhost:8000
2. **Start chatting**: Type in the message box at the bottom
3. **Switch AI models**: Use the dropdown menu to try different AI personalities
4. **View history**: All your conversations are saved on the left sidebar
5. **New conversation**: Click "New Chat" to start fresh

### Available AI Models
- **Llama 3.2 3B** - Fast, good for general chat
- **Dolphin Llama 8B** - Better reasoning, slower but smarter
- **Code Llama** - Great for programming questions
- **Gemma 2B** - Lightweight and quick
- And more! (You can add others)

## 🔧 Daily Operation

### Starting Up
1. Make sure your computer is on
2. Double-click the startup script (`start.bat` or `start.sh`)
3. Wait about 10-15 seconds
4. Your browser opens automatically to the chat

### Stopping the App
- Close the browser tab
- In the black terminal window, press `Ctrl+C`
- Or just close the terminal window

### If Something Goes Wrong
1. **Run the checker**: Double-click `verify.py` to see what's wrong
2. **Common fixes**:
   - **"Ollama not running"**: Look for Ollama in your system tray and start it
   - **"Browser doesn't open"**: Manually go to http://localhost:8000
   - **"Setup failed"**: Run `setup.py` again

## 💡 Tips for Best Experience

### Getting Better Responses
- **Be specific**: Instead of "help me code", say "help me write a Python function to sort a list"
- **Provide context**: Give the AI background information about what you're trying to do
- **Ask follow-ups**: You can continue the conversation - the AI remembers what you talked about

### Managing Conversations
- **Organize by topic**: Start new conversations for different subjects
- **Name your chats**: Click on conversation titles to rename them
- **Delete old chats**: Right-click to remove conversations you don't need

### Performance Tips
- **Close other programs**: AI uses computer resources, so close unnecessary apps
- **Use smaller models**: If it's slow, try Gemma 2B or Llama 3.2 1B
- **Restart occasionally**: If it gets slow, restart the app

## 🆘 Troubleshooting

### "The app won't start"
1. Make sure you completed the one-time setup
2. Check that Ollama is running (look in system tray)
3. Try running `verify.py` to check what's missing

### "AI responses are slow"
- This is normal! AI thinking takes time
- Try a smaller model like Gemma 2B
- Close other programs to free up computer resources

### "I can't access the website"
- Make sure the app is running (black terminal window should be open)
- Try going to http://localhost:8000 manually
- Check if another program is using port 8000

### "Models aren't downloading"
1. Make sure you have internet connection
2. Check that Ollama is installed and running
3. Manually run: `ollama pull llama3.2:3b`

### "Everything is broken"
**Nuclear option** - Start fresh:
1. Delete the project folder
2. Download it again
3. Run setup again

## 🎉 Enjoy Your Private AI!

You now have your own private AI assistant that:
- Runs entirely on your computer
- Doesn't send your data anywhere
- Works even without internet
- Remembers your conversations
- Can help with writing, coding, analysis, and general questions

**Have fun chatting!** 🤖💬

---

*Need help? Ask your developer friend who set this up, or run `verify.py` to check what might be wrong.*
