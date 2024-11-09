# Service Booking Platform

## Project Overview

This project is a web-based service booking platform that allows users to book various services like plumbing, painting, and more. Users can sign up, log in, view available services, and make bookings with options to select preferred dates and times. Additionally, users can view booking confirmations and cancel bookings using a booking ID. The application is built with HTML, CSS, and Python for backend functionality.

## Webpages and Functions

1. **signup.html**  
   - The page where a new user can sign up for an account.

2. **login.html**  
   - The page where an existing user can log in to the system.

3. **home.html**  
   - The home page, which provides an overview of all available service types, including options like plumbing, painting, etc.

4. **stores_db.html**  
   - This page displays stores for each service. Users can filter stores by postal code to find services in their preferred area.

5. **store_services.html**  
   - Displays the list of services offered by a selected store, including the prices for each service.

6. **booking1.html**  
   - The booking page where users can select and book a service, specifying the desired date and time.

7. **booking_confirm.html**  
   - Displays a confirmation of the booking along with a unique booking ID for reference.

8. **cancel_book.html**  
   - Allows users to cancel a booking by entering the booking ID associated with the service.

## Additional Files

1. **styles.css**  
   - Contains all the CSS styling for the project to ensure a consistent and user-friendly design.

2. **secret.py**  
   - Handles secret configurations and sensitive information required for secure operation.

3. **server.py**  
   - The main server-side file that controls the backend logic and processes requests for various pages.

## How to Run the Project

1. Download the code and unzip the folder.
2. Navigate to the project folder in your terminal.
3. Run the following command to start the server:
   ```bash
   python3 server.py
   ```
4. Open a web browser and go to `http://localhost:5000` to access the application.

This will set up the project on your local machine, allowing you to explore the functionalities of the booking platform.

## Collaborators
1. Mihika Sanghvi - mrs2356
2. Anushka Agarwal - aa5477
