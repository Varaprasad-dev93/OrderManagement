import time
import threading
from datetime import datetime, timedelta
from collections import deque

class Logon_Session:
    def __init__(self,username, password):
        self.username = username
        self.password = password
        self.is_authenticated = False
        self.last_activity = datetime.now()
    
    #if want to use authentication system we can add a method to check credentials.
    # For now, we will assume that the credentials are valid.    
    def authenticate(self):
        if self.username and self.password:
            self.is_authenticated = True
            self.last_activity = datetime.now()
            return True
        return False


class Logout_Session:
    def __init__(self, session):
        self.session = session
        self.is_logged_out = False
    
    def logout(self):
        #Here we can implement the logic to log out the user by checking the username 
        #exists in the databse.
        #For now, we will just set the is_logged_out flag to True.
        if self.session.is_authenticated:
            self.is_logged_out = True
            self.session.is_authenticated = False
            return True
        return False
    def force_logout(self):
        # Force logout logic is used to work after the time before 10:00 AM and after 1:00pm.
        self.is_logged_out = True
        self.session.is_authenticated = False
        return True



class OrderRequest:
    def __init__(self, order_id, request_type, quantity=1, price=10, order_type ="buy", symbol:str = "Default Symbol"):
        self.order_id = order_id
        self.symbol = symbol 
        self.quantity = quantity
        self.price = price
        self.order_type = order_type # "buy" or "sell"
        self.request_type = request_type # "New" or "Modify" or "Cancel"
        # Timestamp to track when the order was created
        self.timestamp = datetime.now()


class Response:
    def __init__(self, order_id, status, message):
        self.order_id = order_id
        self.status = status 
        self.message = message



class OrderManagement:
    def __init__(self, start_time, end_time, rate_limit, login_session,logout_session):
        self.start_time = start_time
        self.end_time = end_time
        self.rate_limit = rate_limit
        self.order_queue = deque()
        self.lock = threading.Lock()
        self.sent_orders = {}
        self.login_session = login_session
        self.logout_session = logout_session
        self.start_throttle_thread()
        
    def in_time_range(self):
        now = datetime.now().time()
        return self.start_time <= now <= self.end_time
    
    # On requesting the order, we will check if the user is authenticated and if the request is within the time range.
    def on_data_request(self, order_request):
        if not self.login_session.is_authenticated:
            return Response(order_request.order_id, "Error", "User not authenticated")
        
        if not self.in_time_range():
            return Response(order_request.order_id, "Error", "Orders can only be placed between 10:00 AM and 1:00 PM")
        
        with self.lock:
            # checking all the possible conditions before adding the order to the queue.
            if len(self.order_queue) >= self.rate_limit:
                return Response(order_request.order_id, "Error", "Rate limit exceeded")
            
            if order_request.order_type not in ["buy", "sell"]:
                return Response(order_request.order_id, "Error", "Invalid order type")
            
            #maintaining the order queue and sent orders.
            if order_request.request_type == "Cancel":
                if order_request.order_id not in self.sent_orders:
                    return Response(order_request.order_id, "Error", "Order not found")
                
                for i, req in enumerate(self.order_queue):
                    if req.order_id == order_request.order_id:
                        del self.order_queue[i]
                        break
                # Remove the order from sent orders
                self.sent_orders.pop(order_request.order_id)
                return Response(order_request.order_id, "Success", " Order cancelled")
             
            elif order_request.request_type == "Modify":
                if order_request.order_id not in self.sent_orders:
                    return Response(order_request.order_id, "Error", "Order not found")
                
                # Here we can implement the logic to modify the order.
                for i, req in enumerate(self.order_queue):
                    if req.order_id == order_request.order_id:
                        self.order_queue[i].quantity = order_request.quantity
                        self.order_queue[i].price = order_request.price
                        break
                # For now, we will just return success.
                return Response(order_request.order_id, "Success", "modified")
            
            # If the request is a new order, we will add it to the queue.
            self.order_queue.append(order_request)
            self.sent_orders[order_request.order_id] = datetime.now()  # Store the time when the order was sent
            return Response(order_request.order_id, "Success", "added to queue")
        
    def on_data_response(self, response):
        if response.status == "Error":
            print(f"Response for {response.order_id}: {response.message}")
            return
        if response.order_id in self.sent_orders:
            sent_time = self.sent_orders[response.order_id]
            latency = (datetime.now() - sent_time).total_seconds()
            print(f"Order {response.order_id} {response.message} | Latency: {latency} sec")
            with open("order_responses.log", "a") as log_file:
                log_file.write(f"{datetime.now()} - Order {response.order_id} {response.status} - {response.message} | Latency: {latency} sec\n")
        else:
            print(f"Order {response.order_id} response received: {response.message}")
            with open("order_responses.log", "a") as log_file:
                log_file.write(f"{datetime.now()} - Order {response.order_id} {response.status} - {response.message}\n")

            
    def send_(self, order_request):
        # Simulate sending the order to the exchange
        print(f"Sending order: {order_request.order_id} - {order_request.symbol} - {order_request.quantity} @ {order_request.price} ({order_request.order_type})")
        response = Response(order_request.order_id, "Success", "Order sent successfully")
        self.on_data_response(response)
    
    
    # This method will send the orders in the order queue at the specified rate limit.     
    def start_throttle_thread(self):
        def throttle():
            while True:
                with self.lock:
                    for _ in range(self.rate_limit):
                        if self.order_queue:
                            order = self.order_queue.popleft()
                            self.send_(order)
                time.sleep(1)
        threading.Thread(target=throttle, daemon=True).start()
    
    def start_monitoring(self):
        def monitor():
            while True:
                if not self.login_session.is_authenticated:
                    print("User is not authenticated. Exiting monitoring thread.")
                    break
                if not self.in_time_range():
                    print("Outside of trading hours. Exiting monitoring thread.")
                    break
                time.sleep(5)
        threading.Thread(target=monitor, daemon=True).start()