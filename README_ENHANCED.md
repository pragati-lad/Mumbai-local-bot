# 🚂 Mumbai Train Timetable Chatbot - Enhanced Version

A comprehensive chatbot for Mumbai local trains with **3 major features**:
1. Western Railway timetables (Virar ↔ Churchgate)
2. Harbour Line timetables (Panvel ↔ CSMT)
3. Railway rules (Concessions, Refunds, Luggage)

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run the Enhanced Chatbot

```bash
streamlit run app.py

```

The chatbot will start and show you a URL like:
```
Running on local URL:  http://127.0.0.1:7860
```

Open this URL in your web browser!

## 💬 What Can You Ask?

### 🚆 Train Timings

**Western Railway:**
- "Train from Virar to Churchgate"
- "Next train from Borivali to Dadar after 6 PM"
- "Show AC trains from Andheri to Bandra"

**Harbour Line:**
- "Train from Panvel to CSMT"
- "Harbour line from Vashi to Kurla"
- "Train from Belapur to Mumbai"

### 📋 Railway Rules

**Concessions:**
- "What are student concessions?"
- "Senior citizen discount"
- "Disabled person concession"

**Refunds:**
- "How to get ticket refund?"
- "Can I cancel my season ticket?"
- "Online ticket cancellation"

**Luggage:**
- "Luggage rules"
- "How much baggage can I carry?"
- "Excess luggage charges"

## 📍 Stations Covered

### Western Railway (29 stations)
Churchgate, Marine Lines, Charni Road, Grant Road, Mumbai Central, Dadar, Bandra, Andheri, Borivali, Virar, and more...

### Harbour Line (28 stations)
Mumbai CSMT, Dadar, Kurla, Mankhurd, Vashi, Belapur CBD, Panvel, and more...

## ✨ Features

✅ **Two Railway Lines** - Western & Harbour
✅ **Smart Query Understanding** - Natural language processing
✅ **Time-Based Filtering** - "after 6 PM" queries
✅ **Railway Rules Database** - Concessions, Refunds, Luggage
✅ **Beautiful Web Interface** - Easy to use
✅ **Works Offline** - No internet needed after setup

## 🔧 Technical Details

- **Python 3.8+** required
- **Gradio** for web interface
- Sample timetable data included
- Easy to extend with more data

## 📝 Adding More Data

To add more trains, edit the `train_chatbot_enhanced.py` file:
- Add to `WR_AC_TRAINS` for Western Railway
- Add to `HARBOUR_TRAINS` for Harbour Line
- Add to `RAILWAY_RULES` for new rules

## 🆕 What's New in Enhanced Version?

✨ **Harbour Line Support** - Complete Panvel to CSMT route
✨ **Railway Rules** - Concessions, Refunds, Luggage info
✨ **Dual Line Detection** - Automatically detects Western or Harbour
✨ **Enhanced Examples** - More query types supported

## 🐛 Troubleshooting

**Problem**: `ModuleNotFoundError: No module named 'gradio'`  
**Solution**: Run `pip install gradio`

**Problem**: Can't find trains  
**Solution**: Make sure you mention two station names clearly

## 📞 Need Help?

The chatbot will guide you if you just type "hello" or press submit with an empty query!

---

**Made with ❤️ for Mumbai Local Train Travelers**
