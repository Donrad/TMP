# TMP-Public
 News collection system

 This program collects news for you, I had it sending me cryptocurrency and precious metals related news as well as prices for certain financial instruments on my watchlist every morning.

 There is still room for optimisation in this program. I would suggest separating the html for the emailinto modules and import them to keep the whole script more tidy.

 - You'll need to edit the categories.txt file to contain categories of news you'd like to receive.

 - Set the username and password variables on lines 25 & 26 of pymail.py to either a string of your username and password or set two environment variables in your pc named "EMAIL_PASS" and "EMAIL_USER". Of course make these have a value of your email and password.

 - Depending on the aforementioned variables, you will need to change the smtp server & port. It is currently set to use Microsoft emails. Gmail will not work as it is. 

 - Then, edit the email.txt file so that it contains your email. If you wish to add more recipients - add their emails on each line below; in corresponding order with the contacts variable in pymail. Also add a file in the symbols folder, with the file being named "*recipient*-sym.txt"

 - Depending on the operating system and server you are running this on, all file paths in pymail.py may need to be changed.

 - This will send you the prices for four metals and four stocks. To change this, simply change the symbol in the You-sym.txt file. It is likely you will need to change the web scraping elements within this script to accomodate new symbols if they are not found on Yahoo finance. 

 - The metal prices are set at UK bullion prices, you may wish to set this to a price on a specific exchange in which case the web scraping function will need to be modified. 

- To include crypto prices, a new function will need to be made. Use the metal or stock price scraping function as a starting template and this will be very easy to do.

