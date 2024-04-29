# GoSpice E-Commerce Website
#### Video Demo:  <https://youtu.be/mQIDX-hoCZs>
#### Description:

### Register Page
When a user wants to create an account you click on the register link in the navigation section. You are required to enter a username that must be your email address, and it must be a valid email address in the correct format. An error is displayed if the email address is not of valid form. If the email address/username is already in the users table, it will display a message that the user already exists, and you will be redirected to the login page.

The password and confirm password are also required and will display an error message if any of the two are missing. The server will check that the password and the confirmation password are identical, if not it will display an error message that the two do not match.

The server will create a new user with a default account type of 0 (Client). To change the account to an administrator account (1) you need to do it manually in the database.

Upon successful registration, the user will be redirected to the login page.

### Login Page
A user can log in by clicking on the **Log In** link in the navigation section. When a user login all the session data is clear, user data as well as the user's cart. When submitting the login form the server checks for an empty field that is required and gives an appropriate error message accordingly.

The server checks that the user is registered by the username being present in the users table, and if the username is present, it runs a check_password_hash on the corresponding user's password and compares it with the password the user supplied in the login form. If any of the credentials are missing an error message is displayed.

Once successfully authenticated the server will create the following session data:
- **user_id:** To keep track of which user is in the current session
- **account:** To keep track of what type of user is in session (Administration=1 / Client=0)
- **cart:** to create the cart for the active user

Upon successful login, the user is redirected to the home page/index page.

### Log Out Page
When a user logs out by clicking on the **Log Out** link in the navigation section, all the session data is cleared and the user is redirected to the home page/index page.

## Customer Side
### Home page/index page
The index page lists all the products available for purchase, items that are out of stock are displayed by changing the "Add to Cart" button with an unclickable button that displays "SOLD OUT". An item will display SOLD OUT if the quantity on hand is 0 in the database, or the difference between the number of ordered items in the cart and the quantity on hand is less than zero.

 If a customer wants to add any product to their cart without being logged in, they will be redirected to the login page.

On loading the home page/index page, if a cart does exist in the session it will compare the quantity of that product to the quantity in the database by subtracting the quantity in the cart from the quantity on hand in the database and adding it to the quantity left  in the items list. If the product is not in the cart the quantity left in the items list will be the value of the quantity on hand from the database.

When a user clicks on the **Add to Cart** button the add_to_cart function is called, and that item is added to the **session["cart"]** list in the session, by submitting the id of the specific product with a default quantity of 1. By adding the same product to your cart the quantity will increase accordingly.

### Profile page
When visiting the profile page by clicking on the **Profile** link in the navigation section, the server checks if the user exists in the client_info table. If the user does not exist in the client_info table, they have not yet entered their personal information and delivery address, and they will be redirected to the Update Profile page to complete their profile.

The profile information is displayed in grid format using 3 columns.
  1.  The first column shows the **Personal details**: Name, Phone number, username, and a button that allows the user to update their personal details as well as their delivery address.
  2.  The second column displays the user's **delivery address**.
  3.  The third column allows the user to **change their current password**.

#### Changing your password
When changing your password, all the fields are required. The server compares the old password ran through a check_password_hash function against the old password the user entered, if the incorrect old password was supplied, an error message will be displayed. The new password and the confirm new password are also checked to see if they are identical, if not an error message will be displayed.

When all the fields pass their checks the new password is hashed and the user's login details are updated.

Upon successfully updating the password the user is redirected to their Profile page.

### Update Profile Page
The update profile page is accessed by redirection or by clicking the **Update Details** button on the profile page in the first column.

The known details for the user are preloaded into the corresponding input fields for easy editing if the user already exists in the client_info table, else they will be redirected to the update details page first. The user can update the following fields, but the username cannot be changed. The full name and phone number are required fields.

Fields that can be edited/added:
- Full Name
- Phone Number
- Building/Apartment/House Number
- Street Address
- City
- Province
- Postal Code

By clicking on the **Update Personal Details** button on the Update Profile page, if the user exists already in the client_info table the server will simply update the existing user's information. If the user does not exist in the client_info table a new entry will be created.

