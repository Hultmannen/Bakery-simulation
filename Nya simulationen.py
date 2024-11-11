import simpy
import random
import statistics

# Simulation parameters
SIM_TIME = 12 * 60  # Simulate 12 hours in minutes (8 AM to 8 PM)
NUM_WORKERS = 2     # Two workers
PATIENCE = 10       # Max patience in minutes
num_simulations = 10  # Number of simulations to average results

class BakeryQueueSystem:
    def __init__(self, env, service_rate):
        self.env = env
        self.worker = simpy.Resource(env, capacity=NUM_WORKERS)
        self.service_rate = service_rate
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
                service_time = random.expovariate(self.service_rate)
                yield self.env.timeout(service_time)
                wait_time = self.env.now - arrival_time
                self.wait_times.append(wait_time)
                self.served_customers += 1
                self.server_busy_time += service_time
            else:
                self.lost_customers += 1

def customer_generator(env, bakery, arrival_rate):
    customer_number = 0
    while True:
        yield env.timeout(random.expovariate(arrival_rate))
        customer_number += 1
        env.process(bakery.serve_customer(f'Customer {customer_number}'))

def run_simulation(arrival_rate, service_rate):
    env = simpy.Environment()
    bakery = BakeryQueueSystem(env, service_rate)
    env.process(customer_generator(env, bakery, arrival_rate))
    env.run(until=SIM_TIME)

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

# Test different arrival and service rates
arrival_rates = [1/3, 1/5, 1/7]  # Different arrival intervals (every 3, 5, and 7 minutes)
service_rates = [1/3, 1/4, 1/5]  # Different service times (average of 3, 4, and 5 minutes)

# Collect results for each scenario
for arrival_rate in arrival_rates:
    for service_rate in service_rates:
        print(f"Running simulations with arrival rate = {arrival_rate:.2f} and service rate = {service_rate:.2f}")
        scenario_results = [run_simulation(arrival_rate, service_rate) for _ in range(num_simulations)]

        # Calculate average across all simulations for this scenario
        avg_results = {
            'avg_wait_time': statistics.mean([r['avg_wait_time'] for r in scenario_results]),
            'served_customers': statistics.mean([r['served_customers'] for r in scenario_results]),
            'lost_customers': statistics.mean([r['lost_customers'] for r in scenario_results]),
            'customer_loss_rate': statistics.mean([r['customer_loss_rate'] for r in scenario_results]),
            'worker_utilization': statistics.mean([r['worker_utilization'] for r in scenario_results])
        }

        # Print the average results for the current scenario
        print(f"  Average Waiting Time: {avg_results['avg_wait_time']:.2f} minutes")
        print(f"  Average Customers Served: {avg_results['served_customers']:.2f}")
        print(f"  Average Customers Lost: {avg_results['lost_customers']:.2f}")
        print(f"  Average Customer Loss Rate: {avg_results['customer_loss_rate']:.2f}%")
        print(f"  Average Worker Utilization: {avg_results['worker_utilization']:.2f}%")
        print()
