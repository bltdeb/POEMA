# POEMA
#### Video Demo:  <URL HERE>
#### Description:
POEMA is a small web application built using Python and Flask for poetry lovers, seeking a convenient way to discover and collect their favorite verses. Users can easily search for poems by various criteria and save them in their personal accounts. A unique feature generates a random poem on each page refresh.

#### base.html: 
This base Jinja template defines the common structure for all pages within the web application, including elements like the logo, navigation bar, sidebar, and globally accessible buttons. It also implements an if-else condition to dynamically control the display of logout, favorites (faves), and change password buttons in the sidebar. These buttons are only visible when a valid session ID exists, indicating a logged-in user; otherwise, login and registration buttons are displayed.

#### change_password.html:
This file contains the design of the change password form which has several elements such as current password, new password and confirm new password. The change password form's action attribute is set to a URL that corresponds to a route defined in the Flask application. The form uses the POST method to send the updated password data to this route for processing.

#### faves.html:
The faves page displays the user's saved poems. A Flask route queries the user's database to retrieve this data, which is then rendered on the page, with pagination ensuring a clean and manageable view by showing only one poem per page. Users can favorite or unfavorite poems directly within their display containers using a toggle button. This button, powered by a JavaScript event listener, interacts with two Flask routes: one adds the poem to the user's saved poems in the database, while the other removes it.


#### index.html:
Upon successful authentication, users are greeted by the index page, which serves as the central hub for navigating and interacting with the POEMA application. This page offers several key features. A prominent search bar allows users to discover specific poems by querying the external PoetryDB API. This query is facilitated through a dedicated Flask route, ensuring seamless communication with the API. Below the search bar, a dedicated container dynamically displays a randomly selected poem. This random poem is also fetched from the PoetryDB API, but through a separate Flask route that generates a new selection each time the page is loaded, providing a fresh experience for every visit. Within each displayed poem's container, a user-friendly favorite button is implemented. This button, powered by a JavaScript event listener, provides a simple toggle function. Clicking the button triggers a request to one of two distinct Flask routes. One route handles the action of saving (favoriting) the currently displayed poem to the user's personal database table, while the other route manages the removal (unfavoriting) of the poem from the same table. This system allows users to easily curate their own collections of favorite poems.

#### login.html:
This file defines the layout and functionality of the login form, which includes input fields for the user's username and password. Upon submission, the form data is sent via a POST request to a designated Flask route responsible for user authentication. A "Register here" link is also provided for users who need to create an account.

#### register.html:
This file defines the layout and functionality of the registration form, which includes input fields for username, password and confirm password. Upon submission, the form data is sent via a POST request to a designated Flask route that is responsible for user registration. 

#### search_results.html:
The search results page displays poems retrieved based on the user's search input. If the search yields no results, an error message is displayed. To manage the display of results, pagination is implemented to show one poem per page. The page also includes a favorite toggle button. A JavaScript event listener on this button manages the interaction with two Flask routes. One route persists the poem in the user's database, while the other removes the poem from user's database.

#### config.py:
This file contains the configration variables and the most important thing, the secret key to secure sessions. This file is added to the git ignore file to avoid adding it to version control

#### poema.db:
This file is the sqlite database file which contains all the user information tables such as users, favorites etc.

#### app.py:
This is the python file that handles the backend for the POEMA web app. The first 50 lines are configuring flask to use the sqlite databse. The file contains the following routes:
1. random poetry route - makes a request to the endpoint https://poetrydb.org/random/1 and stores the results in JSON format. To ensure only short poems are displayed on the index page, I implemented an if-else condition that filters out poems with more than 10 lines. In case of a failed request or any other error, an error message is shown to the user.

2. search route - this route makes a request to the endpoint https://poetrydb.org/random/1 and is linked to the /search action in the index.html file. To allow users to search by either author or poem title, I implemented an if-else condition that first attempts to search by author. If no results are found, the search is then performed by poem title. Additionally, I incorporated pagination to display one poem per page. Error handling is also in place to manage situations where no search query is provided or if fetching poetry fails.

3. login route - the login route is linked to the /login action in the login.html file and handles a POST request to the database, where it checks the user's credentials (username and password). Using an if-else condition, it verifies if the provided username matches a record in the database and if the entered password matches the hashed password stored for that user. If either of these checks fails, an error is returned.

4. register route - the registration route is linked to the /register action in the registration.html file. First ensures that the form is not submitted empty. Upon receiving a POST request, it checks if the provided username already exists in the database. If the username is not found, a new hashed password is generated, and the username is then inserted into the database. Once the user is successfully registered, the user_id is stored in the session, indicating a successful login, and the user is redirected to the index page.

5. logout route - the logout route is triggered by the /logout action in the base.html file. This route clears the user_id from the session, effectively logging the user out.

6. change password route - the change password route is linked to the /change_password action in the change_password.html file. Upon receiving a POST request, it first validates that the form is not empty and that the new password matches the confirmation password. Next, it checks the user’s credentials in the database, ensuring the current password is correct. If all conditions are met, a new hashed password is generated and replacing the old one in user's database. Finally, the user is logged out to complete the process.

7. save poem route - the save poem route is triggered by the JavaScript event listener linked to /save-poem. It checks whether the poem is already saved in the user's database. If the poem isn't saved yet, it will be inserted in the user's database. If the poem is already saved, an error will be returned.

8. unsave poem route - the unsave poem route is triggered by the Javascript event listener linked to /unsave-poem. It first extracts data from the resuest (title and user_id) and removes the poem from user's database. 

9. get saved poems route - the get saved poems route is specifically designed for the favorites page. It first counts the number of poems saved in the user's database, then queries the database to retrieve these poems, ensuring they are displayed on the favorites page.

