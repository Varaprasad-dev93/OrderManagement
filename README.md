# Order Management System

This is a simple backend system that simulates order handling with:

- Time-based restrictions (only allow orders between 10AM–1PM)
- Rate limiting (only 100 orders per second)
- Queuing extra orders
- Support for MODIFY and CANCEL
- Response handling and latency calculation

## How to Run

- Make sure Python 3 is installed
- Run `python main.py`
- Orders and responses will print to console
- Responses get saved in `order_responses.log`

## Assumptions

- Orders use timestamp when created
- Rate limit is applied every second
- Latency = response time – sent time
