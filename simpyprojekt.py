import simpy
import random
import statistics

# Simulation parameters
SIM_TIME = 12 * 60  # Simulate 12 hours in minutes (8 AM to 8 PM)
NUM_WORKERS = 2     # Two workers
ARRIVAL_RATE = 1/5  # Average arrival every 5 minutes
SERVICE_RATE = 1/4  # Average service time of 4 minutes
PATIENCE = 10       # Max patience in minutes

class BakeryQueueSystem:
    def __init__(self, env):
        self.env = env
        self.worker = simpy.Resource(env, capacity=NUM_WORKERS)
        self.wait_times = []
        self.server_busy_time = 0
        self.served_customers = 0
        self.lost_customers = 0

    def serve_customer(self, customer_name):
        arrival_time = self.env.now
        with self.worker.request() as request:
            patience = random.uniform(1, PATIENCE)
            results = yield request | self.env.timeout(patience)
            if request in results:
                service_time = random.expovariate(SERVICE_RATE)
                yield self.env.timeout(service_time)
                wait_time = self.env.now - arrival_time
                self.wait_times.append(wait_time)
                self.served_customers += 1
                self.server_busy_time += service_time
            else:
                self.lost_customers += 1

def customer_generator(env, bakery):
    customer_number = 0
    while True:
        yield env.timeout(random.expovariate(ARRIVAL_RATE))
        customer_number += 1
        env.process(bakery.serve_customer(f'Customer {customer_number}'))

def run_simulation():
    env = simpy.Environment()
    bakery = BakeryQueueSystem(env)
    env.process(customer_generator(env, bakery))
    env.run(until=SIM_TIME)

    # Calculate average waiting time and other results
    avg_wait_time = statistics.mean(bakery.wait_times) if bakery.wait_times else 0
    total_customers = bakery.served_customers + bakery.lost_customers
    customer_loss_rate = (bakery.lost_customers / total_customers) * 100 if total_customers > 0 else 0
    worker_utilization = (bakery.server_busy_time / (SIM_TIME * NUM_WORKERS)) * 100 if SIM_TIME > 0 else 0

    return {
        'avg_wait_time': avg_wait_time,
        'served_customers': bakery.served_customers,
        'lost_customers': bakery.lost_customers,
        'customer_loss_rate': customer_loss_rate,
        'worker_utilization': worker_utilization
    }

# Run the simulation multiple times to get average results
num_simulations = 10  # Run 10 times to gather average data
results = [run_simulation() for _ in range(num_simulations)]

# Print results from each round
for i, result in enumerate(results):
    print(f"Simulation {i + 1}:")
    print(f"  Waiting Time: {result['avg_wait_time']:.2f} minutes")
    print(f"  Customers Served: {result['served_customers']}")
    print(f"  Customers Lost: {result['lost_customers']}")
    print(f"  Customer Loss Rate: {result['customer_loss_rate']:.2f}%")
    print(f"  Worker Utilization: {result['worker_utilization']:.2f}%")
    print()

# Calculate average across all simulations
avg_results = {
    'avg_wait_time': statistics.mean([r['avg_wait_time'] for r in results]),
    'served_customers': statistics.mean([r['served_customers'] for r in results]),
    'lost_customers': statistics.mean([r['lost_customers'] for r in results]),
    'customer_loss_rate': statistics.mean([r['customer_loss_rate'] for r in results]),
    'worker_utilization': statistics.mean([r['worker_utilization'] for r in results])
}

# Print the average results
print(f"Average Results across {num_simulations} simulations:")
print(f"  Average Waiting Time: {avg_results['avg_wait_time']:.2f} minutes")
print(f"  Average Customers Served: {avg_results['served_customers']:.2f}")
print(f"  Average Customers Lost: {avg_results['lost_customers']:.2f}")
print(f"  Average Customer Loss Rate: {avg_results['customer_loss_rate']:.2f}%")
print(f"  Average Worker Utilization: {avg_results['worker_utilization']:.2f}%")
