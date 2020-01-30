from psiturk.amt_services_wrapper import MTurkServicesWrapper

class PsiturkServicesManager():
    _cached_amt_services_wrapper = None
    
    @property 
    def amt_services_wrapper(self):
        if not self._cached_amt_services_wrapper:
            self._cached_amt_services_wrapper = MTurkServicesWrapper()
        return self._cached_amt_services_wrapper
        
    @property
    def config(self):
        return self.amt_services_wrapper.config
    
    @property
    def mode(self):
        return self.amt_services_wrapper.get_mode().data
    
    @property
    def codeversion(self):
        return self.config['Task Parameters']['experiment_code_version']
        
    @property
    def amt_balance(self):
        return self.amt_services_wrapper.amt_balance().data
        
psiturk_services_manager = PsiturkServicesManager()