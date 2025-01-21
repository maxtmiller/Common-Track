# CommonTrack

## 📚 **Introduction**  📚
**CommonTrack** was created to assist students applying to colleges by providing detailed, easy-to-understand information about each college on the Common App. Key details include ranking, size, type, deadlines, test policy, recommendations, and more.

---

## 🛠️ **Technology & Frameworks** 🛠️
- The backend is developed in **Python** using the **Flask framework**, chosen for its simplicity and ease of organizing routes for various functionalities.  
- Key libraries include:  
  - **CS50 SQL** for simplified database operations.  
  - **Werkzeug.security** to store passwords securely as hashes.  
  - **Functools** to create a wrapper ensuring users are redirected to the login page upon starting a session.  
- Integrated **Google Calendar API** to manage and sync college deadlines with a personalized calendar.  

---

## 🎨 **Features** 🎨
1. **Home Page**  
   - Explains the website’s purpose.  
   - Provides details on ranking criteria and abbreviation meanings.  

2. **My College List**  
   - Allows users to track up to 20 colleges.  
   - Displays critical information and enables users to add college deadlines to their calendars.  

3. **Search All Colleges**  
   - Contains a comprehensive list of colleges on the Common App.  
   - Users can search for colleges to retrieve essential details.  

4. **Ranked Colleges**  
   - Features a list of QS-ranked colleges.  
   - Includes detailed scores for criteria like sustainability, reputation, research, and international faculty.  

5. **About Section**  
   - Describes the website's purpose in detail.  
   - Shares the creator's motivation and inspiration for developing the app.  

---

## 🚀 **Motivation** 🚀
The idea for CommonTrack was inspired by personal challenges experienced while applying to colleges. By streamlining the process and offering an organized way to manage deadlines and critical information, the app aims to simplify and enhance the college application experience for students.  



CommonTrack was created to help students who are applying to colleges by providing lots of information about each college that is part of the common app in an easy to understand manner, such as ranking, size, type, deadlines, test policy, recommendations and more.

I decided to use a similar framework to the finance practice set, using python for the backend with the flask framework. This is because it was relatively simple to understand and I could use a similar login and register functionality. It was very useful that I could create a different route for each functionality, from creating an event on calendar to searching for a college in the list, as it helped keep the code organized and focused.

The program some of the same libraries from before, including the CS50 SQL library as it was much more convenient since the syntax was simpler and the werkzeug.security libary to store the passwords as hashes. I also used functools library to create a wrapper for executing code before the first request to ensure the user would be directed to the login page with the session being cleared. In this project, I used the google calendar API to enable the program to create a college deadlines calendar and read and write to it depending on the universities the user is interested in. This is because keeping college deadlines organized within a calendar is something that I would have liked to have myself, when applying to universities.

The website has five main content pages. The first being a home page where the purpose is explained, along with more explanations of what each ranking criteria meant and what the abbreviations used in the ranking section mean. The second is my college list page, where the user can add up to 20 colleges to track useful info about them as listed before and add these colleges deadlines to the user's calendar. The third is a page with a list of all colleges on common app and the user can search for any college to obtain some crucial info about the college. The fourth page is a list of all ranked colleges from QS Rankings which includes ranking info and the user can use the search functionality to see a breakdown of the scores for each college in many specific areas such as sustainability, reputatoin, research, and amount of international faculty. Finally, the fifth page is an about section where I talk about the uses of the website in more detail and my reason and motivation for creating it.
