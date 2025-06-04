# 🚀 Quick Start Guide - Werewolf Discord Bot

Get your AI Werewolf game running in under 5 minutes!

## ⚡ Super Quick Setup

### Step 1: Get Your Keys
You need two things:
1. **Discord Bot Token** - [Get it here](https://discord.com/developers/applications)
2. **OpenRouter API Key** - [Get it here](https://openrouter.ai/keys)

### Step 2: Install & Configure

```bash
# Clone and install
git clone <your-repo>
cd werewolf-discord-bot
pip install -r requirements.txt
```

### Step 3: Set your keys

```bash
export DISCORD_TOKEN="your_discord_bot_token_here"
export OPENAI_API_KEY="your_openai_key_here"
```


### Step 3: Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" → Give it a name
3. Go to "Bot" tab → "Add Bot" → Copy the token
4. Enable "Message Content Intent" under "Privileged Gateway Intents"
5. Go to "OAuth2" → "URL Generator":
   - Scopes: ✅ `bot`
   - Permissions: 
      - ✅ `Send Messages` 
      - ✅ `Read Message History` 
      - ✅ `Manage Messages`
6. Use the generated URL to invite bot to your server

### Step 4: Run It!

```bash
python -m bot.bot
```

### Step 5: Play!

In Discord: `!play`

## 🎮 First Game Walkthrough

1. **Type `!play`** - Bot starts a new game
2. **Watch the Setup** - Bot assigns roles to 5 AI players
3. **Night Phase** - AI players secretly perform actions
4. **Day Phase** - Watch AI players discuss (3 rounds of conversation)
5. **Voting** - AI players vote to eliminate suspected werewolves
6. **Results** - See who won and why!

## 🛠️ Essential Commands

```
!play       # Start a new game
!rules      # Show detailed rules  
!clear 10   # Clear last 10 messages
!help       # Show all commands
```

## ⚠️ Quick Troubleshooting

**"Bot not responding"**
- Check your Discord token is correct
- Make sure bot has permissions in the channel
- Verify "Message Content Intent" is enabled

**"OpenAI API Error"**
- Check your API key is valid
- Verify you have API credits/quota
- Try changing `DEFAULT_MODEL` in `common/config.py`

**"Import Error"**
- Run: `pip install -r requirements.txt`

## 🎯 What You'll See

A typical game looks like this:

```
🎮 Game Starting!
✅ Roles have been assigned!

🌙 Night Phase
Everyone close your eyes...
☀️ Dawn breaks! Everyone wake up!

💬 Day Phase - Discussion Time!
📢 Discussion Round 1/3

AI_P3: Let’s get things started: I didn’t see any reason to shake things up last night, so I chose not to interfere with anyone’s roles...
AI_P5: Interesting that AI_P3 claims to have done nothing—if you’re the Troublemaker, that means you left roles untouched, ...
AI_P1: I was a Villager last night, so I didn’t have any night action to perform. It’s interesting that both AI_P3 and AI_P5 are claiming they didn’t do anything either...
AI_P2: Noticing that we have two Villager claims already, I’m curious if we’ll hear from anyone claiming Seer or Robber...
AI_P5: So far we have two Villager claims (from AI_P1 and AI_P5), and AI_P3 has claimed Troublemaker but said no swap was made. AI_P2 has pointed out that neither Seer nor Robber has come forward yet, which is odd—...

🗳️ Voting Phase
Time to vote for who you think is a Werewolf!
⚖️ It's a tie!
AI_P1: 1 vote(s)
AI_P2: 2 vote(s)
AI_P3: 0 vote(s)
AI_P4: 0 vote(s)
AI_P5: 2 vote(s)
Tied players: AI_P2, AI_P5

Additional voting round required!
🏁 Final Results
AI_P1 (Started as: Villager, Ended as: Villager): 0 vote(s)
AI_P2 (Started as: Werewolf, Ended as: Werewolf): 5 vote(s)
AI_P3 (Started as: Troublemaker, Ended as: Troublemaker): 0 vote(s)
AI_P4 (Started as: Villager, Ended as: Villager): 0 vote(s)
AI_P5 (Started as: Villager, Ended as: Villager): 0 vote(s)

🏆 Village Team Wins! 🎉
🎮 Game Over!
Thanks for playing!
```