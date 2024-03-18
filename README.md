# Amazon Price Checker

### What is is?

This simple tool, allows you to keep track of the price of an item on Amazon and will notify you if the price drops below a certain threshold.

---

*Versions are subject to change*

#### Version 1
- [X] Have a simple python cli tool that takes in an Amazon URL
- [X] Use BeautifulSoup to scrape the price and title of the item
- [X] Output the price and title of the item

#### Version 2

- ~~Change to use classes~~
- [X] The tool will take in a new input "price", which checks if current item price <= "price"
- [ ] The tool will send an email to the user if the price is less than the set price
- [ ] Run on a cron to constantly get updated price

#### Version 3
- [ ] Implement threads to check multiple items at once
- [ ] Implement a database to store price data
- [ ] Ability to generate graphs of price over time

#### Version 4
- [ ] New data is pushed to API endpoint
- [ ] Implement docker container

#### Version 5
- [ ] Store data in a database
- [ ] Create a simple backend for website
- [ ] Create a simple frontend for website

#### Version 6
- [ ] Set up user accounts
- [ ] User can add items to a price watchlist through web interface
- [ ] User can set a price for each item

#### Version 7
- [ ] Improve the frontend
