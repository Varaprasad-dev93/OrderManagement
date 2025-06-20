import OrderManagement
from datetime import time
from OrderManagement import Logon_Session, Logout_Session, OrderRequest, OrderManagement
def main():
    
    # Create a logon session for a user
    session = Logon_Session("user1", "password123") #here we can use any cryptographic method to store the password securely.
    # Create a logout session for the user
    logout_session = Logout_Session(session)
    
    oms= OrderManagement(start_time=time(10, 0), end_time=time(13, 0),rate_limit=100,login_session=session, logout_session=logout_session)
    
    #checking the prsent time is in the range of order management system or not.
    print("Checking if the order management system is available...")
    if not oms.in_time_range():
        print("Order management system is not available at this time.")
        return
    
    # Authenticating the user whether the user is valid or not.
    print("Authenticating user...")
    if session.authenticate():
        print(f"User {session.username} authenticated successfully.")
        
        # Create an order request we fe examples # for placing a new order and modifying an existing order.
        # if want we can use loop to place multiple orders.
        order_request = OrderRequest(
            order_id=1,
            symbol="Dell Computers",
            quantity=10,
            price=150000.0,
            order_type="buy",
            request_type="New"
        )
        response = oms.on_data_request(order_request)  # Process the order request
        # Print the response
        oms.on_data_response(response)
        
        # Modify an existing order
        order_request = OrderRequest(
            order_id=1,
            quantity=5,
            price=155000.0,
            request_type="Modify"
        )
        response = oms.on_data_request(order_request)  # Process the order request
        # Print the response
        oms.on_data_response(response)
        
        # Cancel an order
        order_request = OrderRequest(
            order_id=1,
            request_type="Cancel"
        )
        response = oms.on_data_request(order_request)  # Process the order request
        # Print the response
        oms.on_data_response(response)
        
        # Force logout if needed (e.g., after 1:00 PM)
        # if time(13, 0) < time.now().time() < time(14, 0):
        #     print("Forcing logout due to time constraints.")
        #     oms.logout_session.force_logout(session)
            
            
        # Logout the session
        if logout_session.logout():
            print("User logged out successfully.")
    else:
        print("Authentication failed.")

if __name__ == "__main__":
    main()