Upon successfully updating the user's personal details they will be redirected to their profile page.

### Cart page
The cart page can be accessed by clicking on the **Cart** link in the navigation section. All the items with their corresponding quantities are loaded from the cart in the session and displayed.

The server checks if there are any item quantities on your cart that exceed the quantity on hand of the appropriate products in the database. If any cart item quantities exceed the quantity on hand in the products table, that item will be removed from the cart, and the user will have to add the product again if there are any quantities available.

Each item total is calculated and displayed, as well as the overall order total is calculated and displayed.

All currency values are run through a formatting function to format the currency.

#### Remove an item from the cart
The user can remove an item from the cart by clicking the **"Remove from Cart"** button next to the product. The item is then removed from the cart in the session, and the user is redirected to the Cart page.

#### Placing an order
When the user is happy with the items they choose they can place their order by clicking on the **"Place Order"** button.

The server generates a unique order number by combining the date time and the weekday. Then the new Quantity on hand is calculated, and the products table is updated accordingly.

All the items in the session cart are then added to the orders table in the database, if the insert of the order fails, an error message is displayed. After the items are added to the database, the general order information is added to the user_orders database.

The default status of an order is "Received"

The cart is emptied, and a message is displayed that the order has been successfully placed.

### My Orders page
The My Orders page can be accessed by clicking on the **"My Orders"** link in the navigation section.

All the user's orders are displayed, showing the Order Number, the status of the order as well and the date the order was placed in descending order. The user can view each order in more detail by clicking on the applicable order number that is available as a link, the user is redirected to the "View Order" page.

### View Order page
The view order page is accessed by clicking on an order number on the "My Orders" page. This page displays the specific order details: the individual items ordered with their corresponding quantities, the item totals, as well as the overall order total.

## Admin / Business Side
### Product List
Product List can be accessed by clicking on the **"Product List"** link in the navigation section.

All the products that are  in the products table are displayed, and all the details about the product entry are displayed.

#### Delete a Product
The user can delete a product by clicking the corresponding **"Delete Product"** button, which calls the delete_product function passing the product id as a parameter to the function, which permanently deletes the applicable product from the products table in the database.

#### Edit a Product
The user can edit any product by clicking the corresponding **"Edit Product"** button, which redirects the user to the "update_product" page by passing the product id as a parameter to the server.

### Update Product page
The product details are preloaded into the correct input fields for easier editing. All fields are required to be entered except the "Add Product Image" field which will use the current photo of the product if the field is left empty, otherwise the picture will be replaced.

The products table is updated with the appropriate values, and the user is then redirected to the "Product List" page.

### Add New Product page
The Add New Product page can be accessed by clicking on the **"Add a new Product"** link in the navigation section.

All the fields are required. The server gets all the values of the input fields.

The server checks if the image file chosen is a valid image file, and that an actual file is selected. If not an error message will be displayed. The file name will be the name of the image that is uploaded. **The image will be saved on the server disk at "/static/product_images/"**

If all the fields are valid the new product will be added to the products table, and a message will be displayed, indicating that the product was added successfully.

### All Orders page
The All Orders page can be accessed by clicking on the link **"View Orders"** in the navigation section.

All the orders of all the clients that placed orders are displayed sorted by the date ordered in descending order. The page displays the order number, the status of the order, and the date of the order. The details of each order can be viewed by clicking on the order number which is available as a link, the user will then be redirected to the View Order page.

### View Order page
The view order page is accessed by clicking on an order number on the "All Orders" page. This page displays the specific order details: the individual items ordered with their corresponding quantities, the item totals, the overall order total, the shipping address as well as the ability to change the order's status.

The order status and the Shipping address are displayed below the order details in two grid format columns.

The order status is preloaded and selected accordingly on the page for easy viewing and editing.

#### To Change the Order Status
To change the status of an order select the appropriate status option, and click the **Update Order** button. The server will get the appropriate status selected and update the user_orders table accordingly. Then the user will be redirected to the All Orders page.

*The status will reflect on the client's orders side as well.*
