# Soney
Honeytrap for social media applications<br>
A social media threat detection system leveraging honeypot techniques and user behavior analysis to identify malicious activities. It features user chat analysis, post monitoring, and automated threat detection with a honeytrap system to lure attackers. Real-time monitoring of interactions identifies suspicious behaviors, focusing on protecting users from social engineering, fraud, and bots. This proactive system ensures enhanced security through automated threat mitigation.

# Chat application

## Installations
terminal -1: cd backend && source ./bin/activate && pip install -r requirements.txt <br>
terminal -2: cd frontend && npm install dependencies<br>
terminal -3: cd honeytrap && npm install dependencies<br>
## Run
terminal -1: cd backend  && python -m uvicorn main:app --reload<br>
terminal -2: cd frontend && npm start<br>
terminal -3: cd honeytrap &&  npm start<br>


### phase-1:Social media application<br>
Implementation:<br>
1. Signup<br>
2. Login<br>
3. Logout<br>
4. Profile<br>
5. Friend requests<br>
5. Posts<br>
6. Comments<br>
7. Like and Dislike<br>
7. One-to-one chat with friends<br>

#### phase-2:Honeytrap backend<br>
Implementation:<br>
1. Automated account creation<br>
2. Automated post creation<br>
3. Automated interaction with other Honeytrap accounts<br>
4. Log interactions with Honeytrap accounts<br>
5. Integration with Grooq for ai for realistic data<br>

### phase-3:Detection System<br>
Implementation:<br>
1. Analysis of interaction with Honeytrap Accounts<br>
2. Time based interaction detector<br>
3. Spammy content detector<br>
4. Integration with Grooq for ai for sementic analysis of comments<br>

### phase-4:Honeytrap Page<br>
Implementation:<br>
1. Dashboard: Monitor activity<br>
2. Create: creation of honeytraps with purpose<br>
3. Logs: Logs of all honeytrap activities<br>
4. Detected: List of all detected potential spam,frauds and bots with reason<br>
