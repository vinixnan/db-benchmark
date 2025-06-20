from codecarbon import OfflineEmissionsTracker
import timeit
import json


class tracker():
    def __init__(self, framework_name, version, benchmark_name, execution):
        self.tracker = None
        self.opened = False
        self.emissions_results = {}
        self.emissions_results['data'] = {}
        self.emissions_results['framework'] = framework_name
        self.emissions_results['version'] = version
        self.emissions_results['execution'] = execution
        self.emissions_results['benchmark_file_name'] = benchmark_name
        self.filename = f"emissions_results_{framework_name}_{version}_{benchmark_name}_{execution}.json"
        self.counter = 0
        self.question = None
        self.begin = None
        self.very_begin = timeit.default_timer()
        self.execution = execution

    def default_timer(self):
        time = timeit.default_timer()
        self.counter += 1
        if not self.opened:
            self.tracker = OfflineEmissionsTracker(country_iso_code="BRA", save_to_file=False)
            self.opened = True
            self.tracker.start()
            self.begin = time
        else:
            emissions = self.tracker.stop()
            self.opened = False
            total_time = time - self.begin
            self.begin = None
            self.add_emissions(self.question, emissions, total_time)
            
        return time
    
    def save_emissions(self):
        self.emissions_results['counter'] = self.counter
        self.emissions_results['total_time'] = timeit.default_timer() - self.very_begin
        print("Saving emissions results to file:", self.filename, "Counter:", self.counter)
        with open(self.filename, 'w') as f:
            json.dump(self.emissions_results, f, indent=4)
        
    def add_emissions(self, question, emissions, total_time):
        key = question
        if key in self.emissions_results['data']:
            suffix = 2
            key = f"{question}_{suffix}"
            while key in self.emissions_results['data']:
                suffix += 1
                key = f"{question}_{suffix}"
                
        self.emissions_results['data'][key] = {}
        self.emissions_results['data'][key]['emissions'] = emissions
        self.emissions_results['data'][key]['total_time'] = total_time