# English Vocabulary Test
#### Video Demo: https://www.youtube.com/watch?v=usCZ-bEzZck
#### Description:
My project is a web-based Flask application that provides vocabulary tests for the levels from A1 to C2 as well as a placement test.
It features an administrator panel for managing questions and users.
Users can register, log in, take tests, and review their results.
The application uses a SQLite database and Bootstrap for the front-end.

## Files in the Project
### app.py
Initializes the Flask app and defines routes for user authentication, test management, and administrator functionalities.

### helpers.py
Contains helper methods that are used throughout the application to enforce user authentication, check administrator privileges, and fetch questions from the database. Key functions include:
- **login_required**: A decorator to ensure that a user is logged in before accessing certain routes.
- **admin_required**: A decorator to ensure that only administrator users can access certain routes.
- **is_admin**: A helper function to check if the current user has administrator privileges.
- **get_questions**: Selects questions deterministically from the database based on the test type and number of questions required. For placement tests, it selects an equal number of questions from each level (A1 to C2) using a deterministic hash function for randomness.

### vocabulary.db
Database file with the following tables:
- **users**: Stores user information including username, hashed password, and role.
- **questions**: Stores the questions, options, correct answers, levels, and types.
- **results**: Stores the test results including user ID, number of correct answers, total questions, and test type.

### Templates:

#### addQ.html
Form for adding questions. Administrators can input the question text, options, correct answer, level, and type.

While adding questions, I realized it would be faster if the level and type fields were automatically populated with what you entered for the previous question. So I had to change those fields when I was adding a question with a different level or type.

#### addU.html
Form for adding users.
Administrators can input the username, password, and role.

#### admin.html
Administrator panel interface.
Provides links to manage questions and users.

#### changeQ.html
Form for changing a question.
Administrators can select a question to edit and update its details.
Filters and a simple search are available to narrow down questions by type and level.

At first, the form was not populating with the data of the selected question, but because it would have been very tedious to change a question otherwise, I implemented the populateFields function in JavaScript.

#### deleteQ.html
Form for deleting a question.
Administrators can select a question to delete.
Filters and a simple search are available to narrow down questions by type and level.

I copied the filter from changeQ with some minor changes.

#### editU.html
Form for editing users.
Administrators can update the role of a user.

#### index.html
Homepage of the application. This page provides an overview of the application and includes links to the administrator panel for administrators.

#### layout.html
Base layout template with a navigation bar, theme toggle button, and footer.

#### listQ.html
List of questions.
Displays all questions in the database.
Administrators can delete any question by clicking the delete button next to it.

When I first implemented listQ all questions also had an edit button. But I removed it as it would complicate the "/change_question" route. 

#### listU.html
List of users.
Administrators can edit, delete, or add users.

I was first going to have different links for editing, deleting, and adding users like questions. But after I implemented listU, I realized I could do it all from one place.

#### login.html
Login form.
Allows users to log in with their username and password.

#### register.html
Registration form.
Allows new users to register by providing a username, password, and password confirmation.

#### result.html
Individual test result. Displays the user's score and the correct answers for the test.

#### results.html
List of all test results.
Displays the user's test history.

#### test.html
Test interface.
Displays the questions and options for the selected test.

I first tried checkboxes but had a hard time getting only one selected for one question, then I switched to radio buttons. I wanted it to unselect when clicked while selected, so I implemented a simple toggleRadio function in JavaScript.

### Static:

#### styles.css
I wrote this because I wanted to place the flaticon icon button at the bottom.

#### approval.png
Favicon of the application.
Source: https://www.flaticon.com/free-icon/approval_1292849