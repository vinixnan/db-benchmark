from codecarbon import OfflineEmissionsTracker
import timeit
import json


class tracker():
    def __init__(self, framework_name, version, benchmark_name):
        self.tracker = None
        self.opened = False
        self.emissions_results = {}
        self.emissions_results['data'] = {}
        self.emissions_results['framework'] = framework_name
        self.emissions_results['version'] = version
        self.emissions_results['benchmark_file_name'] = benchmark_name
        self.filename = f"emissions_results_{framework_name}_{version}_{benchmark_name}.json"
        self.counter = 0
        self.question = None

    def default_timer(self):
        time = timeit.default_timer()
        self.counter += 1
        if not self.opened:
            self.tracker = OfflineEmissionsTracker(country_iso_code="BRA", save_to_file=False)
            self.opened = True
            self.tracker.start()
        else:
            emissions = self.tracker.stop()
            self.opened = False
            self.add_emissions(self.question, emissions)
        return time
    
    def save_emissions(self):
        print("Saving emissions results to file:", self.filename, "Counter:", self.counter)
        with open(self.filename, 'w') as f:
            json.dump(self.emissions_results, f, indent=4)
        
    def add_emissions(self, question, emissions):
        key = question
        if key in self.emissions_results['data']:
            suffix = 2
            key = f"{question}_{suffix}"
            while key in self.emissions_results['data']:
                suffix += 1
                key = f"{question}_{suffix}"
                
        self.emissions_results['data'][key] = emissions