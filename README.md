# rt-bot-34
Simple hubstaff activity report.

Retrieve information from hubstaff V1 API about time worked on projects by employees of the test organization you are in and present it in a html table.

In columns there should be employees, in rows there should be projects and in the cells in the middle there should be time that a given employee spent working on the given project. Only the projects and employees which worked on a given day should be presented. The table is rendered for one day which by default is yesterday. Output should be saved to a file, configuration (such as the API key) should be read from a config file. Future extension may be to email the table to a manager.

It should be possible to deploy the program on a server without reading its code or running any api queries manually.
