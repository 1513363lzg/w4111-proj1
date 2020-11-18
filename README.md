# w4111-proj1
web-applicaiton-NY-rental-price

PostgreSQL account: sy2890

URL of our web application:http://localhost:4111/

Description of what we implemented: We basically implmented everything we descriped in our original proposal. We showed the buildings basic attributes in the index page, and detailed information including apartments, surroundings, prospect managers and tweet comments in hyperlinks to other routes.

Page description:
1. index page: we showed the building basic attributes in this page and built hyperlinks to the detailed information of each building. Basic attributes include buildings` zipcode, address, built-year and name e.t.c.. Besides, we implemented a search function so that the user can search a certain building by name or addresss.
2. '/\<name>/\<address>/\<zipcode>' page: we showed the detailed information for each building. The route is defined by the name of the building and its primary key (address,zipcode). We wrote several SQL queries inside this detailed information page trying to show and summarize every important aspect of each building, which includes what team manages such building and what kind of tweets comment on this building and how about surrounding facilities. This pages links enetities associated with buildings.
3. '/\<teamname>' page: we showed how about comment on a specific managment team. We distinguish between comment on buildings and comment on management team. On this page, based on different tweets, people have different attitudes from negative to neutral to positive toward management team. 
