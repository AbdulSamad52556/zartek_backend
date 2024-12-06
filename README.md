# Ride Sharing App - Backend

### Installation Instructions

1. Clone the repository.
2. Create an Environment (env)
3. Install the dependencies.

     ## OR
   
### Alternative Installation

1. samad321/zartek_backend:latest - This is my docker image name. You can pull and connect with your DB.
2. For WebSocket functionality, you need to use Redis as well.
   
## Features

- **User Registration**

  - Role-based authentication using Simple JWT.
    
- **Ride Creation**

  - Users can view available drivers and select one of their choosing.
  - The Google Maps Autocomplete library is used for location suggestions.
  
- **Ride Status Updates**
  
  - Both the user and driver can cancel the ride.
  - Drivers can accept and complete the ride.
    
- **Real-time Features**
  
  - When a Ride is Accepted by driver, it will start fetching driver's location and will update in our database.
  - When a user selects a driver for booking, that particular driver will receive a real-time notification.

- **Testing**

  - There are 7 test cases for the endpoints and models.
  - After setting up the project, you can run the following command from the main project folder to run the tests:
     `python manage.py test api`

- **Deployment**

  - The application is deployed on an AWS instance using NGINX and Docker.

  
Ensure to run all migrations using the following command:
`python manage.py migrate`




