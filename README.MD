# Capstone 1 for Springboard
---------------------------------------

This app allows users to explore a small part of the LOTR universe. Features include interacting with characters and quotes by liking and commenting on them. Liked quotes and characters are shown on users profile page. Non users may also use the app, but are barred from liking and commenting.


## Tech used:
- The API I used is https://the-one-api.dev/. 
- I used flask to make page routes for movies, characters, quotes, and users.
- I pulled the Ring trilogy since the API does not allow me access to movie specific quotes from the Hobbit series. 
- I pulled movie specific quotes from the API with python requests, then added the quote and subsequent character that said it to PSQL tables using SQLAlchemy. I also used (UPDATE THIS)
The create user, login user, and edit user info forms were created using WTForms. Bcrypt was used to hash passwords. 
- I used Javascript and JQuery for click handlers. Quotes in list form would redirect to quote specific page through clicking its body. Same for characters. Liking and disliking were done using JS so the page wouldn't refresh everytime. JS was also used to append 10 random quotes from the database to the frontpage with a button.
- I used Jinja to loop and if conditional Instrumented List data I pulled from the database with SQLAchemy to display or hide data on html.
Finally, I used Twitter Bootstrap and CSS to make the webpage look as presentable as I could manage.


## Challenges I faced:
- I did not want to pull one thousand characters into the database just for them not to have a quote associated, so I came up with the idea to only get characters from API that had the character_id associated with a quote.
- API fails to respond and returns null (I'm still not quite sure what it returns), but I haven't had an issue after I put a conditional that checks if the response is null and to skip that iteration if it is.
- Requesting from API then adding to database through a loop takes a while. Added a loader to relay to the user that it is loading but I'm fairly certain my way isn't efficient at all.
- Since creating new html markup with JQuery does not inheret click handlers despite the markup having the same classes and ids, I had to use event delegation to one, avoid the like/comment buttons and the character link inside the quote blockqquote to also be links to the quote page, and two, have the like/unlike buttons to still be like/unlike buttons after swap. 
- Could not figure out how to add like/unlike/comment buttons to the random quotes on homepage due to the fact I wanted two columns. The two column setup is made using a parent div to jinja, and I found I cannot dynamically create jinja since its a preload functionality. I'm sure theres a way I just do not know how.
- I like the background but it makes the white text, which I think is the most contrasting, a bit illegible sometimes. Unsure how to fix other than making boxes underneath text, which might be more ugly.


## How to use (Users):
Click the "Get random quotes!" button to see 20 new random quotes. Use the navbar to navigate various pages. Create a user to be able to log in, favorite, and comment on your favorite quotes and characters. Clicking most elements will redirect you to associated pages.

## How to use (Developers):
Create an account at https://the-one-api.dev/ to be assigned a bearer token. Create an .env file and enter TOKEN = yourtokenhere. Requests should be sent out and database should be filled on load, so long as the app detects anything is empty.

## Conclusion:
Despite the API's limitation I did my best to make a functioning app. Hope you enjoy.